from __future__ import annotations

import argparse
import os
import sys

from .core import (LocalClauseExtractor, LocalStore, OpenAIClauseExtractor, SentinelError,
                   build_proposal, candidate_json, read_document)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="sentinel", description="Cited, human-reviewed notice prototype")
    root.add_argument("--state-dir", default=".sentinel", help="Local demo state directory (default: .sentinel)")
    sub = root.add_subparsers(dest="command", required=True)

    propose = sub.add_parser("propose", help="Read a source and create a reviewable proposal")
    propose.add_argument("--source", required=True)
    propose.add_argument("--association-id", required=True)
    propose.add_argument("--jurisdiction", required=True)
    propose.add_argument("--profile-verified", action="store_true", help="Confirm demo profile was verified by a human")
    propose.add_argument("--receipt-date", help="CAM-recorded actual receipt date, YYYY-MM-DD")
    propose.add_argument("--receipt-evidence", help="Local evidence description/path for actual receipt date")
    propose.add_argument("--extractor", choices=["local", "openai"], default="local")
    propose.add_argument("--confirm-synthetic-or-public-text", action="store_true")

    review = sub.add_parser("review", help="Approve or reject a proposal")
    review.add_argument("proposal_id")
    review.add_argument("--decision", required=True, choices=["approve", "reject"])
    review.add_argument("--reviewer", required=True)
    review.add_argument("--role", required=True)

    register = sub.add_parser("register", help="List active approved obligations")
    complete = sub.add_parser("complete", help="Complete an approved item with local evidence")
    complete.add_argument("proposal_id")
    complete.add_argument("--evidence", required=True)
    sub.add_parser("proposals", help="List proposals and their review states")
    return root


def main() -> None:
    args = parser().parse_args()
    store = LocalStore(args.state_dir)
    try:
        if args.command == "propose":
            document = read_document(args.source)
            if args.extractor == "openai":
                if not args.confirm_synthetic_or_public_text:
                    raise SentinelError("External extraction requires --confirm-synthetic-or-public-text")
                key, model = os.getenv("OPENAI_API_KEY"), os.getenv("SENTINEL_MODEL")
                if not key or not model:
                    raise SentinelError("Set OPENAI_API_KEY and SENTINEL_MODEL in your local environment")
                try:
                    from openai import OpenAI
                except ImportError as exc:
                    raise SentinelError("Install the optional dependency with: pip install -e '.[ai]'") from exc
                extractor = OpenAIClauseExtractor(OpenAI(api_key=key), model)
            else:
                extractor = LocalClauseExtractor()
            extracted = extractor.extract(document)
            candidate = build_proposal(document, extracted, association_id=args.association_id,
                                       jurisdiction=args.jurisdiction, profile_verified=args.profile_verified,
                                       receipt_date=args.receipt_date, receipt_evidence=args.receipt_evidence)
            store.save(candidate, "proposal_created", "system", f"rule={candidate.rule_id}; model={args.extractor}")
            print(candidate_json(candidate))
        elif args.command == "review":
            item = store.review(args.proposal_id, args.decision, args.reviewer, args.role)
            print(candidate_json(item))
        elif args.command == "register":
            print(candidate_json_list([item for item in store.all() if item.state == "approved"]))
        elif args.command == "complete":
            print(candidate_json(store.complete(args.proposal_id, args.evidence)))
        elif args.command == "proposals":
            print(candidate_json_list(store.all()))
    except SentinelError as exc:
        print(f"Sentinel abstained: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def candidate_json_list(items) -> str:
    import json
    from dataclasses import asdict
    return json.dumps([asdict(item) for item in items], indent=2)


if __name__ == "__main__":
    main()
