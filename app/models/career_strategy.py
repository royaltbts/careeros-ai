from pydantic import BaseModel
from typing import List


class CareerStrategy(BaseModel):
    primary_direction: str

    target_roles: List[str]

    preferred_seniority: List[str]

    geography: str
    home_country: str = "India"
    home_city: str = "Hyderabad"
    local_work_modes: List[str] = ["on-site", "hybrid", "remote"]
    outside_country_work_mode: str = "remote"

    priority_capabilities: List[str]

    avoid_roles: List[str]

    strategy_notes: List[str]
