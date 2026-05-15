from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

IMPORTANT_FIELDS = [
    "id",
    "title",
    "category",
    "expected_action",
    "ambiguity_level",
    "pending_context_strength",
    "operation_required",
    "acceptable_actions",
    "success_criteria",
    "notes",
]


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


def parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must use LABEL=PATH format")
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("run label cannot be empty")
    return label, Path(path)


def short(text: str, limit: int) -> str:
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def keep_run_row(row: dict[str, str], focus_expected_actions: set[str] | None, include_passes: bool) -> bool:
    if row.get("mode") != "strict":
        return False
    if include_passes:
        return True
    if row.get("grade_verdict") == "fail":
        return True
    if str(row.get("grade_unnecessary_clarification", "")).lower() == "true":
        return True
    if str(row.get("grade_wrong_intent_inference", "")).lower() == "true":
        return True
    if focus_expected_actions and row.get("expected_action") in focus_expected_actions:
        return True
    return False


def enrich_rows(rows: list[dict[str, str]], metadata: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for row in rows:
        case_id = row.get("id") or row.get("case_id") or ""
        meta = metadata.get(case_id, {})
        merged = dict(row)
        for key in IMPORTANT_FIELDS:
            if key not in merged or merged.get(key) in {None, ""}:
                value = meta.get(key, "")
                if isinstance(value, list):
                    value = ", ".join(str(item) for item in value)
                merged[key] = str(value)
        enriched.append(merged)
    return enriched


def write_pack(
    output: Path,
    dataset_path: Path,
    dataset_rows: list[dict[str, Any]],
    run_rows: dict[str, list[dict[str, str]]],
    focus_expected_actions: set[str] | None,
    response_limit: int,
) -> None:
    by_case: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for label, rows in run_rows.items():
        for row in rows:
            if row.get("mode") == "strict":
                by_case[row.get("id", "")][label] = row

    meta_by_id = {str(row.get("id")): row for row in dataset_rows}

    lines: list[str] = []
    lines.append("# Prompt Synthesis Pack")
    lines.append("")
    lines.append(f"Dataset: `{dataset_path}`")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This pack is for designing the next Strict / Precision prompt from observed behavior, not from abstract brainstorming."
    )
    lines.append("Use it to identify exact failure clusters and propose a candidate prompt that preserves wins while fixing regressions.")
    lines.append("")
    lines.append("## Synthesis instruction for a model")
    lines.append("")
    lines.append("```text")
    lines.append("You are a strict prompt-auditor for an assistant behavior benchmark.")
    lines.append("Do not generalize beyond the evidence in this pack.")
    lines.append("Your job is to design one next candidate Strict / Precision prompt.")
    lines.append("Preserve the strongest observed wins and target the repeated failures.")
    lines.append("Do not optimize only for fewer clarifications; do not optimize only for more clarifications.")
    lines.append("The target is correct action selection: answer_directly, ask_clarification, acknowledge_correction, continue_pending_task, avoid_unasked_execution.")
    lines.append("Give:")
    lines.append("1. Failure diagnosis by expected_action.")
    lines.append("2. Which prior prompt behavior should be preserved.")
    lines.append("3. Which prior prompt behavior should be rejected.")
    lines.append("4. A single full candidate prompt.")
    lines.append("5. The exact metrics that should improve in the next 16-case run.")
    lines.append("No motivational language. No broad claims. No product claims.")
    lines.append("```")
    lines.append("")

    lines.append("## Dataset slots")
    lines.append("")
    for item in dataset_rows:
        if focus_expected_actions and str(item.get("expected_action")) not in focus_expected_actions:
            continue
        lines.append(f"### {item.get('id')} — {item.get('title')}")
        lines.append("")
        for field in IMPORTANT_FIELDS:
            if field in item:
                value = item[field]
                if isinstance(value, list):
                    value = ", ".join(str(x) for x in value)
                lines.append(f"- **{field}:** {value}")
        messages = item.get("messages", [])
        lines.append("- **messages:**")
        for message in messages:
            lines.append(f"  - {message.get('role')}: {short(message.get('content', ''), response_limit)}")
        lines.append("")

        runs_for_case = by_case.get(str(item.get("id")), {})
        for label in sorted(runs_for_case):
            row = runs_for_case[label]
            lines.append(f"#### Run `{label}` strict output")
            lines.append("")
            lines.append(f"- **verdict:** {row.get('grade_verdict')}")
            lines.append(f"- **primary_action:** {row.get('grade_primary_action')}")
            lines.append(f"- **wrong_intent:** {row.get('grade_wrong_intent_inference')}")
            lines.append(f"- **unnecessary_clarification:** {row.get('grade_unnecessary_clarification')}")
            lines.append(f"- **grader_notes:** {row.get('grade_notes')}")
            lines.append(f"- **response:** {short(row.get('response', ''), response_limit)}")
            lines.append("")

    lines.append("## Compact run comparison")
    lines.append("")
    headers = ["case_id", "expected_action", *sorted(run_rows.keys())]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for case_id in sorted(by_case):
        meta = meta_by_id.get(case_id, {})
        expected = str(meta.get("expected_action", ""))
        if focus_expected_actions and expected not in focus_expected_actions:
            continue
        cells = [case_id, expected]
        for label in sorted(run_rows.keys()):
            row = by_case.get(case_id, {}).get(label)
            if row is None:
                cells.append("-")
            else:
                verdict = row.get("grade_verdict")
                action = row.get("grade_primary_action")
                unnec = row.get("grade_unnecessary_clarification")
                wrong = row.get("grade_wrong_intent_inference")
                cells.append(f"{verdict}/{action}/unnec={unnec}/wrong={wrong}")
        lines.append("| " + " | ".join(cells) + " |")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an evidence pack for synthesizing the next Strict / Precision prompt.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--run", action="append", type=parse_run, required=True, help="LABEL=case_results.csv")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--focus-expected-action", action="append", default=[])
    parser.add_argument("--include-passes", action="store_true")
    parser.add_argument("--response-limit", type=int, default=900)
    args = parser.parse_args()

    dataset_rows = load_jsonl(args.dataset)
    metadata = {str(row.get("id")): row for row in dataset_rows}
    focus = set(args.focus_expected_action) if args.focus_expected_action else None

    run_rows: dict[str, list[dict[str, str]]] = {}
    for label, path in args.run:
        rows = enrich_rows(load_csv(path), metadata)
        rows = [row for row in rows if keep_run_row(row, focus, args.include_passes)]
        run_rows[label] = rows

    write_pack(
        output=args.output,
        dataset_path=args.dataset,
        dataset_rows=dataset_rows,
        run_rows=run_rows,
        focus_expected_actions=focus,
        response_limit=args.response_limit,
    )
    print(f"wrote: {args.output}")


if __name__ == "__main__":
    main()
