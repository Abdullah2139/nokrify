from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from app.scrapers.base import BaseJobSource, RawJob

class JobzPkJobSource(BaseJobSource):
    def __init__(self):
        super().__init__(
            name="jobz_pk",
            display_name="Jobz.pk",
            base_url="https://www.jobz.pk"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        if not keywords:
            keywords = ["data-analyst", "database-administrator", "computer"]

        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:2]:
            clean_slug = kw.lower().replace(" ", "-")
            url = f"{self.base_url}/{clean_slug}-jobs/"
            resp = self.safe_get(url)
            if not resp or not resp.text:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            # Jobz.pk uses list items and tables for listings
            rows = soup.find_all(["tr", "div", "li"], class_=lambda c: c and ("job" in c.lower() or "row" in c.lower()))
            if not rows:
                rows = soup.find_all("a", href=lambda h: h and "_jobs" in h)

            for row in rows[:20]:
                link_elem = row if row.name == "a" else row.find("a", href=lambda h: h and "_jobs" in h)
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link = link_elem.get("href", "")
                if link and not link.startswith("http"):
                    link = f"{self.base_url}/{link.lstrip('/')}"
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                # Location & City
                city = "Pakistan"
                for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan"]:
                    if c.lower() in title.lower():
                        city = c
                        break

                jobs.append(RawJob(
                    title=title,
                    company="Newspaper / Corporate Listing",
                    location=city,
                    city=city,
                    industry="Public & Private Sector",
                    source="Jobz.pk",
                    source_url=link,
                    description=f"{title} published via Jobz.pk. Opportunity for data professionals in Pakistan.",
                    date_posted=datetime.utcnow()
                ))

        return jobs
