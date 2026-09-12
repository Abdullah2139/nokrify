import re
from typing import List, Dict, Any, Tuple

DEFAULT_USER_SKILLS = [
    "SQL",
    "Power BI",
    "Excel",
    "MySQL",
    "PostgreSQL",
    "Microsoft Azure",
    "Azure Data Factory",
    "ADLS Gen2",
    "Azure SQL",
    "AWS",
    "S3",
    "AWS Glue",
    "Python",
    "Pandas",
    "PySpark",
    "Git",
    "GitHub",
    "Data Engineering",
    "ETL",
    "Data Warehousing",
    "Snowflake",
    "Databricks",
    "Apache Spark",
    "Kafka",
    "Airflow",
    "dbt",
    "MongoDB",
    "NoSQL",
    "Redis",
    "Elasticsearch",
    "Tableau",
    "Looker",
    "Data Modeling",
    "Database Design",
    "T-SQL",
    "PL/SQL",
    "SSIS",
    "SSRS",
    "Azure Synapse",
    "Google BigQuery",
    "Redshift"
]

DEFAULT_CERTIFICATIONS = [
    "Google Data Analytics Certificate",
    "IBM Data Analytics Professional Certificate",
    "Microsoft Azure Data Fundamentals (DP-900)",
    "Microsoft Azure Data Engineer Associate (DP-203)",
    "AWS Certified Data Analytics",
    "Snowflake SnowPro Core Certification",
    "Databricks Certified Data Engineer Associate",
    "Google Cloud Professional Data Engineer"
]

DEFAULT_TARGET_TITLES = [
    "Data Analyst Intern",
    "Data Trainee",
    "Management Trainee Data",
    "Graduate Trainee Data",
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "BI Analyst",
    "BI Developer",
    "ETL Developer",
    "Database Administrator",
    "DBA",
    "Reporting Analyst",
    "MIS Officer",
    "MIS Executive",
    "Data Intern",
    "Analytics Intern",
    "Data Operations",
    "Business Intelligence",
    "Analytics Associate",
    "Junior Data Analyst",
    "Junior Data Engineer",
    "Associate Data Engineer",
    "Data Engineering Intern",
    "Database Intern",
    "BI Intern",
    "ETL Intern",
    "SQL Developer",
    "SQL Intern",
    "Data Platform Intern",
    "Cloud Data Intern",
    "Azure Data Engineer",
    "AWS Data Engineer",
    "Big Data Engineer",
    "Data Warehouse Developer",
    "Analytics Engineer",
    "BI Engineer"
]

SKILL_ALIASES = {
    "sql": ["sql", "structured query language", "transact-sql", "t-sql", "pl/sql"],
    "power bi": ["power bi", "powerbi", "dax", "power query"],
    "excel": ["excel", "advanced excel", "ms excel", "spreadsheets", "pivot tables", "vlookup"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "microsoft azure": ["azure", "microsoft azure", "ms azure"],
    "azure data factory": ["azure data factory", "adf"],
    "adls gen2": ["adls", "adls gen2", "azure data lake"],
    "azure sql": ["azure sql", "azure sql database"],
    "aws": ["aws", "amazon web services"],
    "s3": ["s3", "amazon s3", "aws s3"],
    "aws glue": ["aws glue", "glue"],
    "python": ["python", "python3"],
    "pandas": ["pandas", "numpy/pandas"],
    "pyspark": ["pyspark", "spark", "apache spark"],
    "git": ["git", "github", "gitlab"],
    "github": ["github"],
    "data engineering": ["data engineering", "data engineer"],
    "etl": ["etl", "extract transform load", "data pipeline"],
    "data warehousing": ["data warehouse", "data warehousing", "dimensional modeling"],
    "snowflake": ["snowflake", "snowflake dw"],
    "databricks": ["databricks", "lakehouse"],
    "apache spark": ["spark", "pyspark", "apache spark"],
    "kafka": ["kafka", "apache kafka", "event streaming"],
    "airflow": ["airflow", "apache airflow", "dag"],
    "dbt": ["dbt", "data build tool"],
    "mongodb": ["mongodb", "mongo", "document db"],
    "nosql": ["nosql", "non-relational", "document store"],
    "redis": ["redis", "in-memory cache"],
    "elasticsearch": ["elasticsearch", "elastic search", "elk stack"],
    "tableau": ["tableau", "tableau desktop"],
    "looker": ["looker", "lookml"],
    "data modeling": ["data modeling", "dimensional modeling", "star schema"],
    "database design": ["database design", "schema design", "normalization"],
    "tsql": ["t-sql", "transact-sql", "mssql", "sql server"],
    "pl/sql": ["pl/sql", "oracle sql", "oracle database"],
    "ssis": ["ssis", "sql server integration services"],
    "ssrs": ["ssrs", "sql server reporting services"],
    "azure synapse": ["azure synapse", "synapse analytics", "synapse"],
    "google bigquery": ["bigquery", "google bigquery", "gcp bigquery"],
    "redshift": ["redshift", "aws redshift"]
}

INTERN_TERMS = [
    "intern", "internship", "internships", "summer intern", "co-op", "student intern"
]

TRAINEE_TERMS = [
    "trainee", "trainees", "management trainee", "graduate trainee", "mto", "gtp", "gte",
    "apprentice", "apprenticeship", "fellowship", "fellow", "academy",
    "bootcamp", "trainee officer", "trainee engineer", "graduate program"
]

ZERO_EXP_TERMS = [
    "no experience", "no experience required", "0 years", "0-1 year", "0-2 years",
    "fresh", "fresh graduate", "fresh graduates", "freshers", "entry level", "entry-level",
    "junior", "jr.", "associate", "leading to permanent", "leading to full time"
]

TRAINING_PROVIDED_TERMS = [
    "training provided", "will be trained", "we will teach", "teach", "train",
    "training", "mentorship", "mentor", "mentors", "mentored", "coaching",
    "structured training", "stipend", "learn modern data stack", "hands-on training",
    "grooming", "learn on the job"
]

SENIOR_PENALTY_TERMS = [
    "senior", "sr.", "sr ", "lead", "principal", "head of", "director", "manager",
    "3+ years", "4+ years", "5+ years", "6+ years", "7+ years", "8+ years", "10+ years"
]

EDUCATION_TERMS = [
    "computer systems", "computer science", "software engineering", "computer engineering",
    "information technology", "bs cs", "bsc", "bachelors in computer", "engineering degree",
    "data science", "statistics", "mathematics"
]

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.lower().strip()

def contains_term(term: str, text: str) -> bool:
    """Safely check if term exists as a word or distinct phrase."""
    pattern = rf"(?:\b|_){re.escape(term.lower())}(?:\b|_)"
    return bool(re.search(pattern, text.lower()))

def classify_experience_and_training(title: str, description: str) -> Tuple[str, bool, bool, int]:
    t_clean = clean_text(title)
    d_clean = clean_text(description)
    full = f"{t_clean} {d_clean}"

    is_intern = any(contains_term(term, t_clean) for term in INTERN_TERMS) or any(contains_term(term, d_clean) for term in INTERN_TERMS)
    is_trainee = any(contains_term(term, t_clean) for term in TRAINEE_TERMS) or any(contains_term(term, d_clean) for term in TRAINEE_TERMS)
    has_zero_exp = any(contains_term(term, full) for term in ZERO_EXP_TERMS)
    training_offered = any(contains_term(term, full) for term in TRAINING_PROVIDED_TERMS)
    is_senior = any(contains_term(term, t_clean) for term in SENIOR_PENALTY_TERMS) or any(contains_term(term, d_clean) for term in SENIOR_PENALTY_TERMS[:5])

    bonus = 0
    if is_intern:
        exp_level = "INTERNSHIP"
        is_zero_exp = True
        bonus = 30
    elif is_trainee:
        exp_level = "TRAINEE"
        is_zero_exp = True
        bonus = 30
    elif has_zero_exp:
        exp_level = "FRESH_GRAD"
        is_zero_exp = True
        bonus = 20
    elif is_senior:
        exp_level = "EXPERIENCED"
        is_zero_exp = False
        bonus = -25
    else:
        exp_level = "ENTRY_LEVEL"
        is_zero_exp = True
        bonus = 10

    if training_offered:
        bonus += 10

    return exp_level, is_zero_exp, training_offered, bonus

def score_job_against_profile(
    job_title: str,
    job_description: str,
    user_skills: List[str] = None,
    target_titles: List[str] = None
) -> Tuple[int, List[str], List[str], Dict[str, Any], str, bool, bool]:
    if user_skills is None:
        user_skills = DEFAULT_USER_SKILLS
    if target_titles is None:
        target_titles = DEFAULT_TARGET_TITLES

    title_clean = clean_text(job_title)
    desc_clean = clean_text(job_description)
    full_text = f"{title_clean} {desc_clean}"

    exp_level, is_zero_exp, training_provided, exp_score = classify_experience_and_training(job_title, job_description)

    # 1. Skill Matching (Weight: 40 max points)
    matched_skills = []
    missing_skills = []
    for skill in user_skills:
        skill_lower = skill.lower()
        aliases = SKILL_ALIASES.get(skill_lower, [skill_lower])
        matched = False
        for alias in aliases:
            if contains_term(alias, full_text):
                matched_skills.append(skill)
                matched = True
                break
        if not matched:
            missing_skills.append(skill)

    matched_unique = list(dict.fromkeys(matched_skills))
    # For internships/trainees, require fewer skills since they're learning on the job
    required_skills = 2 if (exp_level in ["INTERNSHIP", "TRAINEE"]) else 4
    skill_ratio = min(len(matched_unique) / float(required_skills), 1.0)
    skill_score = round(skill_ratio * 40)

    # 2. Target Title / Role Fit (Weight: 30 max points)
    title_score = 0
    title_matched_role = None
    for role in target_titles:
        role_lower = role.lower()
        if contains_term(role_lower, title_clean):
            title_score = 30
            title_matched_role = role
            break
        elif any(part in title_clean for part in role_lower.split() if len(part) > 3):
            title_score = max(title_score, 20)
            title_matched_role = role

    if title_score == 0:
        if exp_level in ["INTERNSHIP", "TRAINEE"] and any(term in full_text for term in ["data", "analytics", "bi", "sql"]):
            title_score = 25
            title_matched_role = f"{exp_level.capitalize()} (Data Track)"
        else:
            for role in target_titles[:5]:
                if contains_term(role.lower(), desc_clean):
                    title_score = 15
                    title_matched_role = f"{role} (in description)"
                    break

    # 3. Education & Degree Alignment (Weight: 5 max points)
    edu_score = 0
    if any(contains_term(term, desc_clean) for term in EDUCATION_TERMS):
        edu_score = 5

    raw_score = skill_score + title_score + max(exp_score, 0) + edu_score
    if exp_score < 0:
        raw_score += exp_score
    total_score = min(max(raw_score, 0), 100)

    breakdown = {
        "skill_score": skill_score,
        "title_score": title_score,
        "experience_score": exp_score,
        "education_score": edu_score,
        "experience_level": exp_level,
        "is_zero_experience": is_zero_exp,
        "training_provided": training_provided,
        "title_matched_role": title_matched_role,
        "total_skills_matched": len(matched_unique)
    }

    return total_score, matched_unique, missing_skills, breakdown, exp_level, is_zero_exp, training_provided
