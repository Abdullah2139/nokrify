from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import time
import random
import requests
from app.config import settings

@dataclass
class RawJob:
    title: str
    company: str
    location: str
    city: str
    industry: str
    source: str
    source_url: str
    description: str
    date_posted: Optional[datetime] = None
    original_id: Optional[str] = None
    extra_metadata: dict = field(default_factory=dict)

class BaseJobSource(ABC):
    def __init__(self, name: str, display_name: str, base_url: str):
        self.name = name
        self.display_name = display_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def polite_delay(self):
        """Applies a polite delay between requests to avoid hammering target sites."""
        delay = settings.request_delay_seconds + random.uniform(0.5, 1.5)
        time.sleep(delay)

    def safe_get(self, url: str, params: dict = None) -> Optional[requests.Response]:
        """Performs a polite HTTP GET request with error handling and timeout."""
        try:
            self.polite_delay()
            resp = self.session.get(
                url,
                params=params,
                timeout=settings.request_timeout_seconds
            )
            if resp.status_code == 200:
                return resp
            return None
        except Exception:
            return None

    @abstractmethod
    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        """Fetch listings from the source and return a normalized list of RawJob objects."""
        pass
