import pytest
from app.services.matching import score_job_against_profile, DEFAULT_USER_SKILLS, DEFAULT_TARGET_TITLES

def test_trainee_and_internship_boost():
    title = "Management Trainee Officer - Data Analytics"
    desc = """
    We are hiring fresh graduates for our accelerated Trainee Program.
    No prior experience required — our team will teach and train you on the modern data stack.
    You will learn SQL, Power BI, and Python (Pandas) under experienced mentors.
    Eligibility: Fresh BSc Computer Systems Engineering or CS graduates.
    """
    score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
        job_title=title,
        job_description=desc,
        user_skills=DEFAULT_USER_SKILLS,
        target_titles=DEFAULT_TARGET_TITLES
    )
    assert exp_level == "TRAINEE"
    assert is_zero_exp is True
    assert training_provided is True
    assert score >= 85
    assert breakdown["experience_score"] >= 30

def test_internship_boost():
    title = "Paid Data Analyst Intern"
    desc = "Looking for an energetic Data Intern. Stipend provided. We will teach you SQL and Power BI."
    score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
        job_title=title,
        job_description=desc,
        user_skills=DEFAULT_USER_SKILLS,
        target_titles=DEFAULT_TARGET_TITLES
    )
    assert exp_level == "INTERNSHIP"
    assert is_zero_exp is True
    assert score >= 80

def test_senior_role_penalty():
    title = "Senior Lead Data Architect - 10+ years"
    desc = "Looking for Senior Lead Architect with 10+ years experience in Enterprise Warehouses."
    score, matched_skills, missing_skills, breakdown, exp_level, is_zero_exp, training_provided = score_job_against_profile(
        job_title=title,
        job_description=desc,
        user_skills=DEFAULT_USER_SKILLS,
        target_titles=DEFAULT_TARGET_TITLES
    )
    assert exp_level == "EXPERIENCED"
    assert is_zero_exp is False
    assert breakdown["experience_score"] < 0
