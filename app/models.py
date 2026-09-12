from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    normalized_title = Column(String(255), index=True)
    company = Column(String(255), default="Unknown", index=True)
    normalized_company = Column(String(255), index=True)
    location = Column(String(255), default="Pakistan", index=True)
    city = Column(String(100), default="Pakistan", index=True)
    industry = Column(String(100), default="All / General", index=True)
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(String(1000), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    date_posted = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Zero Experience & Trainee classification
    experience_level = Column(String(50), default="ENTRY_LEVEL", index=True) # INTERNSHIP, TRAINEE, FRESH_GRAD, ENTRY_LEVEL
    is_zero_experience = Column(Boolean, default=True, index=True)
    training_provided = Column(Boolean, default=False, index=True)

    # Matching Engine results
    match_score = Column(Integer, default=0, index=True)
    matched_skills_json = Column(Text, default="[]")
    missing_skills_json = Column(Text, default="[]")
    match_breakdown_json = Column(Text, default="{}")
    
    # Status Workflow: NEW, VIEWED, APPLIED, INTERVIEWING, REJECTED, ARCHIVED
    status = Column(String(50), default="NEW", index=True)
    notes = Column(Text, default="")
    duplicate_urls_json = Column(Text, default="[]")

    @property
    def matched_skills(self):
        try:
            return json.loads(self.matched_skills_json or "[]")
        except Exception:
            return []

    @matched_skills.setter
    def matched_skills(self, value):
        self.matched_skills_json = json.dumps(value or [])

    @property
    def missing_skills(self):
        try:
            return json.loads(self.missing_skills_json or "[]")
        except Exception:
            return []

    @missing_skills.setter
    def missing_skills(self, value):
        self.missing_skills_json = json.dumps(value or [])

    @property
    def match_breakdown(self):
        try:
            return json.loads(self.match_breakdown_json or "{}")
        except Exception:
            return {}

    @match_breakdown.setter
    def match_breakdown(self, value):
        self.match_breakdown_json = json.dumps(value or {})

    @property
    def duplicate_urls(self):
        try:
            return json.loads(self.duplicate_urls_json or "[]")
        except Exception:
            return []

    @duplicate_urls.setter
    def duplicate_urls(self, value):
        self.duplicate_urls_json = json.dumps(value or [])


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), default="Fresh Graduate")
    degree = Column(String(255), default="BSc Computer Systems Engineering")
    location = Column(String(255), default="Pakistan")
    skills_json = Column(Text, default="[]")
    certifications_json = Column(Text, default="[]")
    target_titles_json = Column(Text, default="[]")
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

    @property
    def skills(self):
        try:
            return json.loads(self.skills_json or "[]")
        except Exception:
            return []

    @skills.setter
    def skills(self, value):
        self.skills_json = json.dumps(value or [])

    @property
    def certifications(self):
        try:
            return json.loads(self.certifications_json or "[]")
        except Exception:
            return []

    @certifications.setter
    def certifications(self, value):
        self.certifications_json = json.dumps(value or [])

    @property
    def target_titles(self):
        try:
            return json.loads(self.target_titles_json or "[]")
        except Exception:
            return []

    @target_titles.setter
    def target_titles(self, value):
        self.target_titles_json = json.dumps(value or [])


class SourceConfig(Base):
    __tablename__ = "source_configs"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    source_type = Column(String(50), default="scraper")
    base_url = Column(String(500), nullable=False)
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    last_status = Column(String(50), default="IDLE")
    last_error = Column(Text, nullable=True)
    total_jobs_found = Column(Integer, default=0)


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    sources_scanned = Column(Integer, default=0)
    new_jobs_found = Column(Integer, default=0)
    duplicates_merged = Column(Integer, default=0)
    status = Column(String(50), default="RUNNING")
    message = Column(Text, default="")
