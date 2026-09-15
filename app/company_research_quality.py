from app.company_research import CompanyResearchResult


RESEARCH_CATEGORIES = {
    "industry",
    "product",
    "product/service",
    "customer segment",
    "customer segments",
    "business model",
    "company stage",
    "customer success model",
    "cs model",
    "cs priority",
    "cs priorities",
    "risk",
}


CONFIDENCE_WEIGHT = {
    "HIGH": 1.0,
    "MEDIUM": 0.75,
    "LOW": 0.50,
}


def calculate_research_quality(
    research: CompanyResearchResult,
) -> dict:
    normalized_categories = {
        category.strip().lower()
        for category in RESEARCH_CATEGORIES
    }

    covered_categories = set()

    confidence_scores = []

    for fact in research.facts:
        category = fact.category.strip().lower()

        if category in normalized_categories:
            covered_categories.add(category)

        confidence = fact.confidence.strip().upper()

        if confidence in CONFIDENCE_WEIGHT:
            confidence_scores.append(
                CONFIDENCE_WEIGHT[confidence]
            )

    # Treat the eight major research dimensions as the
    # completeness target. Equivalent category labels such
    # as "customer segments" and "customer segment" count
    # toward the same dimension.
    category_groups = [
        {"industry"},
        {"product", "product/service"},
        {"customer segment", "customer segments"},
        {"business model"},
        {"company stage"},
        {"customer success model", "cs model"},
        {"cs priority", "cs priorities"},
        {"risk"},
    ]

    covered_dimensions = 0

    for group in category_groups:
        if covered_categories.intersection(group):
            covered_dimensions += 1

    coverage = (
        covered_dimensions / len(category_groups)
    ) * 100.0

    if confidence_scores:
        average_confidence = (
            sum(confidence_scores)
            / len(confidence_scores)
        )
    else:
        average_confidence = 0.0

    confidence_score = (
        average_confidence * 100.0
    )

    # Research quality is driven primarily by coverage,
    # with evidence confidence contributing to the final score.
    score = (
        coverage * 0.70
        + confidence_score * 0.30
    )

    # Non-web research must never appear equivalent to
    # fully researched company intelligence.
    if research.research_status != "WEB_RESEARCHED":
        score = min(score, 75.0)

    score = round(
        max(min(score, 100.0), 0.0),
        2,
    )

    return {
        "score": score,
        "coverage": round(coverage, 2),
        "confidence": round(confidence_score, 2),
        "status": research.research_status,
        "covered_dimensions": covered_dimensions,
        "total_dimensions": len(category_groups),
    }
