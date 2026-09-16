from app.models.career_strategy import CareerStrategy
from app.models.job_location_evaluation import JobLocationEvaluation


def evaluate_location(
    location: str | None,
    work_mode: str | None,
    strategy: CareerStrategy,
) -> JobLocationEvaluation:
    location_text = (location or "").strip().lower()
    mode = (work_mode or "").strip().lower()

    home_city = strategy.home_city.strip().lower()
    home_country = strategy.home_country.strip().lower()

    is_local = (
        home_city in location_text
        or home_country in location_text
    )

    if mode == "remote":
        return JobLocationEvaluation(
            eligible=True,
            reason="Remote work is compatible with the candidate's geography policy.",
            confidence=1.0,
            verification_required=False,
        )

    if is_local and mode in {
        value.lower()
        for value in strategy.local_work_modes
    }:
        return JobLocationEvaluation(
            eligible=True,
            reason="Local India/Hyderabad role with an accepted work mode.",
            confidence=1.0,
            verification_required=False,
        )

    if not mode:
        return JobLocationEvaluation(
            eligible=True,
            reason="Work mode is not explicitly stated; verification required.",
            confidence=0.5,
            verification_required=True,
        )

    if (
        not is_local
        and mode != strategy.outside_country_work_mode.lower()
    ):
        return JobLocationEvaluation(
            eligible=False,
            reason="Outside India role is not remote.",
            confidence=1.0,
            verification_required=False,
        )

    return JobLocationEvaluation(
        eligible=False,
        reason="Work mode is incompatible with the candidate's geography policy.",
        confidence=1.0,
        verification_required=False,
    )


def is_location_eligible(
    location: str | None,
    work_mode: str | None,
    strategy: CareerStrategy,
) -> bool:
    return evaluate_location(
        location,
        work_mode,
        strategy,
    ).eligible
