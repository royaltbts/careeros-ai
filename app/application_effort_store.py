import json
from pathlib import Path

from app.models.application_effort import ApplicationEffort


BASE_DIR = Path(__file__).resolve().parent.parent

APPLICATION_EFFORT_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "application_effort"
)


def get_application_effort_file(job_id: str) -> Path:
    return (
        APPLICATION_EFFORT_DIR
        / f"{job_id}.json"
    )


def save_application_effort(
    effort: ApplicationEffort,
) -> Path:
    APPLICATION_EFFORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_application_effort_file(
        effort.job_id
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            effort.model_dump(mode="json"),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


def load_application_effort(
    job_id: str,
) -> ApplicationEffort:

    file_path = get_application_effort_file(
        job_id
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Application effort not found: "
            f"{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return ApplicationEffort.model_validate(data)
