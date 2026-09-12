from typing import List, Optional
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
from app.scrapers.base import BaseJobSource, RawJob

class GenericRSSJobSource(BaseJobSource):
    """
    Parses any arbitrary RSS / Atom feed URL or Google Alerts feed for job listings.
    Allows users to add any job source without writing code.
    """
    def __init__(self, name: str, display_name: str, feed_url: str):
        super().__init__(name=name, display_name=display_name, base_url=feed_url)
        self.feed_url = feed_url

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        try:
            self.polite_delay()
            feed = feedparser.parse(
                self.feed_url,
                request_headers={"User-Agent": self.session.headers["User-Agent"]}
            )

            for entry in getattr(feed, "entries", []):
                link = getattr(entry, "link", "")
                title = getattr(entry, "title", "Job Posting")
                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                
                # strip html from summary
                soup = BeautifulSoup(raw_summary, "html.parser")
                clean_desc = soup.get_text(separator=" ", strip=True)

                # extract published date if available
                dt = datetime.utcnow()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                # Detect city in title or desc
                city = "Pakistan"
                for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan", "Remote"]:
                    if c.lower() in title.lower() or c.lower() in clean_desc.lower():
                        city = c
                        break

                company = getattr(entry, "author", "RSS Feed Source")

                jobs.append(RawJob(
                    title=title,
                    company=company,
                    location=city,
                    city=city,
                    industry="Feed / Aggregator",
                    source=self.display_name,
                    source_url=link,
                    description=clean_desc or title,
                    date_posted=dt
                ))
        except Exception:
            pass

        return jobs
