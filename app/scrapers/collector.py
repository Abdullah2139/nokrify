import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import Job, UserProfile, SourceConfig, ScanHistory
from app.scrapers.base import BaseJobSource, RawJob
from app.scrapers.linkedin import LinkedInJobSource
from app.scrapers.rozee import RozeeJobSource
from app.scrapers.indeed import IndeedPakistanJobSource
from app.scrapers.jobz_pk import JobzPkJobSource
from app.scrapers.mustakbil import MustakbilJobSource
from app.scrapers.brightspyre import BrightSpyreJobSource
from app.scrapers.bayt import BaytPakistanJobSource
from app.scrapers.gov_portals import GovPortalsJobSource
from app.scrapers.rss_feed import GenericRSSJobSource
from app.scrapers.seed_data import get_initial_seed_jobs
from app.services.matching import score_job_against_profile, DEFAULT_USER_SKILLS, DEFAULT_TARGET_TITLES
from app.services.deduplication import is_duplicate_job, normalize_text, normalize_company

logger = logging.getLogger("nokrify.collector")

class JobCollector:
    def __init__(self):
        self.default_sources: Dict[str, BaseJobSource] = {
            "linkedin": LinkedInJobSource(),
            "rozee": RozeeJobSource(),
            "indeed": IndeedPakistanJobSource(),
            "jobz_pk": JobzPkJobSource(),
            "mustakbil": MustakbilJobSource(),
            "brightspyre": BrightSpyreJobSource(),
            "bayt": BaytPakistanJobSource(),
            "gov_portals": GovPortalsJobSource(),
        }

    def sync_source_configs(self, db: Session):
        """Ensures all standard sources exist in the database configuration table."""
        for name, src in self.default_sources.items():
            existing = db.query(SourceConfig).filter(SourceConfig.name == name).first()
            if not existing:
                cfg = SourceConfig(
                    name=name,
                    display_name=src.display_name,
                    source_type="scraper",
                    base_url=src.base_url,
                    enabled=True
                )
                db.add(cfg)
        db.commit()

    def get_or_create_user_profile(self, db: Session) -> UserProfile:
        profile = db.query(UserProfile).first()
        if not profile:
            profile = UserProfile(
                name="Fresh Graduate (BSc Computer Systems Engineering)",
                degree="BSc Computer Systems Engineering",
                location="Pakistan",
                skills=DEFAULT_USER_SKILLS,
                certifications=[
                    "Google Data Analytics Certificate",
                    "IBM Data Analytics Professional Certificate"
                ],
                target_titles=DEFAULT_TARGET_TITLES
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    def ensure_seed_benchmark_jobs(self, db: Session, user_skills: List[str], target_titles: List[str]) -> int:
        """Populates verified real data jobs from the past 48 hours, highlighting internships and trainees."""
        seed_jobs = get_initial_seed_jobs()
        added = 0
        for rjob in seed_jobs:
            if not db.query(Job).filter(Job.source_url == rjob.source_url).first():
                score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
                    job_title=rjob.title,
                    job_description=rjob.description,
                    user_skills=user_skills,
                    target_titles=target_titles
                )
                s_job = Job(
                    title=rjob.title,
                    normalized_title=normalize_text(rjob.title),
                    company=rjob.company,
                    normalized_company=normalize_company(rjob.company),
                    location=rjob.location,
                    city=rjob.city,
                    industry=rjob.industry,
                    source=rjob.source,
                    source_url=rjob.source_url,
                    description=rjob.description,
                    date_posted=rjob.date_posted or datetime.utcnow(),
                    scraped_at=datetime.utcnow(),
                    experience_level=exp_level,
                    is_zero_experience=is_zero_exp,
                    training_provided=training_provided,
                    match_score=score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    match_breakdown=breakdown,
                    status="NEW",
                    duplicate_urls=[]
                )
                db.add(s_job)
                added += 1
        if added > 0:
            db.commit()
        return added

    def run_scan(self, db: Session, include_network: bool = True, max_age_hours: int = 48) -> ScanHistory:
        """Executes a multi-source polite job scan, prioritizing internships, trainees, and LinkedIn."""
        self.sync_source_configs(db)
        user_profile = self.get_or_create_user_profile(db)
        user_skills = user_profile.skills or DEFAULT_USER_SKILLS
        target_titles = user_profile.target_titles or DEFAULT_TARGET_TITLES

        scan_record = ScanHistory(
            started_at=datetime.utcnow(),
            status="RUNNING",
            sources_scanned=0,
            new_jobs_found=0,
            duplicates_merged=0
        )
        db.add(scan_record)
        db.commit()

        total_new = self.ensure_seed_benchmark_jobs(db, user_skills, target_titles)
        total_merged = 0
        sources_scanned = 0

        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours + 12)

        if include_network:
            active_configs = (
                db.query(SourceConfig)
                .filter(SourceConfig.enabled == True)
                .order_by((SourceConfig.name == "linkedin").desc())
                .all()
            )
            existing_jobs = db.query(Job).all()

            for cfg in active_configs:
                source_impl: BaseJobSource = None
                if cfg.name in self.default_sources:
                    source_impl = self.default_sources[cfg.name]
                elif cfg.source_type == "rss":
                    source_impl = GenericRSSJobSource(
                        name=cfg.name,
                        display_name=cfg.display_name,
                        feed_url=cfg.base_url
                    )

                if not source_impl:
                    continue

                sources_scanned += 1
                cfg.last_run = datetime.utcnow()
                cfg.last_status = "RUNNING"
                db.commit()

                try:
                    raw_jobs: List[RawJob] = source_impl.fetch_jobs(keywords=target_titles[:4])
                    found_for_source = 0

                    for rjob in raw_jobs:
                        if rjob.date_posted and rjob.date_posted < cutoff_time:
                            continue

                        exact_match = db.query(Job).filter(Job.source_url == rjob.source_url).first()
                        if exact_match:
                            continue

                        duplicate_found = False
                        for ejob in existing_jobs:
                            if is_duplicate_job(
                                new_title=rjob.title,
                                new_company=rjob.company,
                                new_city=rjob.city,
                                existing_title=ejob.title,
                                existing_company=ejob.company,
                                existing_city=ejob.city
                            ):
                                urls = ejob.duplicate_urls
                                if rjob.source_url not in urls:
                                    urls.append(rjob.source_url)
                                    ejob.duplicate_urls = urls
                                    db.commit()
                                total_merged += 1
                                duplicate_found = True
                                break

                        if duplicate_found:
                            continue

                        score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
                            job_title=rjob.title,
                            job_description=rjob.description,
                            user_skills=user_skills,
                            target_titles=target_titles
                        )

                        new_job = Job(
                            title=rjob.title,
                            normalized_title=normalize_text(rjob.title),
                            company=rjob.company,
                            normalized_company=normalize_company(rjob.company),
                            location=rjob.location,
                            city=rjob.city,
                            industry=rjob.industry,
                            source=rjob.source,
                            source_url=rjob.source_url,
                            description=rjob.description,
                            date_posted=rjob.date_posted or datetime.utcnow(),
                            scraped_at=datetime.utcnow(),
                            experience_level=exp_level,
                            is_zero_experience=is_zero_exp,
                            training_provided=training_provided,
                            match_score=score,
                            matched_skills=matched_skills,
                            missing_skills=missing_skills,
                            match_breakdown=breakdown,
                            status="NEW",
                            duplicate_urls=[]
                        )
                        db.add(new_job)
                        db.commit()
                        existing_jobs.append(new_job)
                        found_for_source += 1
                        total_new += 1

                    cfg.last_status = "SUCCESS"
                    cfg.total_jobs_found += found_for_source
                    cfg.last_error = None
                    db.commit()

                except Exception as e:
                    cfg.last_status = "ERROR"
                    cfg.last_error = str(e)[:400]
                    db.commit()

        scan_record.completed_at = datetime.utcnow()
        scan_record.sources_scanned = sources_scanned
        scan_record.new_jobs_found = total_new
        scan_record.duplicates_merged = total_merged
        scan_record.status = "COMPLETED"
        scan_record.message = f"Found {total_new} new data opportunities across Pakistan. Merged {total_merged} cross-board duplicates."
        db.commit()

        return scan_record

collector = JobCollector()
