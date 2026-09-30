from app.models.candidate_finding import CandidateFinding
from app.models.evidence import EvidenceItem


def validate_candidate_finding(
    finding: CandidateFinding,
    evidence: list[EvidenceItem],
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

    return finding
