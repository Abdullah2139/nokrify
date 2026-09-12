import re
from typing import Optional
from thefuzz import fuzz

COMPANY_SUFFIXES = [
    r"\b(pvt|private)\.?\s*(ltd|limited)\b",
    r"\b(ltd|limited)\b",
    r"\b(llc|inc|corp|corporation)\b",
    r"\bpakistan\b",
    r"\btechnologies\b",
    r"\bsolutions\b",
    r"\bgroup\b"
]

def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    # Normalize common abbreviations
    text = re.sub(r"\bbi\b", "business intelligence", text)
    # remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_company(company: Optional[str]) -> str:
    norm = normalize_text(company)
    for pat in COMPANY_SUFFIXES:
        norm = re.sub(pat, "", norm)
    return re.sub(r"\s+", " ", norm).strip()

def normalize_city(city: Optional[str]) -> str:
    norm = normalize_text(city)
    if "karachi" in norm:
        return "karachi"
    if "lahore" in norm:
        return "lahore"
    if "islamabad" in norm or "rawalpindi" in norm:
        return "islamabad/rawalpindi"
    if "faisalabad" in norm:
        return "faisalabad"
    if "peshawar" in norm:
        return "peshawar"
    if "multan" in norm:
        return "multan"
    if "remote" in norm:
        return "remote"
    return norm or "pakistan"

def is_duplicate_job(
    new_title: str,
    new_company: str,
    new_city: str,
    existing_title: str,
    existing_company: str,
    existing_city: str
) -> bool:
    """
    Determines if two job postings represent the exact same opportunity.
    Uses token set matching to handle acronym expansions and sub-titles.
    """
    t1 = normalize_text(new_title)
    t2 = normalize_text(existing_title)
    c1 = normalize_company(new_company)
    c2 = normalize_company(existing_company)
    city1 = normalize_city(new_city)
    city2 = normalize_city(existing_city)

    # 1. Company match
    if c1 in ["unknown", "confidential", ""] or c2 in ["unknown", "confidential", ""]:
        company_sim = 75
    else:
        company_sim = fuzz.token_set_ratio(c1, c2)

    # 2. Title match using token_set_ratio for acronym / extra word tolerance
    title_sim = fuzz.token_set_ratio(t1, t2)

    # 3. Location match
    location_match = (
        city1 == city2 or
        city1 in ["pakistan", "remote", ""] or
        city2 in ["pakistan", "remote", ""]
    )

    if title_sim >= 80 and company_sim >= 75 and location_match:
        return True
    return False
