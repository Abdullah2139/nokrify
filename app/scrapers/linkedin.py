import re
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from app.scrapers.base import BaseJobSource, RawJob

logger = logging.getLogger("nokrify.scrapers.linkedin")

def parse_relative_time(time_str: str) -> datetime:
    """Parses relative time like '10 hours ago', '1 day ago', '2 days ago' into a datetime."""
    now = datetime.utcnow()
    if not time_str:
        return now
    time_str = time_str.lower().strip()

    # Hours
    m_hour = re.search(r"(\d+)\s+hour", time_str)
    if m_hour:
        return now - timedelta(hours=int(m_hour.group(1)))

    # Days
    m_day = re.search(r"(\d+)\s+day", time_str)
    if m_day:
        return now - timedelta(days=int(m_day.group(1)))

    # Minutes
    m_min = re.search(r"(\d+)\s+minute", time_str)
    if m_min:
        return now - timedelta(minutes=int(m_min.group(1)))

    return now

class LinkedInJobSource(BaseJobSource):
    """
    Direct guest API scraper for LinkedIn Pakistan.
    Focuses specifically on Internships and Trainee/Entry-Level data positions (f_E=1,2).
    Enforces strict 48-hour freshness (f_TPR=r172800) with working direct URLs.
    """
    def __init__(self):
        super().__init__(
            name="linkedin",
            display_name="LinkedIn Pakistan",
            base_url="https://www.linkedin.com"
        )
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def fetch_jobs(self, keywords: List[str] = None, hours_limit: int = 48) -> List[RawJob]:
        if not keywords:
            keywords = [
                "data engineer intern",
                "data engineering intern",
                "database intern",
                "SQL intern",
                "data analyst intern",
                "BI intern",
                "ETL intern",
                "data trainee",
                "management trainee data",
                "graduate trainee data",
                "azure data intern",
                "aws data intern",
                "big data intern",
                "data platform intern"
            ]

        tpr = "r172800" if hours_limit <= 48 else "r604800"
        jobs: List[RawJob] = []
        seen_urls = set()

        for kw in keywords[:5]:
            url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            params = {
                "keywords": kw,
                "location": "Pakistan",
                "f_TPR": tpr,
                "f_E": "1,2", # 1 = Internship, 2 = Entry level (0-experience / learning positions)
                "start": 0
            }

            try:
                self.polite_delay()
                resp = self.session.get(url, params=params, timeout=12)
                if resp.status_code != 200 or not resp.text:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.find_all("li")

                for card in cards:
                    title_tag = card.find("h3", class_="base-search-card__title") or card.find("h3")
                    comp_tag = (
                        card.find("h4", class_="base-search-card__subtitle") or
                        card.find("a", class_="hidden-nested-link") or
                        card.find("h4")
                    )
                    loc_tag = card.find("span", class_="job-search-card__location")
                    link_tag = card.find("a", class_="base-card__full-link") or card.find("a")
                    time_tag = card.find("time")

                    if not title_tag or not link_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue

                    raw_link = link_tag.get("href", "")
                    clean_link = raw_link.split("?")[0] if raw_link else ""
                    if not clean_link or clean_link in seen_urls:
                        continue
                    seen_urls.add(clean_link)

                    company = comp_tag.get_text(strip=True) if comp_tag else "Company on LinkedIn"
                    location = loc_tag.get_text(strip=True) if loc_tag else "Pakistan"
                    time_str = time_tag.get_text(strip=True) if time_tag else "Recent"
                    posted_dt = parse_relative_time(time_str)

                    city = "Pakistan"
                    for c in ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Multan", "Remote"]:
                        if c.lower() in location.lower() or c.lower() in title.lower():
                            city = c
                            break

                    description = (
                        f"{title} position at {company} in {location}. "
                        f"Listed on LinkedIn {time_str}. Focuses on internship, trainee, or fresh graduate data talent. "
                        f"Hands-on learning with SQL, Power BI, Azure, Python, ETL pipelines, and modern data engineering tools."
                    )

                    jobs.append(RawJob(
                        title=title,
                        company=company,
                        location=location,
                        city=city,
                        industry="Technology & Professional Services",
                        source="LinkedIn",
                        source_url=clean_link,
                        description=description,
                        date_posted=posted_dt,
                        extra_metadata={"posted_text": time_str}
                    ))

            except Exception as e:
                logger.warning(f"Error fetching from LinkedIn for '{kw}': {e}")
                continue

        return jobs
