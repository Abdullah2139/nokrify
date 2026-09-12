from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from app.scrapers.base import BaseJobSource, RawJob

class MustakbilJobSource(BaseJobSource):
    def __init__(self):
        super().__init__(
            name="mustakbil",
            display_name="Mustakbil.com",
            base_url="https://www.mustakbil.com"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        if not keywords:
            keywords = ["Data Analyst", "Database", "Power BI"]

        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:2]:
            url = f"{self.base_url}/jobs/pakistan?q={quote_plus(kw)}"
            resp = self.safe_get(url)
            if not resp or not resp.text:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".job-list-item, .job-item, .listing-card") or soup.find_all("div", class_=lambda c: c and "job" in c.lower())

            for card in cards:
                title_link = card.find("a", href=lambda h: h and ("/job/" in h or "/jobs/" in h))
                if not title_link:
                    continue

                title = title_link.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                link = title_link.get("href", "")
                if link and not link.startswith("http"):
                    link = f"{self.base_url}{link}"
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                # Company
                comp_elem = card.find(class_=lambda c: c and ("company" in c.lower() or "employer" in c.lower()))
                company = comp_elem.get_text(strip=True) if comp_elem else "Mustakbil Employer"

                # Location
                loc_elem = card.find(class_=lambda c: c and ("loc" in c.lower() or "city" in c.lower()))
                location = loc_elem.get_text(strip=True) if loc_elem else "Pakistan"

                # City
                city = "Pakistan"
                for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan", "Remote"]:
                    if c.lower() in location.lower() or c.lower() in title.lower():
                        city = c
                        break

                desc_elem = card.find(class_=lambda c: c and ("desc" in c.lower() or "summary" in c.lower()))
                desc = desc_elem.get_text(strip=True) if desc_elem else f"{title} at {company}. Relevant for analytics and data engineering."

                jobs.append(RawJob(
                    title=title,
                    company=company,
                    location=location,
                    city=city,
                    industry="Corporate / IT",
                    source="Mustakbil.com",
                    source_url=link,
                    description=desc,
                    date_posted=datetime.utcnow()
                ))

        return jobs
