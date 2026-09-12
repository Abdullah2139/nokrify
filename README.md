# 📡 Nokrify — Pakistan Data Jobs Radar

A modern, persistent web application and radar built specifically for fresh graduates in **BSc Computer Systems Engineering** to automatically monitor **any data-related role across Pakistan, listed within the last 48 hours**.

Aggregates directly from **LinkedIn Pakistan**, **Rozee.pk**, and **Indeed**, checks for cross-board duplicates, calculates fit scores against your specific engineering skill set, and provides a sleek dashboard with 100% real, verified, working application URLs.

---

## 🎯 Candidate Profile & Matching Model

Calibrated for your exact fresh graduate profile:
- **Degree**: BSc Computer Systems Engineering (Fresh Graduate, Pakistan)
- **Core Skills**: `SQL` (Complex queries, CTEs, Window functions), `Power BI` (DAX, Power Query), `Excel` (Pivot tables, Advanced formulas), `MySQL`, `PostgreSQL`, `Microsoft Azure` (`Azure Data Factory`, `ADLS Gen2`, `Azure SQL`), `AWS` (`S3`, `AWS Glue`), `Python` (`Pandas`, `PySpark`), `Git/GitHub`.
- **Certifications**: Google Data Analytics Certificate, IBM Data Analytics Professional Certificate.
- **Target Seed Roles**: Data Analyst, Data Engineer, Data Scientist, BI Analyst/Developer, ETL Developer, Database Administrator (DBA), Reporting Analyst, MIS Officer/Executive, Data Operations, Business Intelligence, Analytics Associate, Graduate Trainee.
- **Scope**: Open to all industries across Pakistan (Karachi, Lahore, Islamabad/Rawalpindi, Remote, etc.).

### Weighted Scoring Algorithm (0–100%):
1. **Core Skills Match (50 pts max)**: Scans for exact technical stack matches with boundary-safe phrase analysis.
2. **Target Role & Title Match (30 pts max)**: Checks job title against seed role keywords.
3. **Fresh Graduate / Seniority Fit (15 pts max)**: Rewards entry-level, fresh graduate, intern, trainee, and 0–2 year postings (+15 pts bonus); penalizes 5+ year senior roles.
4. **Degree & Engineering Fit (5 pts max)**: Validates alignment with Computer Systems Engineering, Computer Science, and IT degrees.

---

## ⚡ Key Upgrades & Capabilities

### 1. Direct LinkedIn Pakistan Integration (`app/scrapers/linkedin.py`)
- Leverages LinkedIn's public guest job search API with standard rotating headers.
- Enforces strict **48-hour freshness filtering** (`f_TPR=r172800`) to guarantee you only see active postings from today or yesterday.
- Extracts real, verified `https://pk.linkedin.com/jobs/view/...` URLs that open directly on LinkedIn.

### 2. Strict 48-Hour Freshness Controls
- **Default 48h Filter**: Only listings posted in the last 48 hours are shown by default.
- **Quick Age Horizon Toggle**: Switch with one click between `Last 24h`, `Last 48h`, `Past Week`, and `All Time`.
- Every posting displays an animated green freshness badge (e.g. `⚡ 10h ago`, `⚡ Yesterday`).

### 3. Beautiful High-End Web Interface
- **Modern Obsidian & Emerald Aesthetic**: Dark mode with radial glows, glassmorphism cards, and crisp typography.
- **Dynamic Company Avatars**: Distinct visual brand initials with gradient color palettes.
- **Match Score Gauges**: Glowing status pills displaying fit percentage and complete scoring breakdown on click.
- **Bento Stats Grid**: Live counters for 48h Fresh Roles, Top Fit (&ge;70%), LinkedIn Roles, Applied, Interviewing, and Active Sources.
- **One-Click Actions**: Quick status dropdown (`New`, `Viewed`, `Applied`, `Interviewing`, `Rejected`), "Copy Link" button with toast notification, and direct "Apply on Official Board" button.

### 4. Fuzzy Cross-Board Deduplication (`app/services/deduplication.py`)
- Merges duplicates when a company posts the same job across LinkedIn, Rozee, and Indeed.
- Displays a `Boards Merged` badge with all alternative links preserved in the details drawer.

### 5. Resume & Skill Profile Tuning Drawer (`app/services/resume_parser.py`)
- Upload an updated PDF or DOCX resume to extract new skills.
- Manually add or remove skills with instant live re-scoring of all 48h jobs in the database.

---

## 🚀 How to Run

### Windows (One-Click)
Double-click `run.bat` in the project root:
```cmd
run.bat
```

### Command Line
```bash
python run.py
```

Then navigate to:
```
http://localhost:8000
```

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```bash
python -m pytest -v
```
Verifies API endpoints, LinkedIn scraper, fuzzy deduplication, and matching engine scoring.
