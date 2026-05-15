from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
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


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def truncate(value: str, limit: int) -> str:
    value = str(value or "")
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def as_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def merge_rows(case_rows: list[dict[str, str]], dataset_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = {str(row.get("id")): row for row in dataset_rows}
    merged: list[dict[str, Any]] = []
    missing: list[str] = []

    for row in case_rows:
        case_id = str(row.get("id", ""))
        meta = metadata.get(case_id)
        if meta is None:
            missing.append(case_id)
            meta = {}
        item: dict[str, Any] = dict(row)
        for key in [
            "title",
            "category",
            "expected_action",
            "ambiguity_level",
            "pending_context_strength",
            "operation_required",
            "acceptable_actions",
            "success_criteria",
            "notes",
            "messages",
        ]:
            item[key] = meta.get(key, item.get(key, ""))
        merged.append(item)

    if missing:
        unique = ", ".join(sorted(set(missing))[:20])
        raise SystemExit(f"case_results contains ids not present in dataset: {unique}")

    return merged


def write_markdown(path: Path, rows: list[dict[str, Any]], response_limit: int) -> None:
    strict_rows = [row for row in rows if row.get("mode") == "strict"]
    strict_failures = [row for row in strict_rows if row.get("grade_verdict") == "fail"]
    counter = Counter(
        (
            str(row.get("expected_action", "")),
            str(row.get("grade_primary_action", "")),
            str(row.get("grade_verdict", "")),
        )
        for row in strict_rows
    )

    lines: list[str] = []
    lines.append("# Case Failure Export")
    lines.append("")
    lines.append(f"Strict rows: **{len(strict_rows)}**")
    lines.append(f"Strict failures: **{len(strict_failures)}**")
    lines.append("")

    lines.append("## Strict action summary")
    lines.append("")
    lines.append("| expected_action | primary_action | verdict | count |")
    lines.append("|---|---|---|---:|")
    for (expected, primary, verdict), count in counter.most_common():
        lines.append(f"| `{expected}` | `{primary}` | `{verdict}` | {count} |")
    lines.append("")

    lines.append("## Strict failures")
    lines.append("")
    for row in strict_failures:
        lines.append(f"### {row.get('id')} — {row.get('title')}")
        lines.append("")
        lines.append(f"- **category:** `{row.get('category')}`")
        lines.append(f"- **expected_action:** `{row.get('expected_action')}`")
        lines.append(f"- **ambiguity_level:** `{row.get('ambiguity_level')}`")
        lines.append(f"- **pending_context_strength:** `{row.get('pending_context_strength')}`")
        lines.append(f"- **acceptable_actions:** {as_text(row.get('acceptable_actions'))}")
        lines.append(f"- **success_criteria:** {as_text(row.get('success_criteria'))}")
        lines.append(f"- **case_notes:** {as_text(row.get('notes'))}")
        lines.append(f"- **primary_action:** `{row.get('grade_primary_action')}`")
        lines.append(f"- **verdict:** `{row.get('grade_verdict')}`")
        lines.append(f"- **unnecessary_clarification:** `{row.get('grade_unnecessary_clarification')}`")
        lines.append(f"- **wrong_intent:** `{row.get('grade_wrong_intent_inference')}`")
        lines.append(f"- **grader_notes:** {row.get('grade_notes')}")
        lines.append("- **messages:**")
        for message in row.get("messages", []) or []:
            if isinstance(message, dict):
                lines.append(f"  - **{message.get('role')}:** {truncate(message.get('content', ''), response_limit)}")
        lines.append("- **response:**")
        lines.append("")
        lines.append("```text")
        lines.append(truncate(row.get("response", ""), response_limit))
        lines.append("```")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export strict failures from case_results.csv with dataset metadata joined in.")
    parser.add_argument("--case-results", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--response-limit", type=int, default=1400)
    args = parser.parse_args()

    case_rows = load_csv(args.case_results)
    dataset_rows = load_jsonl(args.dataset)
    merged = merge_rows(case_rows, dataset_rows)

    write_markdown(args.output_md, merged, args.response_limit)
    print(f"wrote: {args.output_md}")

    if args.output_json:
        strict_failures = [row for row in merged if row.get("mode") == "strict" and row.get("grade_verdict") == "fail"]
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(strict_failures, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote: {args.output_json}")


if __name__ == "__main__":
    main()
