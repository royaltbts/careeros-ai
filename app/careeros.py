from openai import OpenAIError
from agents import AgentsException
import json
import os
import uuid
from pathlib import Path

from app.market_scout_pipeline import (
    build_job_intelligence,
    save_job_intelligence,
)
from app.job_discovery_factory import discover_jobs

from app.company_intelligence import (
    build_company_intelligence,
    save_company_intelligence,
)
from app.company_research_web import (
    OpenAIWebCompanyResearchSource,
)
from app.company_research_mock import (
    MockCompanyResearchSource,
)
from app.company_research_pipeline import (
    process_company_research,
)
from app.company_intelligence_merge import (
    merge_company_intelligence,
)
from app.company_research_web_basic import (
    BasicWebCompanyResearchSource,
)

from app.models.candidate import CandidateProfile
from app.models.evidence import EvidenceItem
from app.models.career_strategy import CareerStrategy
from app.models.job import Job
from app.models.application_package import ApplicationPackage
from app.models.company_intelligence import CompanyIntelligence
from app.models.opportunity_status import OpportunityStatus

from app.scoring import calculate_fit
from app.opportunity_scorer import calculate_opportunity_score
from app.opportunity_decision import build_opportunity_decision
from app.opportunity_decision_store import save_opportunity_decision
from app.models.opportunity_decision_audit import OpportunityDecisionAudit
from app.opportunity_decision_audit_store import save_opportunity_decision_audit
from app.application_strategy import build_strategy, save_strategy
from app.application_effort import build_application_effort
from app.application_effort_store import save_application_effort
from app.profile_tailor import build_profile_tailor
from app.tailored_resume import build_tailored_resume
from app.human_approval import prepare_for_approval
from app.package_integrity import calculate_content_hash
from app.execution_authorization_builder import build_execution_authorization
from app.execution_authorization_store import save_execution_authorization
from app.supervisor import (
    build_supervisor_decision_from_case,
)
from app.supervisor_case import build_supervisor_case
from app.candidate_provider import (
    build_candidate_finding_with_provider,
)
from app.supervisor_decision_store import save_supervisor_decision
from app.models.deliberation_record import DeliberationRecord
from app.deliberation_store import save_deliberation


BASE_DIR = Path(__file__).resolve().parent.parent

DISCOVERED_JOBS_FILE = (
    BASE_DIR
    / "data"
    / "jobs"
    / "discovered_jobs.json"
)

CANDIDATE_FILE = (
    BASE_DIR
    / "data"
    / "candidate"
    / "profile.json"
)

CAREER_STRATEGY_FILE = (
    BASE_DIR
    / "data"
    / "candidate"
    / "career_strategy.json"
)

EVIDENCE_FILE = (
    BASE_DIR
    / "data"
    / "evidence"
    / "evidence.json"
)

APPLICATIONS_DIR = (
    BASE_DIR
    / "data"
    / "jobs"
    / "applications"
)


# ============================================================
# FILE HELPERS
# ============================================================

def load_json(path: Path):
    """
    Load JSON from disk.
    """
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_candidate() -> CandidateProfile:
    """
    Load and validate Candidate Truth Profile.
    """
    return CandidateProfile.model_validate(
        load_json(CANDIDATE_FILE)
    )


def load_evidence() -> list[EvidenceItem]:
    """
    Load and validate the Evidence Library.
    """
    data = load_json(EVIDENCE_FILE)

    return [
        EvidenceItem.model_validate(item)
        for item in data
    ]


def load_career_strategy() -> CareerStrategy:
    """
    Load and validate the Career Strategy.
    """
    return CareerStrategy.model_validate(
        load_json(CAREER_STRATEGY_FILE)
    )


# ============================================================
# JOB CONVERSION
# ============================================================

def build_job_from_intelligence(
    job_intelligence,
) -> Job:
    """
    Convert JobIntelligence into the Job model
    required by the scoring engine.
    """
    return Job(
        job_id=job_intelligence.job_id,
        company=job_intelligence.company,
        title=job_intelligence.title,
        location=job_intelligence.location,
        employment_type=job_intelligence.employment_type,
        description="",
        responsibilities=job_intelligence.responsibilities,
        requirements=job_intelligence.requirements,
        experience_required=job_intelligence.experience_required,
        industry=job_intelligence.industry,
        source_url=job_intelligence.source_url,
    )


# ============================================================
# APPLICATION PACKAGE PERSISTENCE
# ============================================================

def get_application_file(job_id: str) -> Path:
    """
    Return the persisted application package path.
    """
    return APPLICATIONS_DIR / f"{job_id}.json"


def load_existing_application_package(
    job_id: str,
):
    """
    Load an existing ApplicationPackage if one exists.

    Returns None when no package exists.
    """
    file_path = get_application_file(job_id)

    if not file_path.exists():
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return ApplicationPackage.model_validate(data)


def save_application_package(
    package: ApplicationPackage,
):
    """
    Persist a complete application package.
    """
    APPLICATIONS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = get_application_file(
        package.job_id
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            package.model_dump(
                mode="json"
            ),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


# ============================================================
# PACKAGE VERSIONING + APPROVAL INTEGRITY
# ============================================================

def prepare_package_identity(
    new_package: ApplicationPackage,
    existing_package: ApplicationPackage | None,
) -> ApplicationPackage:
    """
    Assign package version and content hash.

    Approval is valid only for the exact content that was reviewed.

    Rules:

    1. No existing package:
       Create Version 1.

    2. Existing package with identical content:
       Keep the existing version and human approval state.

    3. Existing package with changed content:
       Create a new version and require human review again.

    4. Existing legacy package without a stored hash:
       Calculate its hash before comparison so old packages
       can be safely migrated.
    """

    new_hash = calculate_content_hash(
        new_package
    )

    new_package.content_hash = new_hash

    # --------------------------------------------------------
    # First package
    # --------------------------------------------------------

    if existing_package is None:
        new_package.package_version = 1
        new_package.approved_by_human = False
        new_package.approved_content_hash = None
        new_package.status = (
            OpportunityStatus.PENDING_APPROVAL
        )

        return new_package

    # --------------------------------------------------------
    # Determine the existing content hash
    # --------------------------------------------------------

    existing_hash = existing_package.content_hash

    if not existing_hash:
        existing_hash = calculate_content_hash(
            existing_package
        )

    # --------------------------------------------------------
    # Content unchanged
    # --------------------------------------------------------

    if existing_hash == new_hash:

        new_package.package_version = (
            existing_package.package_version
        )

        new_package.content_hash = new_hash

        new_package.status = (
            existing_package.status
        )

        new_package.approved_by_human = (
            existing_package.approved_by_human
        )

        new_package.approved_content_hash = (
            existing_package.approved_content_hash
        )

        new_package.reviewer_notes = (
            existing_package.reviewer_notes
        )

        # Migrate legacy approved packages.
        if (
            existing_package.approved_by_human
            and not existing_package.approved_content_hash
        ):
            new_package.approved_content_hash = new_hash

        return new_package

    # --------------------------------------------------------
    # Content changed
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # Never overwrite an existing package during a normal
    # pipeline rerun when its content has already been
    # reviewed or potentially edited by a human.
    #
    # A deliberate regeneration should be an explicit action.
    #
    new_package = existing_package.model_copy(deep=True)

    if not new_package.content_hash:
        new_package.content_hash = existing_hash

    return new_package


# ============================================================
# CAREEROS PIPELINE
# ============================================================

def run_careeros():

    print()
    print("=" * 80)
    print("CAREEROS — END-TO-END PIPELINE")
    print("=" * 80)

    # ========================================================
    # 1. CANDIDATE TRUTH
    # ========================================================

    candidate = load_candidate()
    evidence = load_evidence()
    career_strategy = load_career_strategy()

    print()
    print("[1/9] Candidate Truth loaded")

    candidate_provider = os.getenv(
        "CAREEROS_CANDIDATE_PROVIDER",
        "mock",
    ).strip().lower()

    print(
        f"  Candidate provider: "
        f"{candidate_provider.upper()}"
    )

    candidate_finding = build_candidate_finding_with_provider(
        candidate,
        evidence,
        provider=candidate_provider,
    )

    # ========================================================
    # 2. MARKET SCOUT
    # ========================================================

    print()
    print("[2/9] Market Scout")

    jobs, discovery_provider = discover_jobs(
        str(DISCOVERED_JOBS_FILE),
        strategy=career_strategy,
    )

    print(
        f"  Discovery provider: "
        f"{discovery_provider}"
    )

    print(
        f"Jobs discovered: "
        f"{len(jobs)}"
    )

    print(
        f"Relevant jobs: "
        f"{len(jobs)}"
    )

    # ========================================================
    # 3. JOB INTELLIGENCE
    # ========================================================

    print()
    print("[3/9] Job Intelligence")

    intelligence_list = []

    for job_discovery in jobs:

        intelligence = build_job_intelligence(
            job_discovery
        )

        save_job_intelligence(
            intelligence
        )

        intelligence_list.append(
            intelligence
        )

    print(
        f"Jobs analyzed: "
        f"{len(intelligence_list)}"
    )

    # ========================================================
    # 4. COMPANY INTELLIGENCE
    # ========================================================

    print()
    print("[4/9] Company Intelligence")
    research_provider = os.getenv(
        "CAREEROS_RESEARCH_PROVIDER",
        "mock",
    ).strip().lower()

    if research_provider == "openai":
        company_research_source = OpenAIWebCompanyResearchSource(
            search_context_size="low",
        )
    elif research_provider == "mock":
        company_research_source = MockCompanyResearchSource()
    elif research_provider == "basic_web":
        company_research_source = None
    else:
        raise ValueError(
            "Unsupported CAREEROS_RESEARCH_PROVIDER: "
            f"{research_provider}. "
            "Use 'mock', 'openai', or 'basic_web'."
        )

    print(
        f"  Research provider: {research_provider.upper()}"
    )

    company_intelligence_list = []
    company_intelligence_by_job = {}

    for intelligence in intelligence_list:
        role_derived_intelligence = build_company_intelligence(
            intelligence.job_id
        )

        try:
            if research_provider == "mock":
                research = company_research_source.research(
                    intelligence.company
                )
                web_intelligence = process_company_research(
                    research
                )

            elif research_provider == "openai":
                research = company_research_source.research(
                    intelligence.company
                )
                web_intelligence = process_company_research(
                    research
                )

            elif research_provider == "basic_web":
                web_source = BasicWebCompanyResearchSource(
                    intelligence.source_url or ""
                )
                research = web_source.research(
                    intelligence.company
                )
                web_intelligence = process_company_research(
                    research
                )

            else:
                raise ValueError(
                    f"Unsupported research provider: {research_provider}"
                )

            company_intelligence = merge_company_intelligence(
                role_derived_intelligence,
                web_intelligence,
            )

        except (AgentsException, OpenAIError, ValueError) as exc:
            print(
                f"  Web research unavailable for "
                f"{intelligence.company}: {type(exc).__name__}"
            )
            company_intelligence = role_derived_intelligence

        save_company_intelligence(
            company_intelligence,
            intelligence.job_id,
        )

        # Reload the persisted record so downstream scoring uses
        # the highest-quality intelligence available.
        company_intelligence = CompanyIntelligence.model_validate(
            json.loads(
                (
                    BASE_DIR
                    / "data"
                    / "jobs"
                    / "company_intelligence"
                    / f"{intelligence.job_id}.json"
                ).read_text()
            )
        )

        company_intelligence_list.append(
            company_intelligence
        )
        company_intelligence_by_job[
            intelligence.job_id
        ] = company_intelligence

        print(
            f"  {intelligence.job_id} | "
            f"{company_intelligence.company} | "
            f"Research: "
            f"{company_intelligence.research_status}"
        )

    print(
        f"Company intelligence records: "
        f"{len(company_intelligence_list)}"
    )


    # ========================================================
    # 5. OPPORTUNITY SCORING
    # ========================================================


    print()
    print("[5/9] Opportunity Scoring")

    scored_opportunities = []

    for intelligence in intelligence_list:

        job = build_job_from_intelligence(
            intelligence
        )

        fit_result = calculate_fit(
            job,
            candidate,
            evidence,
        )

        opportunity_result = (
            calculate_opportunity_score(
                job,
                career_strategy,
                fit_result,
                company_intelligence_by_job.get(
                    job.job_id
                ),
            )
        )

        scored_opportunities.append(
            {
                "job_id": job.job_id,
                "company": job.company,
                "title": job.title,

                "fit_score": (
                    fit_result[
                        "overall_score"
                    ]
                ),

                "opportunity_score": (
                    opportunity_result[
                        "opportunity_score"
                    ]
                ),

                "priority": (
                    opportunity_result[
                        "priority"
                    ]
                ),

                "critical_gaps": (
                    fit_result[
                        "critical_gaps"
                    ]
                ),

                "core_gaps": (
                    fit_result[
                        "core_gaps"
                    ]
                ),

                "requirement_analysis": (
                    fit_result[
                        "requirement_analysis"
                    ]
                ),

                "company_strategic_fit": (
                    opportunity_result[
                        "company_strategic_fit"
                    ]
                ),
            }
        )

        print(
            f"  {job.job_id} | "
            f"{job.title} | "
            f"Fit: "
            f"{fit_result['overall_score']} | "
            f"Opportunity: "
            f"{opportunity_result['opportunity_score']} | "
            f"Priority: "
            f"{opportunity_result['priority']}"
        )

    # ========================================================
    # 5. OPPORTUNITY DECISION
    # ========================================================

    print()
    print("[5.5/9] Opportunity Decision")

    opportunity_decisions = []

    for opportunity in scored_opportunities:
        decision = build_opportunity_decision(
            opportunity
        )
        save_opportunity_decision(decision)

        audit = OpportunityDecisionAudit(
            job_id=decision.job_id,
            company=decision.company,
            title=decision.title,
            opportunity_score=decision.opportunity_score,
            priority=decision.priority,
            recommendation=decision.recommendation,
            decision_reasons=decision.decision_reasons,
            strengths=decision.strengths,
            critical_gaps=decision.critical_gaps,
            transferable_opportunities=(
                decision.transferable_opportunities
            ),
            company_strategic_alignment=(
                decision.company_strategic_alignment
            ),
            company_research_confidence=(
                decision.company_research_confidence
            ),
            company_research_coverage=(
                decision.company_research_coverage
            ),
            company_research_evidence_confidence=(
                decision.company_research_evidence_confidence
            ),
            company_research_quality=(
                decision.company_research_quality
            ),
            company_decision_ready_fit=(
                decision.company_decision_ready_fit
            ),
            human_review_required=(
                decision.human_review_required
            ),
        )

        save_opportunity_decision_audit(audit)

        supervisor_case = build_supervisor_case(
            opportunity=opportunity,
            decision=decision.model_dump(
                mode="json"
            ),
            safety=None,
            candidate_finding=candidate_finding,
        )

        supervisor_result = build_supervisor_decision_from_case(
            case=supervisor_case,
            base_decision=decision.model_dump(
                mode="json"
            ),
        )

        save_supervisor_decision(
            supervisor_result
        )

        deliberation_record = DeliberationRecord(
            job_id=supervisor_case.job_id,
            company=supervisor_case.company,
            title=supervisor_case.title,
            cycle_id=f"cycle-{uuid.uuid4().hex}",
            agent_findings=[
                finding.model_dump(mode="json")
                for finding in supervisor_case.findings
            ],
            disagreements=[
                disagreement.model_dump(mode="json")
                for disagreement in supervisor_case.disagreements
            ],
            supervisor_recommendation=(
                supervisor_result.recommendation
            ),
            supervisor_confidence=(
                supervisor_result.confidence
            ),
            supervisor_conflicts=(
                supervisor_result.conflicts
            ),
            unresolved_questions=(
                supervisor_result.unresolved_questions
            ),
            human_review_required=(
                supervisor_result.human_review_required
            ),
            external_action_allowed=(
                supervisor_result.external_action_allowed
            ),
        )

        save_deliberation(
            deliberation_record
        )

        print(
            f"    Supervisor: "
            f"{supervisor_result.recommendation} | "
            f"Confidence: "
            f"{supervisor_result.confidence}"
        )

        if supervisor_result.conflicts:
            for conflict in supervisor_result.conflicts:
                print(
                    f"    Supervisor conflict: "
                    f"{conflict}"
                )

        for finding in supervisor_result.findings:
            if finding.source == "Supervisor Resolution":
                print(
                    f"    Supervisor resolution: "
                    f"{finding.finding}"
                )

        opportunity_decisions.append(
            decision
        )

        print(
            f"  {decision.job_id} | "
            f"{decision.title} | "
            f"Decision: {decision.recommendation} | "
            f"Priority: {decision.priority} | "
            f"Score: {decision.opportunity_score}"
        )

    print(
        f"Opportunity decisions created: "
        f"{len(opportunity_decisions)}"
    )

    # ========================================================
    # 5.7 APPLICATION EFFORT
    # ========================================================

    print()
    print("[5.7/9] Application Effort")

    application_efforts = []

    for decision in opportunity_decisions:
        effort = build_application_effort(
            decision
        )

        save_application_effort(
            effort
        )

        application_efforts.append(
            effort
        )

        print(
            f"  {effort.job_id} | "
            f"{effort.title} | "
            f"Effort: {effort.effort_level} | "
            f"Decision: {effort.recommendation} | "
            f"Score: {effort.opportunity_score}"
        )

    print(
        f"Application effort assessments created: "
        f"{len(application_efforts)}"
    )

    # ========================================================
    # 6. APPLICATION STRATEGY
    # ========================================================

    print()
    print("[6/9] Application Strategy")

    strategies = []

    for opportunity in scored_opportunities:

        strategy = build_strategy(
            opportunity,
            evidence,
        )

        strategies.append(
            strategy
        )
        save_strategy(strategy)

    print(
        f"Strategies created: "
        f"{len(strategies)}"
    )

    # ========================================================
    # 6. APPLICATION PACKAGES
    # ========================================================

    print()
    print("[7/9] Application Packages")

    application_packages = []

    for opportunity in scored_opportunities:

        job_id = opportunity[
            "job_id"
        ]

        opportunity_decision = next(
            item
            for item in opportunity_decisions
            if item.job_id == job_id
        )

        if opportunity_decision.recommendation not in [
            "APPLY",
            "CONDITIONAL",
        ]:
            print(
                f"  {job_id} | "
                f"Package skipped by Opportunity Decision: "
                f"{opportunity_decision.recommendation}"
            )
            continue

        strategy = next(
            item
            for item in strategies
            if item.job_id == job_id
        )

        # ----------------------------------------------------
        # Profile Tailoring + Evidence Map
        # ----------------------------------------------------

        profile, evidence_map = (
            build_profile_tailor(
                job_id
            )
        )

        # ----------------------------------------------------
        # Tailored Resume
        # ----------------------------------------------------

        resume = build_tailored_resume(
            job_id
        )

        # ----------------------------------------------------
        # Human Approval Preparation
        # ----------------------------------------------------

        approval = prepare_for_approval(
            job_id
        )

        # ----------------------------------------------------
        # Create new package
        # ----------------------------------------------------

        package = ApplicationPackage(

            job_id=job_id,

            company=(
                opportunity[
                    "company"
                ]
            ),

            title=(
                opportunity[
                    "title"
                ]
            ),

            package_version=1,

            content_hash="",

            application_decision=(
                strategy.application_decision
            ),

            profile=profile,

            evidence_map=evidence_map,

            resume=resume,

            claims_safe=(
                approval.claims_safe
            ),

            resume_ready=(
                approval.resume_ready
            ),

            cover_letter_ready=(
                approval.cover_letter_ready
            ),

            outreach_ready=(
                approval.outreach_ready
            ),

            forbidden_claims=(
                strategy.forbidden_claims
            ),

            critical_gaps=(
                strategy.critical_gaps
            ),

            core_gaps=(
                strategy.core_gaps
            ),

            human_approval_required=True,

            approved_by_human=False,

            approved_content_hash=None,

            reviewer_notes=None,
        )

        # ----------------------------------------------------
        # Package Identity + Approval Integrity
        # ----------------------------------------------------

        existing_package = (
            load_existing_application_package(
                job_id
            )
        )

        package = prepare_package_identity(
            package,
            existing_package,
        )

        application_packages.append(
            package
        )

        # ----------------------------------------------------
        # Persist
        # ----------------------------------------------------

        save_application_package(
            package
        )

    print(
        f"Packages prepared: "
        f"{len(application_packages)}"
    )

    # ========================================================
    # 7. HUMAN APPROVAL
    # ========================================================

    print()
    print("[8/9] Human Approval")

    for package in application_packages:

        print()

        print(
            f"  {package.job_id} | "
            f"{package.company} | "
            f"{package.title}"
        )

        print(
            f"    Decision: "
            f"{package.application_decision}"
        )

        print(
            f"    Package version: "
            f"{package.package_version}"
        )

        print(
            f"    Status: "
            f"{package.status.value}"
        )

        print(
            f"    Resume ready: "
            f"{package.resume_ready}"
        )

        print(
            f"    Claims safe: "
            f"{package.claims_safe}"
        )

        print(
            f"    Evidence mappings: "
            f"{len(package.evidence_map)}"
        )

        print(
            f"    Human approval required: "
            f"{package.human_approval_required}"
        )

        print(
            f"    Approved by human: "
            f"{package.approved_by_human}"
        )

        print(
            f"    Content hash: "
            f"{package.content_hash[:12]}..."
        )

        if package.approved_content_hash:
            print(
                f"    Approved hash: "
                f"{package.approved_content_hash[:12]}..."
            )

    # ========================================================
    # 8. EXTERNAL ACTION AUTHORIZATION PREPARATION
    # ========================================================

    print()
    print("[9/9] External Action Authorization")

    execution_authorizations = []

    for package in application_packages:

        authorization = build_execution_authorization(
            package
        )

        save_execution_authorization(
            authorization
        )

        execution_authorizations.append(
            authorization
        )

        print()
        print(
            f"  {authorization.job_id} | "
            f"{authorization.company} | "
            f"{authorization.title}"
        )
        print(
            f"    Authorization status: "
            f"{authorization.authorization_status}"
        )
        print(
            f"    Application authorized: "
            f"{authorization.application_submission_authorized}"
        )
        print(
            f"    Outreach authorized: "
            f"{authorization.outreach_authorized}"
        )

    print()
    print(
        "No external applications or outreach "
        "were sent."
    )

    print(
        "Application approval is valid only "
        "for the approved content hash."
    )

    print(
        "If application content changes, "
        "human approval is required again."
    )

    print(
        "Explicit authorization is required "
        "before any external action."
    )

    print()

    print("=" * 80)
    print("CAREEROS PIPELINE COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    run_careeros()
