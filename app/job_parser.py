import json

from app.models.job_intelligence import JobIntelligence


def load_job_intelligence(path: str) -> JobIntelligence:
    """
    Load an already-structured job intelligence record.

    This local parser is intentionally deterministic.
    It does not use an LLM or external API.
    """

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return JobIntelligence.model_validate(data)
