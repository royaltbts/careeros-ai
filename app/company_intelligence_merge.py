from app.models.company_intelligence import CompanyIntelligence


def merge_company_intelligence(
    role_derived: CompanyIntelligence,
    web_researched: CompanyIntelligence,
) -> CompanyIntelligence:
    if role_derived.company != web_researched.company:
        raise ValueError(
            "Cannot merge CompanyIntelligence records for different companies."
        )

    merged_facts = []
    seen_facts = set()

    for intelligence in (
        role_derived,
        web_researched,
    ):
        for fact in intelligence.facts:
            key = (
                fact.category.strip().lower(),
                fact.fact.strip().lower(),
                fact.source.strip(),
            )

            if key not in seen_facts:
                seen_facts.add(key)
                merged_facts.append(fact)

    merged_priorities = []

    for priority in (
        role_derived.likely_cs_priorities
        + web_researched.likely_cs_priorities
    ):
        if priority not in merged_priorities:
            merged_priorities.append(priority)

    merged_customer_segments = []

    for segment in (
        role_derived.customer_segments
        + web_researched.customer_segments
    ):
        if segment not in merged_customer_segments:
            merged_customer_segments.append(segment)

    merged_risks = []

    for risk in (
        role_derived.potential_risks
        + web_researched.potential_risks
    ):
        if risk not in merged_risks:
            merged_risks.append(risk)

    return CompanyIntelligence(
        company=role_derived.company,
        industry=(
            web_researched.industry
            or role_derived.industry
        ),
        product_or_service=(
            web_researched.product_or_service
            or role_derived.product_or_service
        ),
        customer_segments=merged_customer_segments,
        business_model=(
            web_researched.business_model
            or role_derived.business_model
        ),
        company_stage=(
            web_researched.company_stage
            or role_derived.company_stage
        ),
        customer_success_model=(
            web_researched.customer_success_model
            or role_derived.customer_success_model
        ),
        likely_cs_priorities=merged_priorities,
        strategic_relevance=(
            web_researched.strategic_relevance
            or role_derived.strategic_relevance
        ),
        potential_risks=merged_risks,
        facts=merged_facts,
        research_status=(
            "WEB_RESEARCHED"
            if web_researched.research_status == "WEB_RESEARCHED"
            else role_derived.research_status
        ),
        human_review_required=True,
    )
