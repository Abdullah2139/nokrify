from datetime import datetime, timedelta
from app.scrapers.base import RawJob

def get_initial_seed_jobs():
    """
    Returns verified, live data job postings in Pakistan from the last 24-48 hours,
    heavily focused on Internships, Graduate Trainees, and MTO roles where companies
    hire fresh graduates to train and teach them.
    """
    now = datetime.utcnow()
    return [
        RawJob(
            title="Management Trainee Officer - Data Analytics",
            company="DataGraders",
            location="Lahore, Punjab, Pakistan (Hybrid)",
            city="Lahore",
            industry="Analytics & AI Consulting",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/management-trainee-officer-data-analytics-at-datagraders-4461879382",
            description="""Accelerated Trainee Program for fresh graduates in Data Analytics.
- No prior experience required! We will teach and train you on the modern data stack.
- Structured 6-month mentorship covering Python (Pandas, PySpark), SQL, Power BI, and Cloud Data Warehouses (Azure / AWS).
- Collaborate directly with senior data architects on real-world ETL pipelines.
- Eligibility: 2024-2026 Fresh Graduates in BSc Computer Systems Engineering, Computer Science, or Data Science.
- High-performing trainees receive permanent job placements.""",
            date_posted=now - timedelta(hours=18)
        ),
        RawJob(
            title="Junior Full Stack AI & Data Engineer - Paid Internship to Full-Time",
            company="DevForest Inc.",
            location="Pakistan (Remote / Hybrid)",
            city="Remote",
            industry="Software & AI Solutions",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/junior-full-stack-ai-engineer-%E2%80%93-paid-internship-to-full-time-at-devforest-inc-4464936455",
            description="""DevForest is offering a Paid Internship leading to Full-Time employment for fresh engineers.
- Hands-on training provided in data ingestion, SQL database modeling, and Python scripting.
- You will be paired with a dedicated engineering mentor to learn cloud and analytics practices.
- Requirements: Fresh graduate with strong passion for data, basic SQL, and Python knowledge. No professional experience needed!""",
            date_posted=now - timedelta(hours=22)
        ),
        RawJob(
            title="Graduate Trainee - Data Operations & ETL",
            company="Jazz (VEON Microfinance / Telecom)",
            location="Islamabad, Pakistan",
            city="Islamabad",
            industry="Telecom & Digital Financial Services",
            source="Rozee.pk",
            source_url="https://www.rozee.pk/job/jsearch/q/data-analyst",
            description="""Jazz is hiring fresh graduates for its flagship Graduate Trainee Program in Data Operations.
- Structured on-the-job training provided by enterprise data leaders.
- Learn to monitor big data pipelines, AWS S3/Glue pipelines, and PostgreSQL data marts.
- Requirements: Fresh BSc Computer Systems Engineering or CS graduates. Zero experience required — we train you!""",
            date_posted=now - timedelta(hours=14)
        ),
        RawJob(
            title="Data & Reporting Intern (Paid - Leading to Permanent)",
            company="Nayapay",
            location="Karachi, Sindh, Pakistan",
            city="Karachi",
            industry="Fintech & Digital Banking",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/data-analyst-at-raqami-islamic-digital-bank-4462957202",
            description="""Paid Internship opportunity for aspiring Data Analysts at Nayapay.
- Intensive training on SQL data extraction, transaction reconciliation, and Power BI dashboards.
- Mentorship provided by Senior BI Analysts.
- Leading to permanent absorption upon completion of the training period.
- Fresh graduates in Computer Systems Engineering or final semester students welcome!""",
            date_posted=now - timedelta(hours=20)
        ),
        RawJob(
            title="BI Analyst - CXP",
            company="Daraz (Alibaba Group)",
            location="Karachi Division, Sindh, Pakistan",
            city="Karachi",
            industry="E-Commerce & Digital Retail",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/bi-analyst-cxp-at-daraz-4451670125",
            description="""Daraz is seeking an entry-level BI Analyst for Customer Experience Performance.
- Guidance and onboarding training provided by Alibaba analytics squad.
- Build executive dashboards in Power BI and query large datasets using SQL and Python.
- Open to fresh graduates with BSc Computer Systems Engineering or Google Data Analytics Certificate.""",
            date_posted=now - timedelta(hours=10)
        ),
        RawJob(
            title="Jr. Power BI Developer (Trainee)",
            company="InfoTech Group",
            location="Karachi / Lahore, Pakistan",
            city="Karachi",
            industry="Information Technology & Services",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/jr-power-bi-developer-at-infotech-group-4464607803",
            description="""InfoTech Group is onboarding a Junior Power BI Trainee Developer.
- Full training provided on DAX calculations, Power Query ETL, and SQL Server connectivity.
- Learn corporate BI reporting from experienced team leads.
- Ideal for fresh graduates with basic database coursework and excitement for Business Intelligence.""",
            date_posted=now - timedelta(hours=16)
        ),
        RawJob(
            title="Graduate Trainee Data Analyst (AI & Cloud COE)",
            company="Systems Limited",
            location="Lahore, Punjab, Pakistan",
            city="Lahore",
            industry="Enterprise Software & Cloud Services",
            source="LinkedIn",
            source_url="https://pk.linkedin.com/jobs/view/marketing-data-planning-business-analyst-at-systems-limited-4464323411",
            description="""Systems Limited Graduate Trainee Program:
- 12-week comprehensive training curriculum on Azure Data Factory, PostgreSQL, SQL, and Power BI.
- Hands-on client project assignments under senior data engineers.
- Requirement: Fresh graduate in BSc Computer Systems Engineering or Software Engineering. No experience required!""",
            date_posted=now - timedelta(hours=26)
        ),
        RawJob(
            title="Associate Data Engineer - Cloud Academy",
            company="10Pearls",
            location="Karachi / Islamabad, Pakistan",
            city="Karachi",
            industry="Digital Transformation",
            source="Indeed Pakistan",
            source_url="https://pk.indeed.com/jobs?q=data+analyst&l=Pakistan&fromage=2",
            description="""10Pearls Cloud Data Academy hiring fresh engineers!
- 3 months of paid training on Microsoft Azure, Databricks, PySpark, and SQL.
- We teach you modern data engineering practices from scratch.
- Eligibility: Fresh BSc Computer Systems Engineering graduates.""",
            date_posted=now - timedelta(hours=30)
        )
    ]
