from app.models.candidate import CandidateProfile
from app.models.candidate_finding import CandidateFinding
from app.models.evidence import EvidenceItem


def build_candidate_finding(
    candidate: CandidateProfile,
    evidence: list[EvidenceItem],
) -> CandidateFinding:
    verified_evidence_refs = [
        item.id
        for item in evidence
        if item.status == "VERIFIED"
    ]

    transferable_experience = []

    if candidate.experience.people_management:
        transferable_experience.append(
            "People management transferable to Customer Success leadership."
        )

    if candidate.experience.project_management:
        transferable_experience.append(
            "Project management transferable to Customer Success."
        )

    if candidate.experience.lean_six_sigma:
        transferable_experience.append(
            "Lean Six Sigma transferable to Customer Success process improvement."
        )

    explicit_gaps = [
        "Formal SaaS experience",
        "CRM expertise",
        "Enterprise account ownership",
    ]

    forbidden_assumptions = [
        "SaaS experience",
        "CRM expertise",
        "Enterprise account ownership",
    ]

    return CandidateFinding(
        strengths=candidate.strengths,
        transferable_experience=transferable_experience,
        verified_evidence_refs=verified_evidence_refs,
        explicit_gaps=explicit_gaps,
        forbidden_assumptions=forbidden_assumptions,
        recommendation="APPLY",
        confidence=0.90,
    )
