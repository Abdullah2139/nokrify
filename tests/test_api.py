import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.scrapers.collector import collector

def test_api_suite():
    db = SessionLocal()
    collector.sync_source_configs(db)
    prof = collector.get_or_create_user_profile(db)
    collector.ensure_seed_benchmark_jobs(db, prof.skills, prof.target_titles)
    db.close()

    with TestClient(app) as client:
        # 1. Dashboard HTML
        res_dash = client.get("/")
        assert res_dash.status_code == 200
        assert "Nokrify" in res_dash.text
        assert "TRAINEE &amp; ZERO-EXP RADAR" in res_dash.text

        # 2. Stats with intern_trainee_count
        res_stats = client.get("/api/stats")
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert stats["total_jobs"] >= 5
        assert stats["fresh_jobs_48h"] >= 1
        assert stats["high_matches"] >= 1
        assert stats["intern_trainee_count"] >= 1

        # 3. Jobs list with zero_exp_only filter
        res_zero = client.get("/api/jobs?zero_exp_only=true&limit=10")
        assert res_zero.status_code == 200
        zero_jobs = res_zero.json()
        assert len(zero_jobs) > 0
        for j in zero_jobs:
            assert j["is_zero_experience"] is True or j["experience_level"] in ["INTERNSHIP", "TRAINEE", "FRESH_GRAD"]

        # 4. Status update
        job_id = zero_jobs[0]["id"]
        res_update = client.patch(f"/api/jobs/{job_id}/status", json={"status": "APPLIED"})
        assert res_update.status_code == 200
        assert res_update.json()["status"] == "APPLIED"

        # 5. User profile
        res_prof = client.get("/api/profile")
        assert res_prof.status_code == 200
        p_data = res_prof.json()
        assert "BSc Computer Systems Engineering" in p_data["degree"]
        assert "SQL" in p_data["skills"]

        # 6. Sources list
        res_src = client.get("/api/sources")
        assert res_src.status_code == 200
        srcs = res_src.json()
        assert any(s["name"] == "linkedin" for s in srcs)
