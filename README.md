# Sentinel

**AI-assisted statutory obligation extraction and deadline tracking for Florida condominium association managers.**

Sentinel is a course prototype for one narrow workflow: turn a synthetic building-official notice into a cited, reviewable proposal for the 14-day unit-owner notification requirement, compute a candidate due date from the CAM-recorded receipt date, and activate it only after a named licensed CAM approves it.

> **Prototype only:** Sentinel is not legal advice, a compliance determination, or production software. The demo corpus is synthetic. Do not enter confidential association records or personal information. The optional model extractor sends document text to the configured model provider and is disabled unless explicitly opted into.

## What the prototype demonstrates

- PDF or text intake with SHA-256 source fingerprinting and page-by-page text/exception accounting.
- A bounded extraction interface. The offline extractor recognizes the target clause; an optional OpenAI Responses API adapter can propose structured fields. Both must return an exact quote and page that resolve to the source.
- A deterministic, versioned 14-calendar-day rule using the actual receipt date and receipt evidence supplied by the CAM. The printed notice date is never substituted.
- Explicit `proposed`, `under_review`, `approved`, and `rejected` states. Only approved items appear in the active register.
- Approval by a named reviewer who attests to being a licensed CAM, append-only review events, and evidence-required completion.
- Abstention when the source quote is not verifiable, the receipt date/evidence is missing, or the pilot profile is not verified.

## Architecture

```text
Notice + receipt evidence
  -> intake (hash, pages, text or explicit exceptions)
  -> candidate extraction (offline or opt-in model)
  -> exact quote/page validator
  -> deterministic rule engine (receipt date + 14 calendar days)
  -> human review and append-only event log
  -> approved-only register
```

The model cannot calculate dates, decide legal applicability, approve, complete, or send anything. There is no email, filing, or external-send capability. The repository's sample jurisdiction profile is demo configuration only and must not be treated as verified for a real association.

## Requirements traceability

| Assignment 1/2 requirement | Prototype evidence |
|---|---|
| FR-01: page text or visible exception | `sentinel.intake.read_document`; intake tests |
| FR-02: required metadata and no assumed receipt date | `build_proposal`; missing-input tests |
| FR-04/06: discrete candidate with exact page citation | `sentinel.extraction`; quote/page validation tests |
| FR-05: deterministic date from statutory trigger | `sentinel.rules`; hand-calculated date tests |
| FR-07/08: abstention and human approval gate | `sentinel.workflow.review`; bypass tests |
| FR-13: review history | JSONL event log; transition tests |
| FR-17: completion evidence | `sentinel.workflow.complete`; missing-evidence test |
| FR-18/NFR-08: professional authority boundary | CLI role check; code inspection; no send methods |

The remaining Assignment 1/2 requirements are explicitly out of scope for this first slice. See [`docs/traceability.md`](docs/traceability.md).

## Prerequisites and setup

- Python 3.11 or later
- `pip`
- Optional: an OpenAI API key and an account-supported model name, only for the opt-in extractor

```bash
git clone https://github.com/dhanushkarthikeya1/se_project.git
cd se_project
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Run the offline synthetic demo

This uses only the included fictional notice and does not make a network request:

```bash
sentinel propose \
  --source examples/synthetic_notice.txt \
  --association-id demo-association \
  --jurisdiction "Palm Beach County, Florida" \
  --profile-verified \
  --receipt-date 2026-11-01 \
  --receipt-evidence "Synthetic receipt log entry"
```

The output shows the proposed date, arithmetic, source page/quote, and proposal ID. Inspect it before approving:

```bash
sentinel review PROPOSAL_ID \
  --decision approve \
  --reviewer "Demo Reviewer" \
  --role "licensed CAM"
sentinel register
```

Replace `PROPOSAL_ID` with the ID printed by `sentinel propose`. The demo date is illustrative only. Local state and audit events are written under `.sentinel/`, which is ignored by Git.

To see abstention, omit `--profile-verified` or use a missing receipt date/evidence. A proposal without a computed due date cannot be approved. `sentinel complete PROPOSAL_ID --evidence PATH` requires a real local evidence file; it does not send or upload it.

## Optional model-assisted extraction

The model path is opt-in and may only be used with synthetic or public text for this coursework prototype. Install the optional dependency, configure the key and model in your local shell, then explicitly pass the opt-in flag:

```bash
python -m pip install -e ".[ai]"
export OPENAI_API_KEY="your-key"
export SENTINEL_MODEL="a-model-available-to-your-account"
sentinel propose --source examples/synthetic_notice.txt \
  --association-id demo-association \
  --jurisdiction "Palm Beach County, Florida" --profile-verified \
  --receipt-date 2026-11-01 --receipt-evidence "Synthetic receipt log entry" \
  --extractor openai --confirm-synthetic-or-public-text
```

The application sends only the selected source text and extraction instructions, uses `store=False`, and validates the model's quote against the local source before accepting a candidate. A matching schema is not proof that an extraction is correct; a CAM must inspect the source and proposal.

## Test and evaluate

```bash
python -m pip install -e ".[dev]"
pytest
```

The tests use synthetic text/PDF inputs and a fake model client. They do not make API calls. See [`docs/validation.md`](docs/validation.md) for the current evidence record and limits.

## Data, privacy, and security

- Use only synthetic or public inputs in the class prototype. Do not commit real association records, personal information, credentials, API keys, or local state.
- `.sentinel/`, `.env`, PDF samples, and generated state are ignored by Git.
- Keep the original source file; the stored SHA-256 value is a provenance fingerprint, not proof of authenticity.
- Model-assisted extraction is off by default and requires a separate confirmation flag.
- See [`SECURITY.md`](SECURITY.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Sources

- Florida Legislature, [2026 Florida Statutes § 553.899(5)](https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0500-0599/0553/Sections/0553.899.html), checked November 22, 2026 for this prototype's target clause. Rule wording and applicability must be rechecked before any non-class use.
- OpenAI, [Responses API: create a model response](https://developers.openai.com/api/reference/python/resources/responses/methods/create) and [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## AI assistance and limitations

AI assistance was used to translate the Assignment 1/2 design into a bounded implementation plan, draft candidate code and tests, and improve documentation. The developer must review and validate all output. No real records were used. The project does not yet implement OCR, persistent document storage/retention controls, authentication or multi-user authorization, correction workflows, portfolio views, reminders, or real stakeholder evaluation. The model path has not been evaluated against a labeled corpus. This prototype is not production-ready and does not establish legal compliance.

## License

MIT. See [`LICENSE`](LICENSE).
