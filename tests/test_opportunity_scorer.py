from app.models.career_strategy import CareerStrategy
from app.models.job import Job
from app.opportunity_scorer import (
    calculate_capability_alignment,
    calculate_critical_gap_penalty,
    calculate_opportunity_score,
    calculate_role_alignment,
)


def make_strategy():
    return CareerStrategy(
        primary_direction="Customer Success",
        target_roles=["Customer Success Manager"],
        preferred_seniority=["Manager"],
        geography="Any",
        priority_capabilities=[
            "Customer Success",
            "Customer relationship management",
            "Customer communication",
            "Business reviews",
        ],
        avoid_roles=[],
        strategy_notes=[],
    )


def make_job(title="Customer Success Manager", requirements=None):
    return Job(
        job_id="TEST-SCORE-001",
        company="Test Company",
        title=title,
        location="Hyderabad",
        description="Test job description",
        responsibilities=["Manage customer relationships"],
        requirements=requirements or [],
    )


def test_exact_target_role_has_full_alignment():
    strategy = make_strategy()
    job = make_job(requirements=[{"name": "Customer communication", "criticality": "CORE", "category": "CUSTOMER_SUCCESS"}, {"name": "Business reviews", "criticality": "CORE", "category": "CUSTOMER_SUCCESS"}])

    assert calculate_role_alignment(job, strategy) == 100.0


def test_capability_alignment_gives_full_credit_for_exact_match():
    strategy = make_strategy()
    job = make_job(
        requirements=[
            {"name": "Customer communication", "criticality": "CORE", "category": "CUSTOMER_SUCCESS"}
        ]
    )

    assert calculate_capability_alignment(job, strategy) == 100.0


def test_critical_gap_penalty_is_twenty_points_each():
    assert calculate_critical_gap_penalty(
        {"critical_gaps": ["Advanced SQL", "Snowflake"]}
    ) == 40.0


def test_high_opportunity_score_is_high_priority():
    strategy = make_strategy()
    job = make_job(requirements=[{"name": "Customer communication", "criticality": "CORE", "category": "CUSTOMER_SUCCESS"}, {"name": "Business reviews", "criticality": "CORE", "category": "CUSTOMER_SUCCESS"}])

    fit_result = {
        "overall_score": 90.0,
        "critical_gaps": [],
    }

    result = calculate_opportunity_score(
        job,
        strategy,
        fit_result,
    )

    assert result["priority"] == "HIGH"
    assert result["opportunity_score"] >= 75


def test_low_opportunity_score_is_low_priority():
    strategy = make_strategy()
    job = make_job(
        title="Technical Support Specialist",
        requirements=[],
    )

    fit_result = {
        "overall_score": 0.0,
        "critical_gaps": [],
    }

    result = calculate_opportunity_score(
        job,
        strategy,
        fit_result,
    )

    assert result["priority"] == "LOW"
    assert result["opportunity_score"] < 55
