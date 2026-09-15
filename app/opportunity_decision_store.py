import json
from pathlib import Path

from app.models.opportunity_decision import OpportunityDecision


BASE_DIR = Path(__file__).resolve().parent.parent

OPPORTUNITY_DECISION_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "opportunity_decisions"
)


def get_opportunity_decision_file(
    job_id: str,
) -> Path:
    return (
        OPPORTUNITY_DECISION_DIR
        / f"{job_id}.json"
    )


def save_opportunity_decision(
    decision: OpportunityDecision,
) -> Path:
    OPPORTUNITY_DECISION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_opportunity_decision_file(
        decision.job_id
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            decision.model_dump(mode="json"),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


def load_opportunity_decision(
    job_id: str,
) -> OpportunityDecision:

    file_path = get_opportunity_decision_file(
        job_id
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Opportunity decision not found: "
            f"{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return OpportunityDecision.model_validate(
        data
    )
