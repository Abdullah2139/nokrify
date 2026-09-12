import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
RESUMES_DIR = DATA_DIR / "resumes"
RESUMES_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Nokrify - Pakistan Data Jobs Radar"
    database_url: str = f"sqlite:///{DATA_DIR / 'jobs.db'}"
    scheduler_interval_hours: int = 4
    min_match_score_highlight: int = 70
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (compatible; NokrifyJobRadar/1.0; +https://github.com/nokrify)"
    )
    request_timeout_seconds: int = 15
    request_delay_seconds: float = 1.5

settings = Settings()
