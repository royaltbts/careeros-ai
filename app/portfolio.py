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


def render_candidate_section(portfolio):
    candidate = portfolio["candidate"]
    strategy = portfolio["career_strategy"]

    print()
    print("PROFESSIONAL DIRECTION")
    print("-" * 80)
    print(f"Primary direction: {strategy.primary_direction}")

    print()
    print("TARGET ROLES")
    for role in strategy.target_roles:
        print(f"  • {role}")

    print()
    print("TARGET SENIORITY")
    for level in strategy.preferred_seniority:
        print(f"  • {level}")

    print()
    print("LOCATION")
    print(f"  Home: {strategy.home_city}, {strategy.home_country}")
    print(f"  Geography: {strategy.geography}")
    print(f"  Local work modes: {', '.join(strategy.local_work_modes)}")
    print(f"  Outside-country mode: {strategy.outside_country_work_mode}")

    print()
    print("CORE CUSTOMER SUCCESS CAPABILITIES")
    for capability in strategy.priority_capabilities:
        print(f"  • {capability}")

    print()
    print("PROFESSIONAL STRENGTHS")
    for strength in candidate.strengths:
        print(f"  • {strength}")

    print()
    print("=" * 80)


def render_portfolio(job_id="GH-stripe-6558993"):
    portfolio = build_portfolio()

    print()
    print("=" * 80)
    print("CAREEROS PORTFOLIO")
    print("ARUNKUMAR SIRIPURAPU")
    print("=" * 80)

    render_candidate_section(portfolio)
    render_evidence_section(portfolio)
    render_opportunity_section(job_id)
    render_supervisor_section(job_id)
    render_application_section(job_id)

    print()
    print("=" * 80)
    print("CAREEROS PORTFOLIO — END")
    print("=" * 80)


def render_evidence_section(portfolio):
    candidate = portfolio["candidate"]
    evidence = portfolio["evidence"]

    print()
    print("=" * 80)
    print("EVIDENCE & CAREER TRUTH")
    print("=" * 80)

    print()
    print("VERIFIED EVIDENCE")
    for item in evidence:
        print(f"  • {item.id}: {item.capability} — {item.claim}")

    print()
    print("TRANSFERABLE EXPERIENCE")
    print("  • People management → Customer Success leadership")
    print("  • Project management → Customer Success delivery")
    print("  • Lean Six Sigma → Customer Success process improvement")

    print()
    print("EXPLICIT CAREER GAPS")
    print("  • Formal SaaS experience")
    print("  • CRM expertise")
    print("  • Enterprise account ownership")

    print()
    print("TRUTH CONTROLS")
    for rule in candidate.truth_rules:
        print(f"  • {rule}")

    print()
    print("=" * 80)


def load_portfolio_opportunity(job_id):
    import json

    with open(f"data/jobs/opportunity_decisions/{job_id}.json") as f:
        opportunity_decision = json.load(f)

    with open(f"data/jobs/supervisor_decisions/{job_id}.json") as f:
        supervisor_history = json.load(f)

    with open(f"data/jobs/strategies/{job_id}.json") as f:
        strategy = json.load(f)

    with open(f"data/jobs/applications/{job_id}.json") as f:
        application = json.load(f)

    return {
        "opportunity_decision": opportunity_decision,
        "supervisor_history": supervisor_history,
        "strategy": strategy,
        "application": application,
    }


def render_opportunity_section(job_id):
    data = load_portfolio_opportunity(job_id)
    decision = data["opportunity_decision"]

    print()
    print("=" * 80)
    print("CAREEROS OPPORTUNITY")
    print("=" * 80)

    print()
    print(f"COMPANY: {decision['company']}")
    print(f"ROLE: {decision['title']}")

    print()
    print("OPPORTUNITY SIGNALS")
    print(f"  Opportunity score: {decision['opportunity_score']}")
    print(f"  Priority: {decision['priority']}")
    print(f"  CareerOS decision: {decision['recommendation']}")

    print()
    print("COMPANY STRATEGIC FIT")
    print(f"  Strategic alignment: {decision['company_strategic_alignment']}")
    print(f"  Research confidence: {decision['company_research_confidence']}")
    print(f"  Research coverage: {decision['company_research_coverage']}")
    print(f"  Research quality: {decision['company_research_quality']}")
    print(f"  Decision-ready fit: {decision['company_decision_ready_fit']}")

    print()
    print("DECISION REASONS")
    for reason in decision["decision_reasons"]:
        print(f"  • {reason}")

    print()
    print("STRENGTHS")
    for strength in decision["strengths"]:
        print(f"  • {strength}")

    print()
    print("CAREER GAPS")
    gaps = decision["critical_gaps"] + decision["transferable_opportunities"]
    if gaps:
        for gap in gaps:
            print(f"  • {gap}")
    else:
        print("  • None recorded")

    print()
    print(f"Human review required: {decision['human_review_required']}")

    print()
    print("=" * 80)


def get_latest_supervisor_decision(history):
    if not history:
        return None

    return history[-1]


def render_supervisor_section(job_id):
    data = load_portfolio_opportunity(job_id)
    supervisor = get_latest_supervisor_decision(
        data["supervisor_history"]
    )

    print()
    print("=" * 80)
    print("SUPERVISOR DELIBERATION")
    print("=" * 80)

    print()
    print(f"RECOMMENDATION: {supervisor['recommendation']}")
    print(f"CONFIDENCE: {supervisor['confidence']:.4f}")

    print()
    print("FINDINGS")
    for finding in supervisor["findings"]:
        print(f"  • {finding['source']}:")
        print(f"    {finding['finding']}")

    print()
    print("CONFLICTS")
    for conflict in supervisor["conflicts"]:
        print(f"  • {conflict}")

    print()
    print("UNRESOLVED QUESTIONS")
    for question in supervisor["unresolved_questions"]:
        print(f"  • {question}")

    print()
    print(f"Human review required: {supervisor['human_review_required']}")
    print(f"External action allowed: {supervisor['external_action_allowed']}")

    print()
    print("=" * 80)


def render_application_section(job_id):
    data = load_portfolio_opportunity(job_id)
    application = data["application"]

    print()
    print("=" * 80)
    print("APPLICATION PACKAGE")
    print("=" * 80)

    print()
    print(f"STATUS: {application['status']}")
    print(f"PACKAGE VERSION: {application['package_version']}")
    print(f"APPLICATION DECISION: {application['application_decision']}")

    print()
    print("POSITIONING")
    print(f"  {application['profile']['positioning_statement']}")

    print()
    print("TAILORED RESUME")
    print(f"  Headline: {application['resume']['headline']}")
    print(f"  Summary: {application['resume']['summary']}")

    print()
    print("RESUME EVIDENCE")
    for bullet in application["resume"]["bullets"]:
        print(f"  • {bullet['bullet']}")
        print(f"    Evidence: {', '.join(bullet['evidence_ids'])}")
        print(f"    Confidence: {bullet['confidence']}")
        print(f"    Allowed: {bullet['allowed']}")

    print()
    print("EVIDENCE MAP")
    for item in application["evidence_map"]:
        print(f"  • {item['requirement']}")
        print(f"    Match: {item['match_type']}")
        print(f"    Evidence: {', '.join(item['evidence_ids']) or 'None'}")
        print(f"    Confidence: {item['confidence']}")
        print(f"    Allowed: {item['allowed']}")

    print()
    print("SAFETY & APPROVAL")
    print(f"  Claims safe: {application['claims_safe']}")
    print(f"  Human approval required: {application['human_approval_required']}")
    print(f"  Approved by human: {application['approved_by_human']}")
    print("  External action authorized: False")

    print()
    print("=" * 80)
