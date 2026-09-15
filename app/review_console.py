import json
from pathlib import Path

from app.claim_safety import run_safety_gate
from app.package_integrity import calculate_content_hash
from app.models.application_package import ApplicationPackage
from app.models.opportunity_status import OpportunityStatus
from app.opportunity_workflow import transition_status
from app.opportunity_decision_store import load_opportunity_decision
from app.opportunity_decision_audit_store import load_opportunity_decision_audit
from app.application_effort_store import load_application_effort
from app.decision_explanation import build_decision_explanation_for_job
from app.supervisor_decision_store import load_supervisor_decisions


APPLICATION_DIR = Path("data/jobs/applications")


def load_application_package(
    job_id: str,
) -> ApplicationPackage:
    file_path = APPLICATION_DIR / f"{job_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Application package not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    return ApplicationPackage.model_validate(data)

def display_decision_history(package: ApplicationPackage) -> None:
    print()
    print("-" * 80)
    print("DECISION HISTORY")
    print("-" * 80)

    try:
        history = load_opportunity_decision_audit(
            package.job_id
        )
    except FileNotFoundError:
        print("Decision history: NOT AVAILABLE")
        return

    if not history:
        print("Decision history: EMPTY")
        return

    print()

    for index, audit in enumerate(history, start=1):
        print(
            f"Decision #{index} | "
            f"{audit.recommendation} | "
            f"Score: {audit.opportunity_score} | "
            f"Priority: {audit.priority}"
        )
        print(
            f"  Recorded: "
            f"{audit.recorded_at.isoformat()}"
        )

        if audit.decision_reasons:
            for reason in audit.decision_reasons:
                print(f"  Reason: {reason}")

        print()


def display_opportunity_intelligence(
    package: ApplicationPackage,
) -> None:
    print()
    print("-" * 80)
    print("OPPORTUNITY INTELLIGENCE")
    print("-" * 80)

    try:
        decision = load_opportunity_decision(
            package.job_id
        )
    except FileNotFoundError:
        print("Opportunity decision: NOT AVAILABLE")
        return

    try:
        effort = load_application_effort(
            package.job_id
        )
    except FileNotFoundError:
        effort = None

    print()
    print(
        f"Opportunity score:       "
        f"{decision.opportunity_score}"
    )
    print(
        f"Priority:                "
        f"{decision.priority}"
    )
    print(
        f"CareerOS decision:       "
        f"{decision.recommendation}"
    )

    if effort:
        print(
            f"Recommended effort:      "
            f"{effort.effort_level}"
        )

    if decision.company_strategic_alignment is not None:
        print(
            f"Company strategic fit:   "
            f"{decision.company_strategic_alignment}"
        )

    if decision.company_research_confidence is not None:
        print(
            f"Research confidence:     "
            f"{decision.company_research_confidence}"
        )

    if decision.company_decision_ready_fit is not None:
        print(
            f"Decision-ready fit:      "
            f"{decision.company_decision_ready_fit}"
        )

    if decision.strengths:
        print()
        print("Strengths:")
        for strength in decision.strengths:
            print(f"  + {strength}")

    if decision.critical_gaps:
        print()
        print("Critical gaps:")
        for gap in decision.critical_gaps:
            print(f"  - {gap}")

    if decision.decision_reasons:
        print()
        print("Decision reasons:")
        for reason in decision.decision_reasons:
            print(f"  * {reason}")


def display_decision_explanation(
    package: ApplicationPackage,
) -> None:
    print()
    print("-" * 80)
    print("EVIDENCE-BACKED DECISION")
    print("-" * 80)

    try:
        explanation = build_decision_explanation_for_job(
            package.job_id
        )
    except Exception as exc:
        print(
            "Decision explanation: NOT AVAILABLE"
        )
        print(
            f"Reason: {type(exc).__name__}: {exc}"
        )
        return

    print()
    print(
        f"Recommendation: {explanation.recommendation}"
    )
    print(
        f"Confidence:     "
        f"{explanation.confidence_summary}"
    )

    if explanation.evidence_items:
        print()
        print("Requirement evidence:")

        for item in explanation.evidence_items:
            status = "ALLOWED" if item.allowed else "BLOCKED"
            evidence_ids = (
                ", ".join(item.evidence_ids)
                if item.evidence_ids
                else "None"
            )

            print()
            print(
                f"  {'+' if item.allowed else '-'} "
                f"{item.requirement}"
            )
            print(
                f"    Match:      {item.match_type}"
            )
            print(
                f"    Confidence: {item.confidence}"
            )
            print(
                f"    Evidence:   {evidence_ids}"
            )
            print(
                f"    Safety:     {status}"
            )

            if item.evidence_claims:
                for claim in item.evidence_claims:
                    print(
                        f"    Claim:      {claim}"
                    )

            print(
                f"    Explanation: {item.explanation}"
            )

    if explanation.critical_gaps:
        print()
        print("Critical gaps:")
        for gap in explanation.critical_gaps:
            print(f"  - {gap}")

    if explanation.transferable_opportunities:
        print()
        print("Transferable opportunities:")
        for item in explanation.transferable_opportunities:
            print(f"  ~ {item}")

    print()
    print(
        f"Human review required: "
        f"{explanation.human_review_required}"
    )


def display_supervisor_deliberation(
    package: ApplicationPackage,
) -> None:
    print()
    print("-" * 80)
    print("SUPERVISOR DELIBERATION")
    print("-" * 80)

    try:
        records = load_supervisor_decisions(
            package.job_id
        )

        if not records:
            print(
                "Supervisor deliberation: NOT AVAILABLE"
            )
            return

        supervisor_result = records[-1]

    except Exception as exc:
        print(
            "Supervisor deliberation: NOT AVAILABLE"
        )
        print(
            f"Reason: {type(exc).__name__}: {exc}"
        )
        return

    print()
    print(
        f"Supervisor recommendation: "
        f"{supervisor_result.recommendation}"
    )
    print(
        f"Supervisor confidence:     "
        f"{supervisor_result.confidence}"
    )

    if supervisor_result.findings:
        print()
        print("Supervisor findings:")
        for finding in supervisor_result.findings:
            print(
                f"  - {finding.source} | "
                f"Confidence: {finding.confidence}"
            )
            print(
                f"    {finding.finding}"
            )

    if supervisor_result.conflicts:
        print()
        print("Supervisor conflicts:")
        for conflict in supervisor_result.conflicts:
            print(
                f"  - {conflict}"
            )

    if supervisor_result.unresolved_questions:
        print()
        print("Unresolved questions:")
        for question in supervisor_result.unresolved_questions:
            print(
                f"  - {question}"
            )

    print()
    print(
        f"Human review required: "
        f"{supervisor_result.human_review_required}"
    )
    print(
        f"External action allowed: "
        f"{supervisor_result.external_action_allowed}"
    )



def display_header(
    package: ApplicationPackage
) -> None:

    print()
    print("=" * 80)
    print("CAREEROS — HUMAN REVIEW CONSOLE")
    print("=" * 80)

    print()
    print(f"JOB ID:       {package.job_id}")
    print(f"COMPANY:      {package.company}")
    print(f"ROLE:         {package.title}")

    display_decision_history(
        package
    )

    display_opportunity_intelligence(
        package
    )

    display_decision_explanation(
        package
    )
    display_supervisor_deliberation(
        package
    )

    print(f"STATUS:       {package.status.value}")
    print(f"DECISION:     {package.application_decision}")

    print()
    print("-" * 80)
    print("READINESS")
    print("-" * 80)

    print(
        f"Claims safe:             {package.claims_safe}"
    )
    print(
        f"Resume ready:            {package.resume_ready}"
    )
    print(
        f"Cover letter ready:      {package.cover_letter_ready}"
    )
    print(
        f"Outreach ready:          {package.outreach_ready}"
    )
    print(
        f"Human approval required: "
        f"{package.human_approval_required}"
    )
    print(
        f"Approved by human:       "
        f"{package.approved_by_human}"
    )

    if package.approved_by_human:
        integrity = approval_integrity_valid(package)
        print(
            f"Approval integrity:      "
            f"{'VALID' if integrity else 'INVALID'}"
        )
    else:
        print(
            "Approval integrity:      NOT APPROVED"
        )


def display_resume(
    package: ApplicationPackage
) -> None:

    print()
    print("-" * 80)
    print("TAILORED RESUME")
    print("-" * 80)

    print()
    print(f"Headline: {package.resume.headline}")

    print()
    print("Summary:")
    print(package.resume.summary)

    print()
    print("Resume Claims:")

    for index, bullet in enumerate(
        package.resume.bullets,
        start=1
    ):

        print()
        print(f"[{index}] {bullet.bullet}")
        print(f"    Requirement: {bullet.requirement}")
        print(f"    Evidence:    {bullet.evidence_ids}")
        print(f"    Confidence:  {bullet.confidence}")
        print(f"    Allowed:     {bullet.allowed}")


def display_evidence_map(
    package: ApplicationPackage
) -> None:

    print()
    print("-" * 80)
    print("EVIDENCE MAP")
    print("-" * 80)

    if not package.evidence_map:
        print("No evidence mappings.")
        return

    for index, mapping in enumerate(
        package.evidence_map,
        start=1
    ):

        print()
        print(
            f"[{index}] Requirement: "
            f"{mapping.requirement}"
        )

        print(
            f"    Match type:   "
            f"{mapping.match_type}"
        )

        print(
            f"    Confidence:   "
            f"{mapping.confidence}"
        )

        print(
            f"    Evidence IDs: "
            f"{mapping.evidence_ids}"
        )

        print(
            f"    Allowed:      "
            f"{mapping.allowed}"
        )

        print(
            f"    Suggested:    "
            f"{mapping.suggested_claim}"
        )


def display_safety(
    package: ApplicationPackage
) -> None:

    print()
    print("-" * 80)
    print("SAFETY / RISK")
    print("-" * 80)

    print()
    print(f"Claims safe: {package.claims_safe}")

    print()
    print("Forbidden claims:")

    if package.forbidden_claims:

        for claim in package.forbidden_claims:
            print(f"  - {claim}")

    else:
        print("  None")

    print()
    print("Critical gaps:")

    if package.critical_gaps:

        for gap in package.critical_gaps:
            print(f"  - {gap}")

    else:
        print("  None")

    print()
    print("Core gaps:")

    if package.core_gaps:

        for gap in package.core_gaps:
            print(f"  - {gap}")

    else:
        print("  None")


def edit_resume_claim(
    package: ApplicationPackage
) -> None:

    if package.status not in [
        OpportunityStatus.PENDING_APPROVAL,
        OpportunityStatus.APPROVED
    ]:

        print()
        print(
            "Editing is only allowed from "
            "PENDING_APPROVAL or APPROVED."
        )

        return

    display_resume(package)

    print()
    print("-" * 80)
    print("EDIT RESUME CLAIM")
    print("-" * 80)

    bullet_input = input(
        "\nEnter bullet number "
        "(or X to cancel): "
    ).strip().upper()

    if bullet_input == "X":
        print()
        print("Edit cancelled.")
        return

    try:
        bullet_number = int(bullet_input)

    except ValueError:

        print()
        print("Invalid bullet number.")
        return

    index = bullet_number - 1

    if index < 0 or index >= len(package.resume.bullets):

        print()
        print("Invalid bullet number.")
        return

    bullet = package.resume.bullets[index]

    print()
    print("Current claim:")
    print(bullet.bullet)

    new_text = input(
        "\nEnter new claim text:\n"
    ).strip()

    if not new_text:

        print()
        print("Empty claim rejected.")
        return

    print()
    print("-" * 80)
    print("VALIDATING EDIT")
    print("-" * 80)

    safety_result = run_safety_gate(
        package.job_id,
        [
            {
                "claim": new_text,
                "evidence_ids": bullet.evidence_ids
            }
        ]
    )

    check = safety_result.checks[0]

    print()
    print(
        f"Evidence verified:  "
        f"{check.evidence_verified}"
    )

    print(
        f"Forbidden match:    "
        f"{check.forbidden_match}"
    )

    print(
        f"Fidelity supported: "
        f"{check.fidelity_supported}"
    )

    print(
        f"Fidelity reason:    "
        f"{check.fidelity_reason}"
    )

    print(
        f"Allowed:            "
        f"{check.allowed}"
    )

    if not check.allowed:

        print()
        print("=" * 80)
        print("EDIT BLOCKED")
        print("=" * 80)

        print()
        print(
            "The edited claim failed the "
            "safety/fidelity checks."
        )

        print()
        print("Original claim remains unchanged.")

        return

    original_status = package.status

    if original_status == OpportunityStatus.APPROVED:

        package.status = transition_status(
            original_status,
            OpportunityStatus.PENDING_APPROVAL
        )

    elif original_status == OpportunityStatus.PENDING_APPROVAL:

        package.status = original_status

    bullet.bullet = new_text
    bullet.allowed = True
    bullet.human_review_required = True

    package.claims_safe = True

    # Human edits create a new application package version.
    package.package_version += 1
    package.content_hash = calculate_content_hash(package)
    package.approved_content_hash = None

    package.approved_by_human = False

    package.reviewer_notes = (
        "Resume claim edited by human reviewer. "
        "Safety and fidelity validation passed. "
        "Human approval required again."
    )

    save_application_package(package)

    print()
    print("=" * 80)
    print("EDIT ACCEPTED")
    print("=" * 80)

    print()
    print(
        "Claim passed safety and fidelity validation."
    )

    print(
        f"Status: {package.status.value}"
    )

    print(
        "Previous human approval has been reset."
    )


def approval_integrity_valid(package: ApplicationPackage) -> bool:
    """
    Verify that a human approval still applies to the current package content.
    """
    if not package.approved_by_human:
        return False

    if not package.content_hash:
        return False

    if not package.approved_content_hash:
        return False

    current_hash = calculate_content_hash(package)

    return (
        current_hash == package.content_hash
        and current_hash == package.approved_content_hash
    )


def approve_package(
    package: ApplicationPackage
) -> None:

    if package.status != OpportunityStatus.PENDING_APPROVAL:

        print()
        print(
            "Approval is only allowed from "
            "PENDING_APPROVAL."
        )

        return

    if not package.human_approval_required:

        print()
        print(
            "Approval gate configuration is invalid."
        )

        return

    if not package.claims_safe:

        print()
        print(
            "APPROVAL BLOCKED: Claims are unsafe."
        )

        return

    if not package.resume_ready:

        print()
        print(
            "APPROVAL BLOCKED: Resume is not ready."
        )

        return

    new_status = transition_status(
        package.status,
        OpportunityStatus.APPROVED
    )

    package.status = new_status
    package.approved_by_human = True
    package.approved_content_hash = package.content_hash
    package.reviewer_notes = (
        "Explicitly approved by human reviewer."
    )

    save_application_package(package)

    print()
    print("=" * 80)
    print("APPLICATION APPROVED")
    print("=" * 80)

    print()
    print(f"Status: {package.status.value}")
    print(
        f"Approved by human: "
        f"{package.approved_by_human}"
    )

    print()
    print(
        "Approval does NOT submit the application."
    )


def reject_package(
    package: ApplicationPackage
) -> None:

    if package.status != OpportunityStatus.PENDING_APPROVAL:

        print()
        print(
            "Rejection is only allowed from "
            "PENDING_APPROVAL."
        )

        return

    reason = input(
        "\nReason for rejection: "
    ).strip()

    if not reason:
        reason = "Rejected by human reviewer."

    new_status = transition_status(
        package.status,
        OpportunityStatus.REJECTED
    )

    package.status = new_status
    package.approved_by_human = False
    package.reviewer_notes = reason

    save_application_package(package)

    print()
    print("=" * 80)
    print("APPLICATION REJECTED")
    print("=" * 80)

    print()
    print(f"Status: {package.status.value}")
    print(
        f"Reviewer notes: "
        f"{package.reviewer_notes}"
    )


def display_menu() -> None:

    print()
    print("=" * 80)
    print("REVIEW MENU")
    print("=" * 80)

    print()
    print("[V] View evidence map")
    print("[R] View tailored resume")
    print("[E] Edit resume claim")
    print("[A] Approve")
    print("[D] Reject")
    print("[X] Exit")


def review_application(
    job_id: str
) -> None:

    package = load_application_package(job_id)

    while True:

        display_header(package)
        display_safety(package)
        display_menu()

        decision = input(
            "\nYour choice: "
        ).strip().upper()

        if decision == "V":

            display_evidence_map(package)

        elif decision == "R":

            display_resume(package)

        elif decision == "E":

            edit_resume_claim(package)

        elif decision == "A":

            approve_package(package)

            if package.status == OpportunityStatus.APPROVED:
                break

        elif decision == "D":

            reject_package(package)

            if package.status == OpportunityStatus.REJECTED:
                break

        elif decision == "X":

            print()
            print("No further changes made.")
            break

        else:

            print()
            print(
                "Invalid choice. "
                "Please select V, R, E, A, D or X."
            )


def main() -> None:

    print()
    print("=" * 80)
    print("CAREEROS — HUMAN REVIEW")
    print("=" * 80)

    job_id = input(
        "\nEnter Job ID "
        "(example: JOB-001): "
    ).strip().upper()

    if not job_id:

        print("No Job ID provided.")
        return

    try:

        review_application(job_id)

    except FileNotFoundError as error:

        print()
        print(f"ERROR: {error}")

    except ValueError as error:

        print()
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
