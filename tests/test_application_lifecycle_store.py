from app.application_crm_store import load_application_record, save_application_record
from app.application_lifecycle import transition_application
from app.models.application_record import ApplicationRecord
from app.models.opportunity_status import OpportunityStatus


def make_record():
    return ApplicationRecord(
        job_id="TEST-LIFECYCLE-STORE-001",
        company="Test Company",
        title="Customer Success Manager",
        package_version=1,
        content_hash="test-hash",
        application_status="APPROVED",
    )


def test_transition_persists_status_and_history(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.application_crm_store.CRM_DIR",
        tmp_path,
    )

    record = make_record()

    transition_application(record, OpportunityStatus.APPLIED)
    save_application_record(record)

    loaded = load_application_record(record.job_id)

    assert loaded.application_status == "APPLIED"
    assert len(loaded.history) == 1
    assert loaded.history[0].event_type == "STATUS_CHANGE"
    assert loaded.history[0].from_status == "APPROVED"
    assert loaded.history[0].to_status == "APPLIED"
