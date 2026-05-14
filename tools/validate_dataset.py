from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED_ACTIONS = {
    "answer_directly",
    "ask_clarification",
    "acknowledge_correction",
    "continue_pending_task",
    "avoid_unasked_execution",
}
AMBIGUITY_LEVELS = {"low", "medium", "high"}
PENDING_CONTEXT_STRENGTHS = {"none", "weak", "strong"}
CORE_FIELDS = {"id", "title", "category", "messages", "acceptable_actions", "success_criteria"}
V03_FIELDS = {"expected_action", "ambiguity_level", "pending_context_strength", "operation_required", "notes"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}: invalid JSONL on line {line_number}: {exc}") from exc
            item["__line__"] = line_number
            items.append(item)
    return items


def validate_case(item: dict[str, Any], require_v03: bool) -> list[str]:
    errors: list[str] = []
    line = item.get("__line__", "?")
    case_id = item.get("id", f"line:{line}")

    missing = sorted(CORE_FIELDS - set(item.keys()))
    if missing:
        errors.append(f"{case_id}: missing core fields: {', '.join(missing)}")

    if require_v03:
        missing_v03 = sorted(V03_FIELDS - set(item.keys()))
        if missing_v03:
            errors.append(f"{case_id}: missing v0.3 fields: {', '.join(missing_v03)}")

    messages = item.get("messages")
    if not isinstance(messages, list) or not messages:
        errors.append(f"{case_id}: messages must be a non-empty list")
    else:
        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                errors.append(f"{case_id}: messages[{index}] must be an object")
                continue
            if message.get("role") not in {"system", "developer", "assistant", "user"}:
                errors.append(f"{case_id}: messages[{index}].role is invalid: {message.get('role')!r}")
            if not isinstance(message.get("content"), str) or not message.get("content", "").strip():
                errors.append(f"{case_id}: messages[{index}].content must be a non-empty string")

    acceptable_actions = item.get("acceptable_actions")
    if not isinstance(acceptable_actions, list) or not acceptable_actions:
        errors.append(f"{case_id}: acceptable_actions must be a non-empty list")

    expected_action = item.get("expected_action")
    if expected_action is not None and expected_action not in EXPECTED_ACTIONS:
        errors.append(f"{case_id}: invalid expected_action: {expected_action!r}")

    ambiguity_level = item.get("ambiguity_level")
    if ambiguity_level is not None and ambiguity_level not in AMBIGUITY_LEVELS:
        errors.append(f"{case_id}: invalid ambiguity_level: {ambiguity_level!r}")

    pending_context_strength = item.get("pending_context_strength")
    if pending_context_strength is not None and pending_context_strength not in PENDING_CONTEXT_STRENGTHS:
        errors.append(f"{case_id}: invalid pending_context_strength: {pending_context_strength!r}")

    if "operation_required" in item and not isinstance(item["operation_required"], bool):
        errors.append(f"{case_id}: operation_required must be boolean")

    if "notes" in item and not isinstance(item["notes"], str):
        errors.append(f"{case_id}: notes must be a string")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate strict-intent-bench JSONL datasets without using any API.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--require-v03", action="store_true", help="Require all v0.3 schema fields.")
    args = parser.parse_args()

    items = load_jsonl(args.dataset)
    errors: list[str] = []
    ids: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    expected_actions: Counter[str] = Counter()
    ambiguity: Counter[str] = Counter()
    pending: Counter[str] = Counter()
    by_category_expected: dict[str, Counter[str]] = defaultdict(Counter)

    for item in items:
        errors.extend(validate_case(item, require_v03=args.require_v03))
        if "id" in item:
            ids[str(item["id"])] += 1
        category = str(item.get("category", "unspecified"))
        categories[category] += 1
        expected = str(item.get("expected_action", "unspecified"))
        expected_actions[expected] += 1
        ambiguity[str(item.get("ambiguity_level", "unspecified"))] += 1
        pending[str(item.get("pending_context_strength", "unspecified"))] += 1
        by_category_expected[category][expected] += 1

    duplicate_ids = sorted(case_id for case_id, count in ids.items() if count > 1)
    if duplicate_ids:
        errors.append("duplicate ids: " + ", ".join(duplicate_ids))

    print(f"dataset: {args.dataset}")
    print(f"cases: {len(items)}")
    print("categories:", dict(sorted(categories.items())))
    print("expected_action:", dict(sorted(expected_actions.items())))
    print("ambiguity_level:", dict(sorted(ambiguity.items())))
    print("pending_context_strength:", dict(sorted(pending.items())))
    print("category x expected_action:")
    for category, counter in sorted(by_category_expected.items()):
        print(f"  {category}: {dict(sorted(counter.items()))}")

    if errors:
        print("\nFAILED")
        for error in errors[:100]:
            print(f"- {error}")
        if len(errors) > 100:
            print(f"... {len(errors) - 100} more errors")
        raise SystemExit(1)

    print("\nOK")


if __name__ == "__main__":
    main()
