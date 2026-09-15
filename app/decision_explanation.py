import json
from pathlib import Path

from app.models.decision_explanation import (
    DecisionExplanation,
    DecisionEvidenceItem,
)

from app.claim_safety import run_safety_gate


BASE_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_FILE = BASE_DIR / "data" / "evidence" / "evidence.json"


def load_evidence_library() -> dict:
    data = json.loads(
        EVIDENCE_FILE.read_text(encoding="utf-8")
    )

    return {
        item["id"]: item
        for item in data
    }


def explain_requirement(
    job_id: str,
    requirement: dict,
    evidence_library: dict,
) -> DecisionEvidenceItem:
    evidence_ids = requirement.get("evidence_ids", [])

    matched_evidence = [
        evidence_library[evidence_id]
        for evidence_id in evidence_ids
        if evidence_id in evidence_library
    ]

    evidence_claims = [
        item["claim"]
        for item in matched_evidence
    ]

    evidence_types = [
        item["evidence_type"]
        for item in matched_evidence
    ]

    match_type = requirement["match_type"]

    if match_type == "DIRECT":
        explanation = (
            f"{', '.join(evidence_ids) or 'No evidence'} "
            "directly supports this requirement."
        )
    elif match_type == "TRANSFERABLE":
        explanation = (
            f"{', '.join(evidence_ids) or 'No evidence'} "
            "provides transferable support for this requirement."
        )
    else:
        explanation = (
            "No verified evidence supports this requirement."
        )

    safety_allowed = False

    if evidence_ids and matched_evidence:
        safety_result = run_safety_gate(
            job_id,
            [
                {
                    "claim": item["claim"],
                    "evidence_ids": [item["id"]],
                }
                for item in matched_evidence
            ],
        )

        safety_allowed = all(
            check.allowed
            for check in safety_result.checks
        )

    allowed = safety_allowed

    return DecisionEvidenceItem(
        requirement=requirement["requirement"],
        criticality=requirement["criticality"],
        category=requirement["category"],
        match_type=match_type,
        confidence=requirement["confidence"],
        evidence_ids=evidence_ids,
        evidence_claims=evidence_claims,
        evidence_types=evidence_types,
        allowed=allowed,
        explanation=explanation,
    )


def build_decision_explanation(
    opportunity: dict,
) -> DecisionExplanation:

    evidence_library = load_evidence_library()

    evidence_items = [
        explain_requirement(
            opportunity["job_id"],
            requirement,
            evidence_library,
        )
        for requirement in opportunity.get(
            "requirement_analysis",
            [],
        )
    ]

    direct_count = sum(
        item.match_type == "DIRECT"
        for item in evidence_items
    )

    transferable_count = sum(
        item.match_type == "TRANSFERABLE"
        for item in evidence_items
    )

    missing_count = sum(
        item.match_type == "MISSING"
        for item in evidence_items
    )

    if missing_count == 0 and transferable_count == 0:
        confidence_summary = (
            "Strong evidence-backed fit with direct "
            "verified evidence for the analyzed requirements."
        )
    elif missing_count == 0:
        confidence_summary = (
            f"Evidence-backed fit with {direct_count} "
            f"direct and {transferable_count} transferable "
            "matches."
        )
    else:
        confidence_summary = (
            f"Mixed evidence profile with {direct_count} "
            f"direct, {transferable_count} transferable, "
            f"and {missing_count} missing requirements."
        )

    strategic_fit = (
        opportunity.get("company_strategic_fit")
        or {}
    )

    company_alignment = strategic_fit.get(
        "strategic_alignment"
    )

    if company_alignment is not None:
        if company_alignment >= 75:
            confidence_summary += (
                " Company context shows strong strategic alignment."
            )
        elif company_alignment >= 50:
            confidence_summary += (
                " Company context shows moderate strategic alignment."
            )

    transferable_opportunities = list(
        opportunity.get("core_gaps", [])
    )

    return DecisionExplanation(
        job_id=opportunity["job_id"],
        company=opportunity["company"],
        title=opportunity["title"],
        opportunity_score=opportunity["opportunity_score"],
        priority=opportunity["priority"],
        recommendation=opportunity.get(
            "recommendation",
            "REVIEW",
        ),
        strengths=opportunity.get(
            "strengths",
            [],
        ),
        evidence_items=evidence_items,
        critical_gaps=opportunity.get(
            "critical_gaps",
            [],
        ),
        transferable_opportunities=(
            transferable_opportunities
        ),
        confidence_summary=confidence_summary,
        human_review_required=True,
    )


def build_decision_explanation_for_job(
    job_id: str,
) -> DecisionExplanation:
    from app.careeros import build_job_from_intelligence
    from app.models.candidate import CandidateProfile
    from app.models.evidence import EvidenceItem
    from app.models.job_intelligence import JobIntelligence
    from app.opportunity_decision_store import (
        load_opportunity_decision,
    )
    from app.scoring import calculate_fit

    job_intelligence_file = (
        BASE_DIR
        / "data"
        / "jobs"
        / "intelligence"
        / f"{job_id}.json"
    )

    candidate_file = (
        BASE_DIR
        / "data"
        / "candidate"
        / "profile.json"
    )

    if not job_intelligence_file.exists():
        raise FileNotFoundError(
            f"Job intelligence not found: {job_intelligence_file}"
        )

    job_intelligence = JobIntelligence.model_validate(
        json.loads(
            job_intelligence_file.read_text(
                encoding="utf-8"
            )
        )
    )

    job = build_job_from_intelligence(
        job_intelligence
    )

    candidate = CandidateProfile.model_validate(
        json.loads(
            candidate_file.read_text(
                encoding="utf-8"
            )
        )
    )

    evidence = [
        EvidenceItem.model_validate(item)
        for item in json.loads(
            EVIDENCE_FILE.read_text(
                encoding="utf-8"
            )
        )
    ]

    fit_result = calculate_fit(
        job,
        candidate,
        evidence,
    )

    decision = load_opportunity_decision(
        job_id
    )

    opportunity = {
        "job_id": decision.job_id,
        "company": decision.company,
        "title": decision.title,
        "opportunity_score": decision.opportunity_score,
        "priority": decision.priority,
        "recommendation": decision.recommendation,
        "strengths": decision.strengths,
        "critical_gaps": decision.critical_gaps,
        "core_gaps": decision.transferable_opportunities,
        "requirement_analysis": fit_result[
            "requirement_analysis"
        ],
        "company_strategic_fit": {
            "strategic_alignment":
                decision.company_strategic_alignment,
            "research_confidence":
                decision.company_research_confidence,
            "decision_ready_fit":
                decision.company_decision_ready_fit,
        },
    }

    return build_decision_explanation(
        opportunity
    )
