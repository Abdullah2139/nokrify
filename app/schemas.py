from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class JobBase(BaseModel):
    title: str
    company: str = "Unknown"
    location: str = "Pakistan"
    city: str = "Pakistan"
    industry: str = "All / General"
    source: str
    source_url: str
    description: str = ""
    date_posted: Optional[datetime] = None

class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    normalized_title: Optional[str] = None
    normalized_company: Optional[str] = None
    scraped_at: datetime
    
    # Zero Experience / Trainee metadata
    experience_level: str = "ENTRY_LEVEL" # INTERNSHIP, TRAINEE, FRESH_GRAD, ENTRY_LEVEL, EXPERIENCED
    is_zero_experience: bool = True
    training_provided: bool = False

    match_score: int = 0
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    match_breakdown: Dict[str, Any] = {}
    status: str = "NEW"
    notes: Optional[str] = ""
    duplicate_urls: List[str] = []

class JobStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    degree: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    target_titles: Optional[List[str]] = None

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    degree: str
    location: str
    skills: List[str]
    certifications: List[str]
    target_titles: List[str]
    resume_filename: Optional[str] = None
    last_updated: datetime

class SourceConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str
    source_type: str
    base_url: str
    enabled: bool
    last_run: Optional[datetime] = None
    last_status: str
    last_error: Optional[str] = None
    total_jobs_found: int

class SourceConfigToggle(BaseModel):
    enabled: bool

class CustomSourceCreate(BaseModel):
    name: str
    display_name: str
    base_url: str
    source_type: str = "rss"

class ScanStatsResponse(BaseModel):
    total_jobs: int
    fresh_jobs_48h: int
    high_matches: int  # score >= 70
    intern_trainee_count: int # internships & trainee positions
    linkedin_jobs: int
    applied_count: int
    interviewing_count: int
    active_sources: int
    last_scan_time: Optional[datetime] = None
    is_scanning: bool = False
