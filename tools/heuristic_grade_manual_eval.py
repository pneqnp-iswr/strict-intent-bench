from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

QUESTION_PATTERNS = [
    r"\?",
    r"\bwhat do you mean\b",
    r"\bwhich\b",
    r"\bwhat exactly\b",
    r"\bclarify\b",
    r"\bcan you specify\b",
    r"\bdo you want me to\b",
    r"\bуточн",
    r"\bчто именно\b",
    r"\bкакой\b",
    r"\bкакую\b",
    r"\bкакое\b",
    r"\bчто ты имеешь в виду\b",
    r"\bчто сделать\b",
]
ACK_PATTERNS = [
    r"\bgot it\b",
    r"\bunderstood\b",
    r"\bthanks\b",
    r"\bcorrected\b",
    r"\byou're right\b",
    r"\bпонял\b",
    r"\bпоняла\b",
    r"\bпринял\b",
    r"\bверно\b",
    r"\bисправил\b",
    r"\bсогласен\b",
    r"\bда,? точно\b",
]
REFUSAL_PATTERNS = [
    r"\bi can't\b",
    r"\bi cannot\b",
    r"\bне могу\b",
    r"\bне буду\b",
]


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "да"}


def detect_primary_action(text: str) -> str:
    normalized = text.strip().lower()
    if not normalized:
        return "other"
    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in REFUSAL_PATTERNS):
        return "refuse"
    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in QUESTION_PATTERNS):
        # A response can answer and then ask a trailing question, but for this weak grader
        # we intentionally classify question-first behavior as clarification-heavy.
        return "clarify"
    if any(re.search(pattern, normalized, re.IGNORECASE) for pattern in ACK_PATTERNS) and len(normalized.split()) <= 25:
        return "acknowledge"
    return "answer"


def expected_action_matches(expected: str, primary: str, wrong_intent: bool) -> bool:
    if expected == "answer_directly":
        return primary == "answer" and not wrong_intent
    if expected == "continue_pending_task":
        return primary == "answer" and not wrong_intent
    if expected == "ask_clarification":
        return primary == "clarify"
    if expected == "acknowledge_correction":
        return primary == "acknowledge" and not wrong_intent
    if expected == "avoid_unasked_execution":
        return primary in {"clarify", "acknowledge", "refuse"} and not wrong_intent
    return False


def heuristic_grade(row: dict[str, str]) -> dict[str, str]:
    response = row.get("response", "")
    expected = row.get("expected_action", "")
    category = row.get("category", "")
    primary = detect_primary_action(response)

    # Conservative smoke-test heuristic, not a publication-grade judge.
    unnecessary_clarification = primary == "clarify" and expected in {
        "answer_directly",
        "continue_pending_task",
        "acknowledge_correction",
    }
    wrong_intent = False
    if expected:
        if expected in {"answer_directly", "continue_pending_task"} and primary in {"clarify", "acknowledge", "refuse"}:
            wrong_intent = primary != "clarify" or category == "clear_direct"
        elif expected == "ask_clarification" and primary != "clarify":
            wrong_intent = True
        elif expected == "acknowledge_correction" and primary not in {"acknowledge"}:
            wrong_intent = True
        elif expected == "avoid_unasked_execution" and primary == "answer":
            wrong_intent = True

    verdict = "pass" if expected and expected_action_matches(expected, primary, wrong_intent) else "fail"
    return {
        "grade_verdict": verdict,
        "grade_primary_action": primary,
        "grade_wrong_intent_inference": str(wrong_intent).lower(),
        "grade_unnecessary_clarification": str(unnecessary_clarification).lower(),
        "grade_notes": "heuristic free grader; use human/API grading for publishable results",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill grade columns in a manual eval CSV using a weak no-API heuristic grader.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite-existing", action="store_true")
    args = parser.parse_args()

    with args.input.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        raise SystemExit("No rows found.")

    for row in rows:
        if not row.get("response", "").strip():
            continue
        if row.get("grade_verdict") and not args.overwrite_existing:
            continue
        row.update(heuristic_grade(row))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    graded = sum(1 for row in rows if row.get("grade_verdict"))
    print(f"Wrote {args.output}; graded rows: {graded}/{len(rows)}")


if __name__ == "__main__":
    main()
