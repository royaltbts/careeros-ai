from app.models.job import Job
from app.models.candidate import CandidateProfile
from app.models.evidence import EvidenceItem


CRITICALITY_WEIGHT = {
    "CRITICAL": 3,
    "CORE": 2,
    "PREFERRED": 1,
}


def normalize(value: str) -> str:
    return value.strip().lower()


def classify_requirement(requirement_name: str):
    """
    Map a job requirement to candidate capabilities.

    The mapping is deliberately conservative.
    A capability is not treated as direct evidence merely
    because it is conceptually related.
    """

    name = normalize(requirement_name)

    direct = {
        "customer communication": [
            "CUSTOMER_COMMUNICATION"
        ],
        "business reviews": [
            "CUSTOMER_COMMUNICATION"
        ],
        "customer satisfaction": [
            "CUSTOMER_SATISFACTION"
        ],
        "continuous improvement": [
            "CONTINUOUS_IMPROVEMENT"
        ],
        "problem solving": [
            "CUSTOMER_PROBLEM_SOLVING"
        ],
        "escalation management": [
            "CUSTOMER_PROBLEM_SOLVING"
        ],
        "people leadership": [
            "PEOPLE_LEADERSHIP"
        ],
        "people management": [
            "PEOPLE_LEADERSHIP"
        ],
        "project management": [
            "PROJECT_MANAGEMENT"
        ],
        "stakeholder management": [
            "CUSTOMER_COMMUNICATION",
            "PROJECT_MANAGEMENT"
        ],
    }

    transferable = {
        "customer health": [
            "CUSTOMER_SATISFACTION",
            "CUSTOMER_COMMUNICATION",
        ],
        "customer adoption": [
            "CUSTOMER_PROBLEM_SOLVING",
            "CONTINUOUS_IMPROVEMENT",
        ],
        "data-driven decision making": [
            "CUSTOMER_SATISFACTION",
            "CUSTOMER_COMMUNICATION",
        ],
    }

    if name in direct:
        return {
            "type": "DIRECT",
            "capabilities": direct[name],
        }

    if name in transferable:
        return {
            "type": "TRANSFERABLE",
            "capabilities": transferable[name],
        }

    return {
        "type": "MISSING",
        "capabilities": [],
    }


def build_evidence_index(
    evidence: list[EvidenceItem]
):
    """
    Create a lookup from capability to verified evidence.
    """

    index = {}

    for item in evidence:

        if item.status != "VERIFIED":
            continue

        capability = item.capability

        if capability not in index:
            index[capability] = []

        index[capability].append(item)

    return index


def analyze_requirements(
    job: Job,
    evidence: list[EvidenceItem]
):
    """
    Analyze every job requirement against verified evidence.
    """

    evidence_index = build_evidence_index(evidence)

    requirement_analysis = []

    for requirement in job.requirements:

        classification = classify_requirement(
            requirement.name
        )

        matched_evidence = []

        for capability in classification["capabilities"]:

            items = evidence_index.get(
                capability,
                []
            )

            for item in items:
                matched_evidence.append(item)

        # Remove duplicate evidence items.
        unique_evidence = {
            item.id: item
            for item in matched_evidence
        }

        matched_evidence = list(
            unique_evidence.values()
        )

        if matched_evidence:

            if classification["type"] == "DIRECT":

                result_type = "DIRECT"
                confidence = "HIGH"

            else:

                result_type = "TRANSFERABLE"
                confidence = "MEDIUM"

        else:

            result_type = "MISSING"
            confidence = "UNKNOWN"

        requirement_analysis.append(
            {
                "requirement": requirement.name,
                "criticality": requirement.criticality,
                "category": requirement.category,
                "match_type": result_type,
                "confidence": confidence,
                "evidence_ids": [
                    item.id
                    for item in matched_evidence
                ],
            }
        )

    return requirement_analysis


def calculate_fit_score(
    job: Job,
    evidence: list[EvidenceItem]
):
    """
    Calculate a requirement-level fit score.

    DIRECT = full credit
    TRANSFERABLE = half credit
    MISSING = zero
    """

    analysis = analyze_requirements(
        job,
        evidence
    )

    total_weight = 0
    earned_weight = 0

    direct_count = 0
    transferable_count = 0
    missing_count = 0

    critical_gaps = []
    core_gaps = []

    for item in analysis:

        weight = CRITICALITY_WEIGHT.get(
            item["criticality"],
            1
        )

        total_weight += weight

        if item["match_type"] == "DIRECT":

            earned_weight += weight
            direct_count += 1

        elif item["match_type"] == "TRANSFERABLE":

            earned_weight += weight * 0.5
            transferable_count += 1

        else:

            missing_count += 1

            if item["criticality"] == "CRITICAL":
                critical_gaps.append(
                    item["requirement"]
                )

            elif item["criticality"] == "CORE":
                core_gaps.append(
                    item["requirement"]
                )

    if total_weight == 0:
        overall_score = 0.0
    else:
        overall_score = (
            earned_weight / total_weight
        ) * 100

    return {
        "overall_score": round(
            overall_score,
            2
        ),
        "direct_matches": direct_count,
        "transferable_matches": transferable_count,
        "missing_requirements": missing_count,
        "critical_gaps": critical_gaps,
        "core_gaps": core_gaps,
        "requirement_analysis": analysis,
    }


def calculate_fit(
    job: Job,
    candidate: CandidateProfile,
    evidence: list[EvidenceItem]
):
    """
    Public scoring function used by CareerOS.

    Candidate is retained in the signature because the
    candidate profile is part of the scoring context.
    """

    result = calculate_fit_score(
        job,
        evidence
    )

    return result
