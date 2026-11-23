# Validation record

## Automated evidence

The unit tests cover hand-calculated date arithmetic, missing or invalid receipt inputs, source quote resolution, ambiguous clauses, approval bypass, approved-only register behavior, and completion evidence. Tests use synthetic data and do not call a model API.

## Manual demonstration path

1. Run the offline demo in the README.
2. Confirm the output contains the synthetic source name, page 1, verbatim quote, actual receipt date, arithmetic, due date, and `proposed` state.
3. Run `sentinel register`; it should be empty before approval.
4. Review the source quote, then approve using the licensed-CAM role attestation.
5. Run `sentinel register`; the approved candidate should appear.
6. Attempt approval with missing receipt evidence or an unverified profile; the system should abstain and block approval.
7. Attempt completion with a nonexistent evidence path; completion should be rejected.

## Current results and limits

Run on November 23, 2026 with Python 3.12 using `pytest`: **13 passed**. The test suite uses a fake model response and does not call an external model API. The offline CLI demo produced a cited proposal dated 2026-11-15 from the synthetic receipt date 2026-11-01; the proposal remained `proposed` until a reviewer decision.

No interview, real-notice evaluation, OCR evaluation, precision/recall study, penetration test, multi-user access test, or 15-year retention test has been performed. A classroom test does not establish legal compliance or production reliability.
