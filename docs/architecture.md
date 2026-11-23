# Architecture and design decisions

## Selected pattern

Sentinel follows the document-intelligence pipeline from Assignment 2: intake, source-preserving page text, candidate extraction, citation validation, deterministic rule calculation, CAM review, and approved-only register. The prototype keeps each stage small and inspectable.

## Trust and control boundaries

1. The local source file is read without modification. Its SHA-256 hash and page-level text are attached to the proposal.
2. Extraction returns a candidate only. The OpenAI adapter is optional, disabled by default, and has no authority to calculate a date or approve a proposal.
3. The candidate quote must exactly match one unique page in the original document. An uncited or ambiguous candidate is rejected/abstained.
4. The rule engine uses only the CAM-entered actual receipt date, evidence description, and explicitly confirmed pilot profile. Missing inputs produce no due date.
5. `LocalStore.review` is the only activation path. The reviewer must provide a name and attest to the role `licensed CAM`.
6. The active register includes only `approved` items. Completion requires an existing local evidence file.
7. The prototype has no outbound communications, filing, legal interpretation, or engineering judgment features.

## Data flow

`source file -> SourceDocument -> extractor -> exact citation check -> Candidate -> rule result -> LocalStore -> review event -> approved register`

The model never receives association state, receipt evidence, or other records. If the optional model path is enabled, it receives only the selected source text and extraction instructions. For this course, inputs must be synthetic or public.

## Decisions and known gaps

- **One obligation class:** only the 14-day owner-notice obligation is in the first end-to-end slice; all other classes remain deferred.
- **Actual receipt date:** use the CAM-entered receipt date, never the notice issue date.
- **Calendar arithmetic:** the rule proposes receipt date + 14 calendar days. The date is a candidate for review, not a legal determination.
- **Simple local store:** JSON proposal state and JSONL audit events support a single-user demo. They do not provide tamper-proof audit, access control, backup, encryption at rest, or 15-year retention.
- **Scanned pages:** pages with no extracted text are explicitly listed as exceptions. OCR is not implemented in this increment.
- **Jurisdiction:** the included Palm Beach County label is a demo-only profile marker, not a verified production configuration.
- **AI evaluation:** the optional model adapter is tested with a fake response client, not measured on a labeled real-world corpus.
