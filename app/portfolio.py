from app.pipeline import (
    load_candidate_profile,
    load_evidence,
    load_career_strategy,
)


def build_portfolio():
    candidate = load_candidate_profile(
        "data/candidate/profile.json"
    )
    evidence = load_evidence(
        "data/evidence/evidence.json"
    )
    career_strategy = load_career_strategy(
        "data/candidate/career_strategy.json"
    )

    return {
        "candidate": candidate,
        "evidence": evidence,
        "career_strategy": career_strategy,
    }
