import json

from app.models.candidate import CandidateProfile
from app.models.evidence import EvidenceItem
from app.models.career_strategy import CareerStrategy
from app.models.job import Job
from app.job_parser import load_job_intelligence
from app.scoring import calculate_fit
from app.opportunity_scorer import calculate_opportunity_score
from app.decision import make_application_decision


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_candidate_profile(path: str) -> CandidateProfile:
    return CandidateProfile.model_validate(load_json(path))


def load_evidence(path: str) -> list[EvidenceItem]:
    data = load_json(path)
    return [EvidenceItem.model_validate(item) for item in data]


def load_career_strategy(path: str) -> CareerStrategy:
    return CareerStrategy.model_validate(load_json(path))


def build_job_from_intelligence(job_intelligence):
    return Job(
        job_id=job_intelligence.job_id,
        company=job_intelligence.company,
        title=job_intelligence.title,
        location=job_intelligence.location,
        employment_type=job_intelligence.employment_type,
        description="",
        responsibilities=job_intelligence.responsibilities,
        requirements=job_intelligence.requirements,
        experience_required=job_intelligence.experience_required,
        industry=job_intelligence.industry,
        source_url=job_intelligence.source_url,
    )


def run_pipeline():

    # 1. Candidate Truth Profile
    candidate = load_candidate_profile(
        "data/candidate/profile.json"
    )

    # 2. Verified Evidence Library
    evidence = load_evidence(
        "data/evidence/evidence.json"
    )

    # 3. Career Strategy
    career_strategy = load_career_strategy(
        "data/candidate/career_strategy.json"
    )

    # 4. Job Intelligence
    job_intelligence = load_job_intelligence(
        "data/job_intelligence_test.json"
    )

    # 5. Convert Job Intelligence to Job
    job = build_job_from_intelligence(
        job_intelligence
    )

    # 6. Candidate Fit
    fit_result = calculate_fit(
        job,
        candidate,
        evidence
    )

    # 7. Strategic Opportunity Score
    opportunity_result = calculate_opportunity_score(
        job,
        career_strategy,
        fit_result
    )

    # 8. Application Decision
    decision_result = make_application_decision(
        job,
        fit_result
    )

    # ---------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("CAREEROS OPPORTUNITY PIPELINE")
    print("=" * 70)

    print(f"Company: {job.company}")
    print(f"Role: {job.title}")

    print(
        f"Candidate Fit: "
        f"{fit_result['overall_score']:.2f}"
    )

    print(
        f"Opportunity Score: "
        f"{opportunity_result['opportunity_score']:.2f}"
    )

    print(
        f"Priority: "
        f"{opportunity_result['priority']}"
    )

    print(
        f"Application Decision: "
        f"{decision_result['decision']['apply']}"
    )

    print(
        f"Networking: "
        f"{decision_result['strategy']['networking']}"
    )

    print(
        f"Human Approval: "
        f"{decision_result['human_approval']}"
    )

    print()

    print("Critical Gaps:")

    if fit_result["critical_gaps"]:
        for gap in fit_result["critical_gaps"]:
            print(f"  - {gap}")
    else:
        print("  None")

    print()

    print("Core Gaps:")

    if fit_result["core_gaps"]:
        for gap in fit_result["core_gaps"]:
            print(f"  - {gap}")
    else:
        print("  None")

    print()

    print("Evidence Confidence:")

    for level, count in decision_result["confidence"].items():
        print(f"  {level}: {count}")

    print()

    print("Requirement Analysis:")

    for requirement in decision_result["requirement_analysis"]:
        print(
            f"  - {requirement['requirement']}: "
            f"{requirement['match_type']} "
            f"({requirement['evidence_confidence']})"
        )

    print()
    print("=" * 70)

    return {
        "job": job,
        "fit": fit_result,
        "opportunity": opportunity_result,
        "decision": decision_result,
    }


if __name__ == "__main__":
    run_pipeline()
