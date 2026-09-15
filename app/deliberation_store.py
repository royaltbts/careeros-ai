import json
from pathlib import Path

from app.models.deliberation_record import DeliberationRecord


BASE_DIR = Path(__file__).resolve().parent.parent

DELIBERATION_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "deliberations"
)


def get_deliberation_file(
    job_id: str,
) -> Path:
    return (
        DELIBERATION_DIR
        / f"{job_id}.json"
    )


def save_deliberation(
    record: DeliberationRecord,
) -> Path:
    DELIBERATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_deliberation_file(
        record.job_id
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
        record.model_dump(mode="json")
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


def load_deliberations(
    job_id: str,
) -> list[DeliberationRecord]:
    file_path = get_deliberation_file(
        job_id
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "Deliberation history not found: "
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
        DeliberationRecord.model_validate(item)
        for item in data
    ]
