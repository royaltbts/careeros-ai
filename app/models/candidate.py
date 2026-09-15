from pydantic import BaseModel
from typing import List


class TargetRole(BaseModel):
    title: str


class ClientProject(BaseModel):
    company: str
    relationship: str
    scope: str


class CandidateExperience(BaseModel):
    years: str
    current_background: str
    people_management: bool
    project_management: bool
    lean_six_sigma: bool


class CustomerExperience(BaseModel):
    external_clients: List[ClientProject]
    customer_facing_activities: List[str]
    customer_issues_handled: List[str]


class ImprovementExperience(BaseModel):
    initiative: str
    problem: str
    action: List[str]
    objective: str


class CandidateProfile(BaseModel):

    career_direction: dict

    experience: CandidateExperience

    customer_experience: CustomerExperience

    customer_success_metrics: List[str]

    improvement_experience: List[ImprovementExperience]

    strengths: List[str]

    excluded_skills: List[str]

    truth_rules: List[str]
