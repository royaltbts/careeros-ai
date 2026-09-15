import json
from pathlib import Path

from app.models.execution_authorization import ExecutionAuthorization


BASE_DIR = Path(__file__).resolve().parent.parent

EXECUTION_AUTHORIZATION_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "execution_authorizations"
)


def get_execution_authorization_file(job_id: str) -> Path:
    return EXECUTION_AUTHORIZATION_DIR / f"{job_id}.json"


def save_execution_authorization(
    authorization: ExecutionAuthorization,
) -> Path:
    EXECUTION_AUTHORIZATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_execution_authorization_file(
        authorization.job_id
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            authorization.model_dump(mode="json"),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


def load_execution_authorization(
    job_id: str,
) -> ExecutionAuthorization | None:
    file_path = get_execution_authorization_file(job_id)

    if not file_path.exists():
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return ExecutionAuthorization.model_validate(data)
