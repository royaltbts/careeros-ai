import json
from pathlib import Path

from app.models.supervisor_decision import SupervisorDecision


BASE_DIR = Path(__file__).resolve().parent.parent

SUPERVISOR_DECISION_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "supervisor_decisions"
)


def get_supervisor_decision_file(
    job_id: str,
) -> Path:
    return (
        SUPERVISOR_DECISION_DIR
        / f"{job_id}.json"
    )


def save_supervisor_decision(
    decision: SupervisorDecision,
) -> Path:
    SUPERVISOR_DECISION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_supervisor_decision_file(
        decision.job_id
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
        decision.model_dump(mode="json")
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


def load_supervisor_decisions(
    job_id: str,
) -> list[SupervisorDecision]:
    file_path = get_supervisor_decision_file(
        job_id
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "Supervisor decision not found: "
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
        SupervisorDecision.model_validate(item)
        for item in data
    ]
