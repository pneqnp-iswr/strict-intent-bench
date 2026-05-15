from __future__ import annotations

import argparse
import json
import re
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

CATEGORIES = {
    "quoted_reply",
    "short_fragment",
    "acknowledgment_or_correction",
    "clear_direct",
}

AMBIGUITY_LEVELS = {"low", "medium", "high"}
PENDING_CONTEXT_STRENGTHS = {"none", "weak", "strong"}
WEAK_SUCCESS_PHRASES = {
    "be helpful",
    "answer well",
    "do the right thing",
    "understand the user",
    "respond appropriately",
}

# Legacy acceptable_actions values are intentionally coarser than v0.3 expected_action.
# This map prevents false-positive warnings such as ask_clarification not matching "clarify".
EXPECTED_TO_ACCEPTABLE_ALIASES = {
    "answer_directly": {"answer", "direct_answer", "answer_directly"},
    "ask_clarification": {"clarify", "ask_clarification", "ask"},
    "acknowledge_correction": {"acknowledge", "acknowledge_correction"},
    "continue_pending_task": {"answer", "continue", "continue_pending_task"},
    "avoid_unasked_execution": {"clarify", "acknowledge", "refuse", "avoid_unasked_execution"},
}


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


def compact_messages(messages: Any) -> str:
    if not isinstance(messages, list):
        return ""
    parts: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", ""))
        content = re.sub(r"\s+", " ", str(message.get("content", "")).strip().lower())
        parts.append(f"{role}:{content}")
    return "\n".join(parts)


def add_issue(issues: list[dict[str, str]], severity: str, case_id: str, message: str) -> None:
    issues.append({"severity": severity, "case_id": case_id, "message": message})


def acceptable_action_matches(expected_action: Any, acceptable_actions: Any) -> bool:
    if expected_action is None or not isinstance(acceptable_actions, list):
        return True
    normalized = {str(action).strip().lower() for action in acceptable_actions}
    allowed = EXPECTED_TO_ACCEPTABLE_ALIASES.get(str(expected_action), {str(expected_action)})
    return bool(normalized & allowed)


def audit_case(item: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    case_id = str(item.get("id", f"line:{item.get('__line__', '?')}"))
    category = item.get("category")
    expected_action = item.get("expected_action")
    ambiguity_level = item.get("ambiguity_level")
    pending_context_strength = item.get("pending_context_strength")
    acceptable_actions = item.get("acceptable_actions")
    success_criteria = str(item.get("success_criteria", "")).strip()
    notes = str(item.get("notes", "")).strip()
    messages = item.get("messages")

    if category not in CATEGORIES:
        add_issue(issues, "error", case_id, f"unknown category: {category!r}")

    if expected_action is not None and expected_action not in EXPECTED_ACTIONS:
        add_issue(issues, "error", case_id, f"unknown expected_action: {expected_action!r}")

    if ambiguity_level is not None and ambiguity_level not in AMBIGUITY_LEVELS:
        add_issue(issues, "error", case_id, f"unknown ambiguity_level: {ambiguity_level!r}")

    if pending_context_strength is not None and pending_context_strength not in PENDING_CONTEXT_STRENGTHS:
        add_issue(issues, "error", case_id, f"unknown pending_context_strength: {pending_context_strength!r}")

    if not isinstance(acceptable_actions, list) or not acceptable_actions:
        add_issue(issues, "error", case_id, "acceptable_actions must be a non-empty list")
    elif len(acceptable_actions) > 3:
        add_issue(issues, "warning", case_id, "acceptable_actions is broad; check that this does not hide wrong-intent errors")

    if len(success_criteria) < 40:
        add_issue(issues, "warning", case_id, "success_criteria is short; check that it is specific enough to grade")

    success_lower = success_criteria.lower()
    for phrase in WEAK_SUCCESS_PHRASES:
        if phrase in success_lower:
            add_issue(issues, "warning", case_id, f"success_criteria contains weak phrase: {phrase!r}")

    if not acceptable_action_matches(expected_action, acceptable_actions):
        add_issue(issues, "warning", case_id, "expected_action does not align with acceptable_actions aliases")

    if "notes" in item and len(notes) < 20:
        add_issue(issues, "warning", case_id, "notes field is very short")

    if isinstance(messages, list):
        user_messages = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
        if not user_messages:
            add_issue(issues, "error", case_id, "case has no user message")
        if len(messages) < 2:
            add_issue(issues, "warning", case_id, "case has fewer than two messages; context may be too thin")
    else:
        add_issue(issues, "error", case_id, "messages must be a list")

    # Heuristic consistency checks. These are not proof obligations; they flag review targets.
    if category == "clear_direct" and expected_action == "ask_clarification":
        add_issue(issues, "warning", case_id, "clear_direct with ask_clarification is unusual; check pending context")

    if category == "short_fragment" and pending_context_strength == "none" and expected_action == "answer_directly":
        add_issue(issues, "warning", case_id, "short_fragment with no pending context and answer_directly may be over-specified")

    if pending_context_strength == "strong" and expected_action == "ask_clarification":
        add_issue(issues, "warning", case_id, "strong pending context with ask_clarification may indicate over-clarification")

    if ambiguity_level == "high" and expected_action in {"answer_directly", "continue_pending_task"} and pending_context_strength != "strong":
        add_issue(issues, "warning", case_id, "high ambiguity with direct action but without strong pending context")

    if category == "acknowledgment_or_correction" and expected_action not in {None, "acknowledge_correction", "continue_pending_task", "ask_clarification"}:
        add_issue(issues, "warning", case_id, "acknowledgment_or_correction expected_action should usually acknowledge, clarify, or continue")

    return issues


def build_markdown_report(path: Path, items: list[dict[str, Any]], issues: list[dict[str, str]]) -> str:
    categories = Counter(str(item.get("category", "unspecified")) for item in items)
    expected_actions = Counter(str(item.get("expected_action", "unspecified")) for item in items)
    ambiguity = Counter(str(item.get("ambiguity_level", "unspecified")) for item in items)
    pending = Counter(str(item.get("pending_context_strength", "unspecified")) for item in items)
    severity = Counter(issue["severity"] for issue in issues)

    lines: list[str] = []
    lines.append("# Dataset Quality Audit")
    lines.append("")
    lines.append(f"Dataset: `{path}`")
    lines.append(f"Cases: **{len(items)}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"Errors: **{severity.get('error', 0)}**")
    lines.append(f"Warnings: **{severity.get('warning', 0)}**")
    lines.append("")
    lines.append("## Category balance")
    lines.append("")
    for key, value in sorted(categories.items()):
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("## Expected action balance")
    lines.append("")
    for key, value in sorted(expected_actions.items()):
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("## Ambiguity balance")
    lines.append("")
    for key, value in sorted(ambiguity.items()):
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("## Pending context balance")
    lines.append("")
    for key, value in sorted(pending.items()):
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("## Issues")
    lines.append("")
    if not issues:
        lines.append("No quality issues detected by heuristic checks.")
    else:
        for issue in issues:
            lines.append(f"- **{issue['severity']}** `{issue['case_id']}`: {issue['message']}")
    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append("This audit is heuristic. It flags cases for review; it does not replace manual judgment.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit strict-intent-bench dataset quality without API access.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, help="Optional Markdown report path.")
    parser.add_argument("--fail-on-warning", action="store_true", help="Return non-zero if warnings are found.")
    args = parser.parse_args()

    items = load_jsonl(args.dataset)
    issues: list[dict[str, str]] = []
    seen_ids: Counter[str] = Counter()
    seen_messages: defaultdict[str, list[str]] = defaultdict(list)

    for item in items:
        case_id = str(item.get("id", f"line:{item.get('__line__', '?')}"))
        seen_ids[case_id] += 1
        signature = compact_messages(item.get("messages"))
        if signature:
            seen_messages[signature].append(case_id)
        issues.extend(audit_case(item))

    for case_id, count in sorted(seen_ids.items()):
        if count > 1:
            add_issue(issues, "error", case_id, f"duplicate id appears {count} times")

    for signature, ids in seen_messages.items():
        if len(ids) > 1:
            add_issue(issues, "warning", ids[0], "duplicate message signature with: " + ", ".join(ids[1:]))

    report = build_markdown_report(args.dataset, items, issues)
    print(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote: {args.output}")

    severity = Counter(issue["severity"] for issue in issues)
    if severity.get("error", 0) > 0:
        raise SystemExit(1)
    if args.fail_on_warning and severity.get("warning", 0) > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
