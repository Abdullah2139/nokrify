import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.config import settings, DATA_DIR, RESUMES_DIR
from app.database import init_db, get_db, SessionLocal
from app.models import Job, UserProfile, SourceConfig, ScanHistory
from app.schemas import (
    JobResponse, JobStatusUpdate, UserProfileResponse, UserProfileUpdate,
    SourceConfigResponse, SourceConfigToggle, CustomSourceCreate, ScanStatsResponse
)
from app.scrapers.collector import collector
from app.services.matching import score_job_against_profile, DEFAULT_USER_SKILLS, DEFAULT_TARGET_TITLES
from app.services.resume_parser import parse_resume_file
from app.services.scheduler import start_scheduler, stop_scheduler, trigger_scan_async, is_currently_scanning

# Initialize database
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        collector.sync_source_configs(db)
        profile = collector.get_or_create_user_profile(db)
        collector.ensure_seed_benchmark_jobs(db, profile.skills, profile.target_titles)
    finally:
        db.close()

    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(
    title=settings.app_name,
    description="Continuous radar for Pakistani data jobs matching your engineering skill profile.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    index_path = TEMPLATES_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>Nokrify - Dashboard UI loading...</h1>"

@app.get("/api/jobs", response_model=List[JobResponse])
def list_jobs(
    search: Optional[str] = Query(None, description="Search term for title, company, or description"),
    min_score: int = Query(0, ge=0, le=100),
    status: Optional[str] = Query(None, description="Filter by status (NEW, VIEWED, APPLIED, INTERVIEWING, REJECTED)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    source: Optional[str] = Query(None, description="Filter by source"),
    max_age_hours: Optional[int] = Query(48, description="Filter jobs posted within last N hours (default 48h, 0 for all)"),
    zero_exp_only: bool = Query(False, description="Filter strictly for internships, trainee, and zero-experience positions"),
    experience_type: Optional[str] = Query(None, description="Filter by specific exp level (INTERNSHIP, TRAINEE, FRESH_GRAD)"),
    sort_by: str = Query("score_desc", pattern="^(score_desc|date_desc|title_asc)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    # 48-Hour Freshness Filter
    if max_age_hours and max_age_hours > 0:
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        query = query.filter(Job.date_posted >= cutoff)

    # Zero Experience / Trainee Focus Filter
    if zero_exp_only:
        query = query.filter(
            (Job.is_zero_experience == True) |
            (Job.experience_level.in_(["INTERNSHIP", "TRAINEE", "FRESH_GRAD"]))
        )

    if experience_type and experience_type.upper() != "ALL":
        query = query.filter(Job.experience_level == experience_type.upper())

    if min_score > 0:
        query = query.filter(Job.match_score >= min_score)

    if status and status.upper() != "ALL":
        query = query.filter(Job.status == status.upper())

    if city and city.upper() != "ALL":
        query = query.filter(Job.city.ilike(f"%{city}%"))

    if source and source.upper() != "ALL":
        query = query.filter(Job.source.ilike(f"%{source}%"))

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Job.title.ilike(search_fmt)) |
            (Job.company.ilike(search_fmt)) |
            (Job.description.ilike(search_fmt)) |
            (Job.matched_skills_json.ilike(search_fmt))
        )

    if sort_by == "score_desc":
        # Prioritize trainees and internships first, then score
        query = query.order_by(
            desc(Job.experience_level.in_(["INTERNSHIP", "TRAINEE"])),
            desc(Job.match_score),
            desc(Job.date_posted)
        )
    elif sort_by == "date_desc":
        query = query.order_by(desc(Job.date_posted), desc(Job.match_score))
    elif sort_by == "title_asc":
        query = query.order_by(asc(Job.title))

    return query.offset(offset).limit(limit).all()

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.patch("/api/jobs/{job_id}/status", response_model=JobResponse)
def update_job_status(job_id: int, update: JobStatusUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = update.status.upper()
    if update.notes is not None:
        job.notes = update.notes
    db.commit()
    db.refresh(job)
    return job

@app.get("/api/stats", response_model=ScanStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    cutoff_48 = now - timedelta(hours=48)

    total = db.query(Job).count()
    fresh_48 = db.query(Job).filter(Job.date_posted >= cutoff_48).count()
    high_matches = db.query(Job).filter(Job.match_score >= 70, Job.date_posted >= cutoff_48).count()
    if high_matches == 0:
        high_matches = db.query(Job).filter(Job.match_score >= 70).count()

    intern_trainee_count = db.query(Job).filter(
        (Job.is_zero_experience == True) |
        (Job.experience_level.in_(["INTERNSHIP", "TRAINEE", "FRESH_GRAD"]))
    ).count()

    linkedin_count = db.query(Job).filter(Job.source == "LinkedIn").count()
    applied = db.query(Job).filter(Job.status == "APPLIED").count()
    interviewing = db.query(Job).filter(Job.status == "INTERVIEWING").count()
    active_srcs = db.query(SourceConfig).filter(SourceConfig.enabled == True).count()
    
    last_scan = db.query(ScanHistory).order_by(desc(ScanHistory.started_at)).first()
    last_scan_time = last_scan.started_at if last_scan else None

    return ScanStatsResponse(
        total_jobs=total,
        fresh_jobs_48h=fresh_48,
        high_matches=high_matches,
        intern_trainee_count=intern_trainee_count,
        linkedin_jobs=linkedin_count,
        applied_count=applied,
        interviewing_count=interviewing,
        active_sources=active_srcs,
        last_scan_time=last_scan_time,
        is_scanning=is_currently_scanning()
    )

@app.post("/api/scan/pull")
def trigger_pull(db: Session = Depends(get_db)):
    """Triggers an immediate background pull across LinkedIn, Rozee, Indeed, etc."""
    started = trigger_scan_async()
    if not started:
        return {"status": "in_progress", "message": "Radar scan is already actively running."}
    return {"status": "started", "message": "Job Radar pull launched for internships, trainees, and fresh data roles."}

@app.get("/api/scan/status")
def get_scan_status(db: Session = Depends(get_db)):
    last_scan = db.query(ScanHistory).order_by(desc(ScanHistory.started_at)).first()
    return {
        "is_scanning": is_currently_scanning(),
        "last_scan": {
            "started_at": last_scan.started_at.isoformat() if last_scan and last_scan.started_at else None,
            "completed_at": last_scan.completed_at.isoformat() if last_scan and last_scan.completed_at else None,
            "status": last_scan.status if last_scan else "IDLE",
            "new_jobs": last_scan.new_jobs_found if last_scan else 0,
            "duplicates_merged": last_scan.duplicates_merged if last_scan else 0,
            "message": last_scan.message if last_scan else ""
        } if last_scan else None
    }

@app.get("/api/profile", response_model=UserProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    profile = collector.get_or_create_user_profile(db)
    return profile

@app.put("/api/profile", response_model=UserProfileResponse)
def update_profile(update: UserProfileUpdate, db: Session = Depends(get_db)):
    profile = collector.get_or_create_user_profile(db)
    if update.name is not None:
        profile.name = update.name
    if update.degree is not None:
        profile.degree = update.degree
    if update.location is not None:
        profile.location = update.location
    if update.skills is not None:
        profile.skills = update.skills
    if update.certifications is not None:
        profile.certifications = update.certifications
    if update.target_titles is not None:
        profile.target_titles = update.target_titles
    profile.last_updated = datetime.utcnow()
    db.commit()

    jobs = db.query(Job).all()
    for j in jobs:
        score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
            job_title=j.title,
            job_description=j.description,
            user_skills=profile.skills,
            target_titles=profile.target_titles
        )
        j.match_score = score
        j.matched_skills = matched_skills
        j.missing_skills = missing_skills
        j.match_breakdown = breakdown
        j.experience_level = exp_level
        j.is_zero_experience = is_zero_exp
        j.training_provided = training_provided
    db.commit()
    db.refresh(profile)
    return profile

@app.post("/api/profile/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    profile = collector.get_or_create_user_profile(db)
    
    file_path = RESUMES_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed_data = parse_resume_file(file_path)
    
    merged_skills = list(dict.fromkeys(profile.skills + parsed_data["skills"]))
    merged_certs = list(dict.fromkeys(profile.certifications + parsed_data["certifications"]))
    merged_titles = list(dict.fromkeys(profile.target_titles + parsed_data["target_titles"]))

    profile.skills = merged_skills
    profile.certifications = merged_certs
    profile.target_titles = merged_titles
    profile.resume_filename = file.filename
    profile.resume_text = parsed_data["raw_text"]
    profile.last_updated = datetime.utcnow()
    db.commit()

    jobs = db.query(Job).all()
    for j in jobs:
        score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
            job_title=j.title,
            job_description=j.description,
            user_skills=profile.skills,
            target_titles=profile.target_titles
        )
        j.match_score = score
        j.matched_skills = matched_skills
        j.missing_skills = missing_skills
        j.match_breakdown = breakdown
        j.experience_level = exp_level
        j.is_zero_experience = is_zero_exp
        j.training_provided = training_provided
    db.commit()

    return {
        "message": f"Resume parsed successfully! Extracted {len(parsed_data['skills'])} skills.",
        "filename": file.filename,
        "extracted_skills": parsed_data["skills"],
        "total_active_skills": len(merged_skills),
        "jobs_rescored": len(jobs)
    }

@app.get("/api/sources", response_model=List[SourceConfigResponse])
def list_sources(db: Session = Depends(get_db)):
    return db.query(SourceConfig).all()

@app.patch("/api/sources/{source_id}/toggle", response_model=SourceConfigResponse)
def toggle_source(source_id: int, toggle: SourceConfigToggle, db: Session = Depends(get_db)):
    src = db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    src.enabled = toggle.enabled
    db.commit()
    db.refresh(src)
    return src

@app.post("/api/sources/custom", response_model=SourceConfigResponse)
def add_custom_source(custom: CustomSourceCreate, db: Session = Depends(get_db)):
    existing = db.query(SourceConfig).filter(SourceConfig.name == custom.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A source with this internal name already exists")
    
    src = SourceConfig(
        name=custom.name.lower().replace(" ", "_"),
        display_name=custom.display_name,
        source_type=custom.source_type,
        base_url=custom.base_url,
        enabled=True
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    return src

@app.delete("/api/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    src = db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(src)
    db.commit()
    return {"status": "deleted", "id": source_id}
