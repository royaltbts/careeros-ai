import json
from pathlib import Path

from app.claim_safety import run_safety_gate
from app.models.application_package import ApplicationPackage
from app.models.opportunity_status import OpportunityStatus
from app.opportunity_workflow import transition_status


APPLICATION_DIR = Path("data/jobs/applications")


def load_application_package(job_id: str) -> ApplicationPackage:
    """
    Load a persisted application package.
    """

    file_path = APPLICATION_DIR / f"{job_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Application package not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return ApplicationPackage.model_validate(data)


def save_application_package(
    package: ApplicationPackage
) -> None:
    """
    Persist the updated application package.
    """

    file_path = APPLICATION_DIR / f"{package.job_id}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            package.model_dump(mode="json"),
            file,
            indent=2
        )

    print()
    print(f"Application package saved: {file_path}")


def display_bullets(
    package: ApplicationPackage
) -> None:
    """
    Display the current tailored resume bullets.
    """

    print()
    print("=" * 80)
    print("CURRENT RESUME CLAIMS")
    print("=" * 80)

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


def validate_edited_claim(
    package: ApplicationPackage,
    evidence_ids: list[str],
    new_text: str
):
    """
    Run the complete claim safety and fidelity gate
    against an edited claim.
    """

    return run_safety_gate(
        package.job_id,
        [
            {
                "claim": new_text,
                "evidence_ids": evidence_ids
            }
        ]
    )


def edit_bullet(
    package: ApplicationPackage,
    bullet_number: int,
    new_text: str
) -> bool:
    """
    Edit one resume bullet.

    The edited claim must pass the claim safety gate.

    If the package was APPROVED, the edit moves it back
    to PENDING_APPROVAL through the central state machine.

    Human approval is always reset after an edit.
    """

    index = bullet_number - 1

    if index < 0 or index >= len(package.resume.bullets):
        print()
        print("Invalid bullet number.")
        return False

    bullet = package.resume.bullets[index]

    print()
    print("-" * 80)
    print("VALIDATING EDITED CLAIM")
    print("-" * 80)

    print()
    print("New claim:")
    print(new_text)

    safety_result = validate_edited_claim(
        package,
        bullet.evidence_ids,
        new_text
    )

    check = safety_result.checks[0]

    print()
    print(f"Evidence verified:  {check.evidence_verified}")
    print(f"Forbidden match:    {check.forbidden_match}")
    print(f"Fidelity supported: {check.fidelity_supported}")
    print(f"Fidelity reason:    {check.fidelity_reason}")
    print(f"Allowed:            {check.allowed}")
    print(f"Reason:             {check.reason}")

    if not check.allowed:

        print()
        print("=" * 80)
        print("EDIT BLOCKED")
        print("=" * 80)

        print()
        print(
            "The edited claim is not sufficiently supported "
            "by the available evidence."
        )

        print()
        print("The original claim has NOT been changed.")

        return False

    original_status = package.status

    if original_status == OpportunityStatus.APPROVED:

        package.status = transition_status(
            original_status,
            OpportunityStatus.PENDING_APPROVAL
        )

    elif original_status == OpportunityStatus.PENDING_APPROVAL:

        package.status = original_status

    else:

        print()
        print("=" * 80)
        print("EDIT BLOCKED")
        print("=" * 80)

        print()
        print(
            f"Claims cannot be edited from status "
            f"{original_status.value}."
        )

        return False

    bullet.bullet = new_text
    bullet.allowed = True
    bullet.human_review_required = True

    package.claims_safe = True

    # Any edit invalidates previous human approval.
    package.approved_by_human = False

    package.reviewer_notes = (
        "Resume claim edited by human reviewer. "
        "Claim safety and fidelity validation passed. "
        "Human approval is required again."
    )

    save_application_package(package)

    print()
    print("=" * 80)
    print("EDIT ACCEPTED")
    print("=" * 80)

    print()
    print(
        "The edited claim passed the safety and fidelity checks."
    )

    print()
    print(
        f"Status: {package.status.value}"
    )

    print()
    print(
        "Previous human approval has been reset."
    )

    print()
    print(
        "The application requires human approval again."
    )

    return True


def main() -> None:

    print()
    print("=" * 80)
    print("CAREEROS — REVIEW EDITOR")
    print("=" * 80)

    job_id = input(
        "\nEnter Job ID "
        "(example: JOB-001): "
    ).strip().upper()

    if not job_id:
        print("No Job ID provided.")
        return

    try:
        package = load_application_package(job_id)

    except FileNotFoundError as error:
        print()
        print(f"ERROR: {error}")
        return

    display_bullets(package)

    print()
    print("=" * 80)
    print("EDIT RESUME CLAIM")
    print("=" * 80)

    bullet_input = input(
        "\nEnter bullet number to edit "
        "(or X to exit): "
    ).strip().upper()

    if bullet_input == "X":
        print()
        print("No changes made.")
        return

    try:
        bullet_number = int(bullet_input)

    except ValueError:
        print()
        print("Invalid bullet number.")
        return

    new_text = input(
        "\nEnter the new claim text:\n"
    ).strip()

    if not new_text:
        print()
        print("Empty claim rejected.")
        return

    edit_bullet(
        package,
        bullet_number,
        new_text
    )


if __name__ == "__main__":
    main()
