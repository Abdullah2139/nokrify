from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from app.scrapers.base import BaseJobSource, RawJob

class RozeeJobSource(BaseJobSource):
    def __init__(self):
        super().__init__(
            name="rozee",
            display_name="Rozee.pk",
            base_url="https://www.rozee.pk"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        if not keywords:
            keywords = ["Data Analyst", "Data Engineer", "Power BI", "SQL"]

        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:3]:  # Top query seeds to keep polite
            url = f"{self.base_url}/job/jsearch/q/{quote_plus(kw)}"
            resp = self.safe_get(url)
            if not resp or not resp.text:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.select(".job, .job-item, .c_jobs, .search-job")
            if not job_cards:
                # Alternate selector for modern Rozee layout
                job_cards = soup.find_all("div", class_=lambda c: c and "job" in c.lower())

            for card in job_cards:
                title_elem = card.find("a", href=lambda h: h and "/job/" in h) or card.find("h3") or card.find("h2")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                link = title_elem.get("href") if title_elem.name == "a" else (title_elem.find("a") or {}).get("href", "")
                if link and not link.startswith("http"):
                    link = f"{self.base_url}{link}"
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                # Company
                comp_elem = card.find(class_=lambda c: c and ("comp" in c.lower() or "c_name" in c.lower())) or card.find("span", class_="cname")
                company = comp_elem.get_text(strip=True) if comp_elem else "Rozee Employer"

                # Location / City
                loc_elem = card.find(class_=lambda c: c and ("loc" in c.lower() or "city" in c.lower()))
                location = loc_elem.get_text(strip=True) if loc_elem else "Pakistan"

                # Snippet / Description
                desc_elem = card.find(class_=lambda c: c and ("desc" in c.lower() or "detail" in c.lower() or "snippet" in c.lower()))
                desc = desc_elem.get_text(strip=True) if desc_elem else f"{title} at {company}. Skills: SQL, Analytics."

                # City determination
                city = "Pakistan"
                for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan", "Remote"]:
                    if c.lower() in location.lower() or c.lower() in title.lower():
                        city = c
                        break

                jobs.append(RawJob(
                    title=title,
                    company=company,
                    location=location,
                    city=city,
                    industry="Technology / Corporate",
                    source="Rozee.pk",
                    source_url=link,
                    description=desc,
                    date_posted=datetime.utcnow()
                ))

        return jobs
