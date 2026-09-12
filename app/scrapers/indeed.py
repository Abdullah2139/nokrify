from typing import List
from datetime import datetime
import feedparser
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from app.scrapers.base import BaseJobSource, RawJob

class IndeedPakistanJobSource(BaseJobSource):
    def __init__(self):
        super().__init__(
            name="indeed",
            display_name="Indeed Pakistan",
            base_url="https://pk.indeed.com"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        if not keywords:
            keywords = ["Data Analyst", "Data Engineer", "Power BI", "SQL"]

        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:3]:
            # fromage=2 restricts strictly to postings within the past 2 days (48 hours)
            feed_url = f"https://pk.indeed.com/rss?q={quote_plus(kw)}&l=Pakistan&fromage=2"
            try:
                self.polite_delay()
                feed = feedparser.parse(
                    feed_url,
                    request_headers={"User-Agent": self.session.headers["User-Agent"]}
                )

                for entry in getattr(feed, "entries", []):
                    link = getattr(entry, "link", "")
                    if not link or link in seen_urls:
                        continue
                    seen_urls.add(link)

                    raw_title = getattr(entry, "title", "Data Position")
                    parts = [p.strip() for p in raw_title.split(" - ")]
                    title = parts[0] if parts else raw_title
                    company = parts[1] if len(parts) > 1 else getattr(entry, "author", "Employer via Indeed")
                    location = parts[2] if len(parts) > 2 else "Pakistan"

                    raw_desc = getattr(entry, "summary", "") or getattr(entry, "description", "")
                    desc_soup = BeautifulSoup(raw_desc, "html.parser")
                    clean_desc = desc_soup.get_text(separator=" ", strip=True)

                    city = "Pakistan"
                    for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan", "Remote"]:
                        if c.lower() in location.lower() or c.lower() in raw_title.lower():
                            city = c
                            break

                    jobs.append(RawJob(
                        title=title,
                        company=company,
                        location=location,
                        city=city,
                        industry="General / Corporate",
                        source="Indeed Pakistan",
                        source_url=link,
                        description=clean_desc or f"{title} at {company}",
                        date_posted=datetime.utcnow()
                    ))
            except Exception:
                continue

        return jobs
