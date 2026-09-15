import json
from pathlib import Path

from app.models.candidate import CandidateProfile
from app.models.evidence import EvidenceItem
from app.models.career_strategy import CareerStrategy
from app.models.job import Job
from app.models.job_intelligence import JobIntelligence
from app.models.company_intelligence import CompanyIntelligence

from app.scoring import calculate_fit
from app.opportunity_scorer import calculate_opportunity_score


INTELLIGENCE_DIR = Path("data/jobs/intelligence")
COMPANY_INTELLIGENCE_DIR = Path("data/jobs/company_intelligence")
OUTPUT_FILE = Path("data/jobs/ranked_opportunities.json")


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_candidate() -> CandidateProfile:
    return CandidateProfile.model_validate(
        load_json("data/candidate/profile.json")
    )


def load_evidence() -> list[EvidenceItem]:
    data = load_json("data/evidence/evidence.json")

    return [
        EvidenceItem.model_validate(item)
        for item in data
    ]


def load_strategy() -> CareerStrategy:
    return CareerStrategy.model_validate(
        load_json("data/candidate/career_strategy.json")
    )


def load_intelligence_files() -> list[JobIntelligence]:

    files = sorted(
        INTELLIGENCE_DIR.glob("*.json")
    )

    return [
        JobIntelligence.model_validate(
            load_json(file_path)
        )
        for file_path in files
    ]


def load_company_intelligence(
    job_id: str
) -> CompanyIntelligence:
    path = COMPANY_INTELLIGENCE_DIR / f"{job_id}.json"
    return CompanyIntelligence.model_validate(
        load_json(str(path))
    )


def build_job(
    intelligence: JobIntelligence
) -> Job:

    return Job(
        job_id=intelligence.job_id,
        company=intelligence.company,
        title=intelligence.title,
        location=intelligence.location,
        employment_type=intelligence.employment_type,
        description="",
        responsibilities=intelligence.responsibilities,
        requirements=intelligence.requirements,
        experience_required=intelligence.experience_required,
        industry=intelligence.industry,
        source_url=intelligence.source_url,
    )


def score_job(
    intelligence: JobIntelligence,
    candidate: CandidateProfile,
    evidence: list[EvidenceItem],
    strategy: CareerStrategy
):

    job = build_job(intelligence)

    fit_result = calculate_fit(
        job,
        candidate,
        evidence
    )

    company_intelligence = load_company_intelligence(
        job.job_id
    )
    opportunity_result = calculate_opportunity_score(
        job,
        strategy,
        fit_result,
        company_intelligence
    )

    return {
        "job_id": job.job_id,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "source_url": job.source_url,
        "fit_score": fit_result["overall_score"],
        "opportunity_score": opportunity_result[
            "opportunity_score"
        ],
        "priority": opportunity_result["priority"],
        "company_strategic_fit": opportunity_result.get(
            "company_strategic_fit"
        ),
        "critical_gaps": fit_result["critical_gaps"],
        "core_gaps": fit_result["core_gaps"],
    }


def save_ranked_opportunities(results: list[dict]):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "generated_at": "2026-09-13",
        "total_opportunities": len(results),
        "opportunities": results
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )


def main():

    candidate = load_candidate()
    evidence = load_evidence()
    strategy = load_strategy()
    intelligence_jobs = load_intelligence_files()

    results = []

    for intelligence in intelligence_jobs:

        result = score_job(
            intelligence,
            candidate,
            evidence,
            strategy
        )

        results.append(result)

    results.sort(
        key=lambda item: item["opportunity_score"],
        reverse=True
    )

    save_ranked_opportunities(results)

    print()
    print("=" * 80)
    print("CAREEROS BATCH OPPORTUNITY SCORER")
    print("=" * 80)

    print(
        f"Jobs analyzed: {len(results)}"
    )

    print()

    print(
        f"{'RANK':<6}"
        f"{'JOB':<10}"
        f"{'ROLE':<38}"
        f"{'FIT':<10}"
        f"{'OPPORTUNITY':<14}"
        f"PRIORITY"
    )

    print("-" * 80)

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{rank:<6}"
            f"{result['job_id']:<10}"
            f"{result['title'][:36]:<38}"
            f"{result['fit_score']:<10.2f}"
            f"{result['opportunity_score']:<14.2f}"
            f"{result['priority']}"
        )

    print()
    print(
        f"Saved ranking: {OUTPUT_FILE}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()
