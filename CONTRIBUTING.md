# Contributing

This repository is a course prototype. Keep changes within the documented scope unless the decision record and traceability matrix are updated.

## Before proposing a change

1. Open an issue describing the user need and affected requirement IDs.
2. Keep sample material synthetic or public. Never add association records, personal information, credentials, or API keys.
3. Keep extraction, rule calculation, and human approval as separate stages.
4. Preserve source quotes and page references. Do not accept a candidate whose citation does not resolve exactly to the source.
5. Add or update tests and document observed results and limitations.

## Local checks

```bash
python -m pip install -e ".[dev]"
pytest
```

Pull requests should explain the behavior changed, the requirements affected, validation performed, and any remaining risks. A reviewer must inspect generated code and outputs; model output is not accepted as validation evidence by itself.
