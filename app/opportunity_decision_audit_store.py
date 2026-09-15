import json
from pathlib import Path

from app.models.opportunity_decision_audit import (
    OpportunityDecisionAudit,
)


BASE_DIR = Path(__file__).resolve().parent.parent

OPPORTUNITY_DECISION_AUDIT_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "opportunity_decision_audit"
)


def get_opportunity_decision_audit_file(
    job_id: str,
) -> Path:
    return (
        OPPORTUNITY_DECISION_AUDIT_DIR
        / f"{job_id}.json"
    )


def save_opportunity_decision_audit(
    audit: OpportunityDecisionAudit,
) -> Path:

    OPPORTUNITY_DECISION_AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_opportunity_decision_audit_file(
        audit.job_id
    )

    existing_records = []

    if output_file.exists():
        with open(
            output_file,
            "r",
            encoding="utf-8",
        ) as file:
            existing_records = json.load(file)

    if not isinstance(existing_records, list):
        existing_records = [existing_records]

    existing_records.append(
        audit.model_dump(mode="json")
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            existing_records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


def load_opportunity_decision_audit(
    job_id: str,
) -> list[OpportunityDecisionAudit]:

    file_path = get_opportunity_decision_audit_file(
        job_id
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "Opportunity decision audit not found: "
            f"{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        data = [data]

    return [
        OpportunityDecisionAudit.model_validate(
            item
        )
        for item in data
    ]
