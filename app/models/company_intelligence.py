from pydantic import BaseModel
from typing import List, Optional


class CompanyFact(BaseModel):
    category: str
    fact: str
    source: str
    confidence: str = "MEDIUM"


class CompanyIntelligence(BaseModel):
    company: str
    industry: Optional[str] = None
    product_or_service: Optional[str] = None
    customer_segments: List[str] = []
    business_model: Optional[str] = None
    company_stage: Optional[str] = None

    customer_success_model: Optional[str] = None
    likely_cs_priorities: List[str] = []

    strategic_relevance: str = ""
    potential_risks: List[str] = []

    facts: List[CompanyFact] = []

    research_status: str = "NOT_RESEARCHED"
    human_review_required: bool = True
