from app.models.company_intelligence import CompanyIntelligence
from app.company_research import CompanyResearchResult


def map_research_to_intelligence(
    research: CompanyResearchResult,
) -> CompanyIntelligence:

    industry = None
    product_or_service = None
    customer_segments = []
    business_model = None
    company_stage = None
    customer_success_model = None
    likely_cs_priorities = []
    potential_risks = []

    for fact in research.facts:
        category = fact.category.strip().lower()

        if category == "industry":
            industry = fact.fact

        elif category in {"product", "product/service"}:
            product_or_service = fact.fact

        elif category in {"customer segment", "customer segments"}:
            if fact.fact not in customer_segments:
                customer_segments.append(fact.fact)

        elif category == "business model":
            business_model = fact.fact

        elif category == "company stage":
            company_stage = fact.fact

        elif category in {
            "customer success model",
            "cs model",
        }:
            customer_success_model = fact.fact

        elif category in {
            "cs priority",
            "cs priorities",
        }:
            if fact.fact not in likely_cs_priorities:
                likely_cs_priorities.append(fact.fact)

        elif category == "risk":
            if fact.fact not in potential_risks:
                potential_risks.append(fact.fact)

    return CompanyIntelligence(
        company=research.company,
        industry=industry,
        product_or_service=product_or_service,
        customer_segments=customer_segments,
        business_model=business_model,
        company_stage=company_stage,
        customer_success_model=customer_success_model,
        likely_cs_priorities=likely_cs_priorities,
        potential_risks=potential_risks,
        facts=research.facts,
        research_status=research.research_status,
        human_review_required=True,
    )
