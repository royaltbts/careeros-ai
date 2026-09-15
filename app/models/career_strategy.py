from pydantic import BaseModel
from typing import List


class CareerStrategy(BaseModel):
    primary_direction: str

    target_roles: List[str]

    preferred_seniority: List[str]

    geography: str

    priority_capabilities: List[str]

    avoid_roles: List[str]

    strategy_notes: List[str]
