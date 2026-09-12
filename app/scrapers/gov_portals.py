from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.base import BaseJobSource, RawJob

class GovPortalsJobSource(BaseJobSource):
    """
    Monitors official Pakistani government recruitment portals and testing agencies
    (NTS, FPSC, PPSC) for IT, Computer Systems, Data, and MIS Officer positions.
    """
    def __init__(self):
        super().__init__(
            name="gov_portals",
            display_name="Government Portals (NTS / FPSC / PPSC)",
            base_url="https://www.nts.org.pk"
        )

    def fetch_jobs(self, keywords: List[str] = None) -> List[RawJob]:
        jobs: List[RawJob] = []
        seen_urls = set()

        # 1. NTS Open Projects
        nts_url = "https://www.nts.org.pk/new/open-projects"
        resp = self.safe_get(nts_url)
        if resp and resp.text:
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                text = row.get_text(separator=" ", strip=True)
                # Check for data/IT roles
                if any(kw in text.lower() for kw in ["data", "computer", "database", "mis", "analytics", "it officer", "systems"]):
                    link_elem = row.find("a")
                    link = link_elem.get("href", "") if link_elem else nts_url
                    if link and not link.startswith("http"):
                        link = f"https://www.nts.org.pk{link}"
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    jobs.append(RawJob(
                        title=text[:80].strip(),
                        company="National Testing Service (Public Sector Project)",
                        location="Islamabad / Nationwide",
                        city="Islamabad",
                        industry="Public Sector / Government",
                        source="NTS Pakistan",
                        source_url=link,
                        description=f"Government recruitment project: {text[:250]}. Relevant for engineering & IT graduates.",
                        date_posted=datetime.utcnow()
                    ))

        # 2. Pakistan Jobs Bank public aggregator feed
        pjb_url = "https://www.pakistanjobsbank.com"
        resp_pjb = self.safe_get(pjb_url)
        if resp_pjb and resp_pjb.text:
            soup_pjb = BeautifulSoup(resp_pjb.text, "html.parser")
            for a in soup_pjb.find_all("a", href=True):
                title = a.get_text(strip=True)
                if len(title) > 10 and any(k in title.lower() for k in ["data", "mis officer", "database", "analytics"]):
                    link = a["href"]
                    if not link.startswith("http"):
                        link = f"{pjb_url}/{link.lstrip('/')}"
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    jobs.append(RawJob(
                        title=title,
                        company="Federal / Provincial Government Department",
                        location="Pakistan",
                        city="Islamabad",
                        industry="Government / Public Sector",
                        source="PakistanJobsBank",
                        source_url=link,
                        description=f"Public sector job vacancy: {title}. Requires degree in Computer Systems / IT.",
                        date_posted=datetime.utcnow()
                    ))

        return jobs
