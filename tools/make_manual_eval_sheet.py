from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PROMPT = PROJECT_ROOT / "baselines" / "no_prompt" / "baseline.txt"
DEFAULT_STRICT_PROMPT = PROJECT_ROOT / "baselines" / "strict_v8" / "strict.txt"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def conversation_to_text(messages: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in messages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a no-API CSV sheet for manual or UI-based evaluation.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-prompt", type=Path, default=DEFAULT_BASELINE_PROMPT)
    parser.add_argument("--strict-prompt", type=Path, default=DEFAULT_STRICT_PROMPT)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument(
        "--mode",
        choices=["both", "baseline", "strict"],
        default="both",
        help="Which prompt condition to include in the manual sheet.",
    )
    args = parser.parse_args()

    dataset = load_jsonl(args.dataset)
    if args.max_cases > 0:
        dataset = dataset[: args.max_cases]

    prompt_by_mode = {
        "baseline": load_text(args.baseline_prompt),
        "strict": load_text(args.strict_prompt),
    }
    modes = ["baseline", "strict"] if args.mode == "both" else [args.mode]

    rows: list[dict[str, Any]] = []
    for item in dataset:
        for mode in modes:
            rows.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "category": item["category"],
                    "expected_action": item.get("expected_action", ""),
                    "ambiguity_level": item.get("ambiguity_level", ""),
                    "pending_context_strength": item.get("pending_context_strength", ""),
                    "operation_required": item.get("operation_required", ""),
                    "mode": mode,
                    "developer_prompt": prompt_by_mode[mode],
                    "conversation": conversation_to_text(item["messages"]),
                    "acceptable_actions": ", ".join(item["acceptable_actions"]),
                    "success_criteria": item["success_criteria"],
                    "case_notes": item.get("notes", ""),
                    "response": "",
                    "grade_verdict": "",
                    "grade_primary_action": "",
                    "grade_wrong_intent_inference": "",
                    "grade_unnecessary_clarification": "",
                    "grade_notes": "",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} manual-eval rows to {args.output}")
    print("Fill response + grade_* columns manually, or run tools/heuristic_grade_manual_eval.py for a weak free smoke-test grader.")


if __name__ == "__main__":
    main()
