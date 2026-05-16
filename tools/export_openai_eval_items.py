from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}: invalid JSONL on line {line_number}: {exc}") from exc
    return rows


def export_item(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "item": {
            "id": case.get("id"),
            "title": case.get("title"),
            "category": case.get("category"),
            "conversation": case.get("messages", []),
            "acceptable_actions": case.get("acceptable_actions", []),
            "expected_action": case.get("expected_action"),
            "success_criteria": case.get("success_criteria"),
            "ambiguity_level": case.get("ambiguity_level"),
            "pending_context_strength": case.get("pending_context_strength"),
            "operation_required": case.get("operation_required"),
            "notes": case.get("notes"),
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export strict-intent-bench JSONL cases into OpenAI Evals-style JSONL items."
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = load_jsonl(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for case in rows:
            handle.write(json.dumps(export_item(case), ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"dataset: {args.dataset}")
    print(f"cases: {len(rows)}")
    print(f"wrote: {args.output}")


if __name__ == "__main__":
    main()
