import pytest
from app.services.deduplication import is_duplicate_job, normalize_text, normalize_company, normalize_city

def test_exact_and_fuzzy_duplicates():
    # Same job posted with slight differences on Rozee vs Indeed
    t1 = "Junior Data Analyst - Business Intelligence"
    c1 = "Systems Limited Pakistan"
    loc1 = "Lahore, Punjab"

    t2 = "Junior Data Analyst (BI)"
    c2 = "Systems Ltd"
    loc2 = "Lahore"

    assert is_duplicate_job(t1, c1, loc1, t2, c2, loc2) is True

def test_different_companies_not_duplicate():
    t1 = "Data Analyst"
    c1 = "Jazz Pakistan"
    loc1 = "Islamabad"

    t2 = "Data Analyst"
    c2 = "Telenor Pakistan"
    loc2 = "Islamabad"

    assert is_duplicate_job(t1, c1, loc1, t2, c2, loc2) is False

def test_normalization():
    assert normalize_city("Karachi, Sindh, Pakistan") == "karachi"
    assert normalize_city("Islamabad Capital Territory") == "islamabad/rawalpindi"
    assert normalize_company("Systems Limited Pvt Ltd") == "systems"
