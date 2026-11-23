# Requirement traceability and scope

| Requirement | Status | Implementation/evidence |
|---|---|---|
| FR-01 page text/accounting | Partial | PDF/text intake emits text by page and records unreadable pages. OCR and large-corpus tests are deferred. |
| FR-02 association and receipt metadata | Partial | Association ID, jurisdiction, actual receipt date, and evidence description are required inputs; full building profile is deferred. |
| FR-03 milestone schedule / 25-year agency determination | Deferred | Not part of the narrow notice slice. |
| FR-04 discrete extraction | Partial | One 14-day target obligation; other statutory classes are out of scope. |
| FR-05 date calculation | Partial | Deterministic 14 calendar days from actual receipt; other trigger/rule classes deferred. |
| FR-06 exact citations | Implemented for slice | Exact quote must resolve uniquely to cited source page. |
| FR-07 ambiguity and abstention | Implemented for slice | Missing evidence/profile, low confidence, ambiguity, and citation failures block a usable deadline. |
| FR-08 human approval | Implemented for slice | Only a named reviewer attesting `licensed CAM` can approve. |
| FR-09 professional escalation | Deferred | No engineer/attorney workflow in this slice. |
| FR-10 through FR-12 notices, alerts, portfolio | Deferred | No drafting, scheduled alerts, or portfolio dashboard. |
| FR-13 audit | Partial | Append-only JSONL review events; not tamper-proof. |
| FR-14 retention | Deferred | No long-term document store or deletion controls. |
| FR-15 jurisdiction-specific rules | Partial | Demo profile flag only; not production verified. |
| FR-16 evidence package | Deferred | Local JSON output only. |
| FR-17 completion evidence | Partial | Completion requires a local evidence file; access/security controls are not production-grade. |
| FR-18 no legal/engineering conclusion | Implemented for slice | No conclusion, external-send, or filing feature exists. |
| NFR-05 citation / NFR-06 review gate | Implemented for slice | Source-resolution and approval-gate tests. |
| NFR-08 professional boundary | Implemented for slice | No autonomous authority or external action. |
| Other quality, security, retention, and performance requirements | Not established | Single-user classroom prototype; see [`validation.md`](validation.md). |

## Scope change from Assignment 1 to Assignment 2

Assignment 1 considered a wider initial register. Assignment 2 deliberately narrowed the first prototype to one official notice and one 14-day owner-notification obligation. This implementation preserves that decision and defers milestone schedule, multi-obligation extraction, alerts, long-term retention, and production security rather than implying they are complete.
