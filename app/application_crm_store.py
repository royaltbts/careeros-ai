import json
from pathlib import Path

from app.models.application_record import ApplicationRecord


CRM_DIR = Path("data/jobs/applications/crm")


def save_application_record(
    record: ApplicationRecord,
) -> Path:
    """
    Persist an ApplicationRecord as JSON.
    """

    CRM_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = CRM_DIR / f"{record.job_id}.json"

    with open(path, "w") as f:
        json.dump(
            record.model_dump(mode="json"),
            f,
            indent=2,
        )

    return path


def load_application_record(
    job_id: str,
) -> ApplicationRecord:
    """
    Load a persisted ApplicationRecord.
    """

    path = CRM_DIR / f"{job_id}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"No CRM record found for {job_id}"
        )

    with open(path, "r") as f:
        data = json.load(f)

    return ApplicationRecord.model_validate(data)
