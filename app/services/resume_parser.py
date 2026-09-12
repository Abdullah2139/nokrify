import re
from pathlib import Path
from typing import Dict, Any, List

COMMON_DATA_SKILLS = [
    "SQL", "Power BI", "Excel", "Advanced Excel", "MySQL", "PostgreSQL",
    "Microsoft Azure", "Azure Data Factory", "ADLS Gen2", "Azure SQL",
    "AWS", "S3", "AWS Glue", "Redshift", "Python", "Pandas", "NumPy",
    "PySpark", "Apache Spark", "Git", "GitHub", "GitLab", "Tableau",
    "ETL", "Data Warehousing", "Data Modeling", "DAX", "Power Query",
    "Docker", "Linux", "Airflow", "Kafka", "Snowflake", "Databricks",
    "BigQuery", "Machine Learning", "Scikit-Learn", "Matplotlib", "Seaborn"
]

COMMON_CERTIFICATIONS = [
    "Google Data Analytics",
    "Google Data Analytics Certificate",
    "IBM Data Analytics",
    "IBM Data Analytics Professional Certificate",
    "Microsoft Certified: Azure Data Fundamentals",
    "DP-900", "DP-203", "AWS Certified Cloud Practitioner",
    "AWS Certified Data Analytics"
]

COMMON_TARGET_TITLES = [
    "Data Analyst", "Data Engineer", "Data Scientist", "BI Analyst",
    "BI Developer", "ETL Developer", "Database Administrator", "DBA",
    "Reporting Analyst", "MIS Officer", "Data Operations", "Analytics Associate"
]

def extract_text_from_pdf(filepath: Path) -> str:
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(filepath))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        # Fallback to pdfplumber if pypdf has issues
        try:
            import pdfplumber
            with pdfplumber.open(str(filepath)) as pdf:
                for page in pdf.pages:
                    pt = page.extract_text()
                    if pt:
                        text += pt + "\n"
        except Exception:
            pass
    return text.strip()

def extract_text_from_docx(filepath: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(filepath))
        return "\n".join([p.text for p in doc.paragraphs if p.text]).strip()
    except Exception:
        return ""

def parse_resume_file(filepath: Path) -> Dict[str, Any]:
    ext = filepath.suffix.lower()
    raw_text = ""
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(filepath)
    else:
        try:
            raw_text = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            raw_text = ""

    return extract_profile_from_text(raw_text, filename=filepath.name)

def extract_profile_from_text(text: str, filename: str = None) -> Dict[str, Any]:
    if not text:
        return {
            "skills": [],
            "certifications": [],
            "target_titles": [],
            "degree": "",
            "raw_text": "",
            "filename": filename
        }

    lower_text = text.lower()

    # 1. Identify skills
    detected_skills = []
    for skill in COMMON_DATA_SKILLS:
        pattern = rf"(?:\b|_){re.escape(skill.lower())}(?:\b|_)"
        if re.search(pattern, lower_text):
            detected_skills.append(skill)

    # 2. Identify certifications
    detected_certs = []
    for cert in COMMON_CERTIFICATIONS:
        if cert.lower() in lower_text:
            detected_certs.append(cert)

    # 3. Identify target titles / roles mentioned or desired
    detected_titles = []
    for title in COMMON_TARGET_TITLES:
        pattern = rf"\b{re.escape(title.lower())}\b"
        if re.search(pattern, lower_text):
            detected_titles.append(title)

    # 4. Degree detection
    degree = "BSc Computer Systems Engineering"
    if "computer systems engineering" in lower_text:
        degree = "BSc Computer Systems Engineering"
    elif "computer science" in lower_text:
        degree = "BS Computer Science"
    elif "software engineering" in lower_text:
        degree = "BS Software Engineering"
    elif "data science" in lower_text:
        degree = "BS Data Science"

    return {
        "skills": detected_skills or ["SQL", "Power BI", "Excel", "Python", "MySQL"],
        "certifications": detected_certs or ["Google Data Analytics Certificate"],
        "target_titles": detected_titles or ["Data Analyst", "Data Engineer", "BI Developer"],
        "degree": degree,
        "raw_text": text[:5000],
        "filename": filename
    }
