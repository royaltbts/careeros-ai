from agents import AgentsException
from openai import OpenAIError
from agents import Runner

from app.agent_nodes.profile_agent import profile_agent
from app.candidate_finding import build_candidate_finding
from app.candidate_finding_validator import validate_candidate_finding


def build_candidate_finding_with_provider(
    candidate,
    evidence,
    provider: str = "mock",
):
    provider = provider.strip().lower()

    if provider == "mock":
        finding = build_candidate_finding(
            candidate,
            evidence,
        )
        return validate_candidate_finding(
            finding,
            evidence,
        )

    if provider != "openai":
        raise ValueError(
            "Unsupported candidate provider: "
            f"{provider}. Use 'mock' or 'openai'."
        )

    prompt = f"""
Analyze the verified candidate profile and evidence library.

Candidate profile:
{candidate.model_dump_json(indent=2)}

Evidence library:
[
{chr(10).join(
    item.model_dump_json()
    for item in evidence
)}
]

Return a CandidateFinding.

Truth rules:
- Use only verified evidence.
- Never fabricate SaaS experience.
- Never fabricate CRM expertise.
- Never fabricate enterprise account ownership.
- Distinguish direct experience from transferable experience.
- Do not invent metrics.
"""

    try:
        result = Runner.run_sync(
            profile_agent,
            prompt,
        )
    except (AgentsException, OpenAIError):
        return build_candidate_finding(
            candidate,
            evidence,
        )

    return validate_candidate_finding(
        result.final_output,
        evidence,
    )
