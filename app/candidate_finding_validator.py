from app.models.candidate import CandidateProfile
from app.models.candidate_finding import CandidateFinding
from app.models.evidence import EvidenceItem


def validate_candidate_finding(
    finding: CandidateFinding,
    evidence: list[EvidenceItem],
    candidate: CandidateProfile | None = None,
) -> CandidateFinding:
    verified_ids = {
        item.id
        for item in evidence
        if item.status == "VERIFIED"
    }

    invalid_refs = set(finding.verified_evidence_refs) - verified_ids

    if invalid_refs:
        raise ValueError(
            "Candidate finding contains unverified evidence refs: "
            + ", ".join(sorted(invalid_refs))
        )

    if candidate is not None:
        excluded_skills = {
            skill.strip().lower()
            for skill in candidate.excluded_skills
        }

        invalid_strengths = {
            strength
            for strength in finding.strengths
            if strength.strip().lower() in excluded_skills
        }

        if invalid_strengths:
            raise ValueError(
                "Candidate finding claims excluded skills as strengths: "
                + ", ".join(sorted(invalid_strengths))
            )

    return finding
