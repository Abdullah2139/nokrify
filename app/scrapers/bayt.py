from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from app.scrapers.base import BaseJobSource, RawJob

class BaytPakistanJobSource(BaseJobSource):
    def __init__(self):
        super().__init__(
            name="bayt",
            display_name="Bayt.com (Pakistan)",
            base_url="https://www.bayt.com"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        if not keywords:
            keywords = ["data-analyst", "business-intelligence"]

        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:2]:
            slug = kw.lower().replace(" ", "-")
            url = f"{self.base_url}/en/pakistan/jobs/{slug}-jobs/"
            resp = self.safe_get(url)
            if not resp or not resp.text:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("[data-js-job], .has-pointer-d, li.jb")

            for card in cards:
                title_elem = card.find("h2") or card.find("a", href=lambda h: h and "/job/" in h)
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if not title or len(title) < 4:
                    continue

                link_elem = title_elem if title_elem.name == "a" else (title_elem.find("a") or {})
                link = link_elem.get("href", "")
                if link and not link.startswith("http"):
                    link = f"{self.base_url}{link}"
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                comp_elem = card.find(class_=lambda c: c and "comp" in c.lower()) or card.find("b")
                company = comp_elem.get_text(strip=True) if comp_elem else "Bayt Client"

                loc_elem = card.find(class_=lambda c: c and ("loc" in c.lower() or "city" in c.lower()))
                location = loc_elem.get_text(strip=True) if loc_elem else "Pakistan"

                city = "Pakistan"
                for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad"]:
                    if c.lower() in location.lower() or c.lower() in title.lower():
                        city = c
                        break

                desc_elem = card.find(class_=lambda c: c and ("desc" in c.lower() or "snippet" in c.lower()))
                desc = desc_elem.get_text(strip=True) if desc_elem else f"{title} at {company}."

                jobs.append(RawJob(
                    title=title,
                    company=company,
                    location=location,
                    city=city,
                    industry="International / Corporate",
                    source="Bayt.com",
                    source_url=link,
                    description=desc,
                    date_posted=datetime.utcnow()
                ))

        return jobs
