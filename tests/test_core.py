import json
from types import SimpleNamespace

import pytest

from sentinel.core import (CitationError, LocalClauseExtractor, LocalStore, OpenAIClauseExtractor,
                           SentinelError, build_proposal, calculate_due_date, read_document)


def fixture_document(tmp_path, body):
    path = tmp_path / "notice.txt"
    path.write_text(body, encoding="utf-8")
    return read_document(path)


CLAUSE = ("The association must notify the unit owners of the required milestone inspection "
          "within 14 days after receipt of this written notice.")


def test_due_date_uses_actual_receipt_plus_14_calendar_days():
    due, arithmetic, reason = calculate_due_date("2026-11-01", "receipt log", True)
    assert due == "2026-11-15"
    assert arithmetic == "2026-11-01 + 14 calendar days = 2026-11-15"
    assert reason is None


@pytest.mark.parametrize("receipt,evidence,verified", [
    (None, "receipt", True), ("2026-11-01", None, True), ("2026-11-01", "receipt", False),
    ("not-a-date", "receipt", True),
])
def test_missing_or_invalid_input_abstains(receipt, evidence, verified):
    due, arithmetic, reason = calculate_due_date(receipt, evidence, verified)
    assert due is None and arithmetic is None and reason


def test_local_extractor_requires_exact_cited_clause(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)
    extracted = LocalClauseExtractor().extract(document)
    proposal = build_proposal(document, extracted, association_id="demo", jurisdiction="Palm Beach County, Florida",
                              profile_verified=True, receipt_date="2026-11-01", receipt_evidence="synthetic record")
    assert proposal.page == 1
    assert proposal.quote == CLAUSE
    assert proposal.due_date == "2026-11-15"
    assert proposal.state == "proposed"
    assert proposal.rule_source.startswith("https://www.leg.state.fl.us/")
    assert proposal.rule_verified_on == "2026-11-22"


def test_uncited_quote_is_rejected(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)
    extracted = LocalClauseExtractor().extract(document)
    extracted["quote"] = "The model made this up."
    with pytest.raises(CitationError):
        build_proposal(document, extracted, association_id="demo", jurisdiction="Palm Beach County, Florida",
                       profile_verified=True, receipt_date="2026-11-01", receipt_evidence="synthetic record")


def test_ambiguous_clauses_require_review(tmp_path):
    document = fixture_document(tmp_path, CLAUSE + "\n" + CLAUSE)
    with pytest.raises(SentinelError):
        LocalClauseExtractor().extract(document)


def test_under_review_cannot_be_approved(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)
    proposal = build_proposal(document, LocalClauseExtractor().extract(document), association_id="demo",
                              jurisdiction="Palm Beach County, Florida", profile_verified=False,
                              receipt_date="2026-11-01", receipt_evidence="synthetic record")
    store = LocalStore(tmp_path / "state")
    store.save(proposal, "proposal_created")
    with pytest.raises(SentinelError):
        store.review(proposal.id, "approve", "Reviewer", "licensed CAM")


def test_only_named_licensed_cam_can_approve_and_register_is_approved_only(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)
    proposal = build_proposal(document, LocalClauseExtractor().extract(document), association_id="demo",
                              jurisdiction="Palm Beach County, Florida", profile_verified=True,
                              receipt_date="2026-11-01", receipt_evidence="synthetic record")
    store = LocalStore(tmp_path / "state")
    store.save(proposal, "proposal_created")
    with pytest.raises(SentinelError):
        store.review(proposal.id, "approve", "Reviewer", "student")
    approved = store.review(proposal.id, "approve", "Reviewer", "licensed CAM")
    assert approved.state == "approved"
    assert [item.id for item in store.all() if item.state == "approved"] == [proposal.id]
    assert len(store.events_path.read_text().splitlines()) == 2


def test_completion_requires_existing_evidence(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)
    proposal = build_proposal(document, LocalClauseExtractor().extract(document), association_id="demo",
                              jurisdiction="Palm Beach County, Florida", profile_verified=True,
                              receipt_date="2026-11-01", receipt_evidence="synthetic record")
    store = LocalStore(tmp_path / "state")
    store.save(proposal, "proposal_created")
    store.review(proposal.id, "approve", "Reviewer", "licensed CAM")
    with pytest.raises(SentinelError):
        store.complete(proposal.id, str(tmp_path / "missing.pdf"))
    proof = tmp_path / "evidence.txt"
    proof.write_text("synthetic proof", encoding="utf-8")
    assert store.complete(proposal.id, str(proof)).state == "completed"


def test_model_adapter_uses_structured_candidate_and_source_validation(tmp_path):
    document = fixture_document(tmp_path, CLAUSE)

    class FakeResponses:
        def create(self, **kwargs):
            assert kwargs["store"] is False
            assert kwargs["text"]["format"]["type"] == "json_schema"
            payload = {"found": True, "page": 1, "quote": CLAUSE,
                       "obligated_party": "Association", "action": "Notify owners",
                       "trigger": "Receipt of notice", "confidence": 0.92}
            return SimpleNamespace(output_text=json.dumps(payload))

    client = SimpleNamespace(responses=FakeResponses())
    result = OpenAIClauseExtractor(client, "test-model").extract(document)
    assert result["quote"] == CLAUSE
    assert result["page"] == 1


def test_pdf_blank_page_is_reported_not_silently_skipped(tmp_path):
    from reportlab.pdfgen.canvas import Canvas

    path = tmp_path / "two-pages.pdf"
    canvas = Canvas(str(path))
    canvas.drawString(72, 720, CLAUSE)
    canvas.showPage()
    canvas.showPage()
    canvas.save()

    document = read_document(path)
    assert set(document.pages) == {1, 2}
    assert document.pages[1] == CLAUSE
    assert document.exceptions == [2]
