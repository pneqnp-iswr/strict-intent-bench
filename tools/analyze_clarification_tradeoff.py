from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

CLARIFY_ACTIONS = {"clarify", "ask_clarification", "ask"}
METADATA_FIELDS = {
    "expected_action",
    "ambiguity_level",
    "pending_context_strength",
    "operation_required",
    "notes",
}

PRIMARY_TO_EXPECTED_ALIASES = {
    "answer": {"answer_directly", "continue_pending_task"},
    "direct_answer": {"answer_directly"},
    "answer_directly": {"answer_directly"},
    "continue": {"continue_pending_task"},
    "continue_pending_task": {"continue_pending_task"},
    "clarify": {"ask_clarification", "avoid_unasked_execution"},
    "ask": {"ask_clarification"},
    "ask_clarification": {"ask_clarification"},
    "acknowledge": {"acknowledge_correction", "avoid_unasked_execution"},
    "acknowledge_correction": {"acknowledge_correction"},
    "refuse": {"avoid_unasked_execution"},
    "avoid_unasked_execution": {"avoid_unasked_execution"},
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}: invalid JSONL on line {line_number}: {exc}") from exc
    return items


def load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def is_clarification(row: dict[str, Any]) -> bool:
    return str(row.get("grade_primary_action", "")).strip().lower() in CLARIFY_ACTIONS


def action_correct(row: dict[str, Any]) -> bool:
    expected = str(row.get("expected_action", "")).strip()
    primary = str(row.get("grade_primary_action", "")).strip().lower()
    if not expected or expected == "unspecified":
        return False
    return expected in PRIMARY_TO_EXPECTED_ALIASES.get(primary, {primary})


def detect_metadata_coverage(dataset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(dataset_rows)
    coverage: dict[str, Any] = {"cases": total}
    for field in sorted(METADATA_FIELDS):
        present = sum(1 for item in dataset_rows if field in item and item.get(field) not in {None, ""})
        coverage[field] = {
            "present": present,
            "missing": total - present,
            "coverage_rate": pct(present, total),
        }
    fully_annotated = sum(1 for item in dataset_rows if all(field in item and item.get(field) not in {None, ""} for field in METADATA_FIELDS))
    coverage["fully_annotated_cases"] = fully_annotated
    coverage["fully_annotated_rate"] = pct(fully_annotated, total)
    return coverage


def build_missing_id_error(missing: list[str], dataset_rows: list[dict[str, Any]], case_rows: list[dict[str, Any]]) -> str:
    unique_missing = sorted(set(missing))
    dataset_ids = {str(item.get("id", "")) for item in dataset_rows}
    sample_dataset = sorted(case_id for case_id in dataset_ids if case_id)[:5]
    sample_case = sorted({str(row.get("id", "")) for row in case_rows if row.get("id")})[:5]

    lines = [
        "case_results contains ids not present in dataset.",
        "This usually means --case-results and --dataset come from different language tracks or different dataset versions.",
        "",
        "First missing ids:",
    ]
    lines.extend(f"- {case_id}" for case_id in unique_missing[:20])
    lines.append("")
    lines.append("Sample case_results ids:")
    lines.extend(f"- {case_id}" for case_id in sample_case)
    lines.append("")
    lines.append("Sample dataset ids:")
    lines.extend(f"- {case_id}" for case_id in sample_dataset)
    lines.append("")
    lines.append("Fix: pass the matching JSONL dataset for the case_results.csv, or rerun evaluation on the intended dataset.")
    return "\n".join(lines)


def merge_rows(case_rows: list[dict[str, Any]], dataset_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    case_metadata = {str(item["id"]): item for item in dataset_rows if "id" in item}
    merged: list[dict[str, Any]] = []
    missing: list[str] = []

    for row in case_rows:
        case_id = str(row.get("id", ""))
        metadata = case_metadata.get(case_id)
        if metadata is None:
            missing.append(case_id)
            metadata = {}
        merged_row = dict(row)
        for key in (
            "expected_action",
            "ambiguity_level",
            "pending_context_strength",
            "operation_required",
            "notes",
        ):
            merged_row[key] = metadata.get(key, "unspecified")
        merged_row.setdefault("category", metadata.get("category", "unspecified"))
        merged.append(merged_row)

    if missing:
        raise SystemExit(build_missing_id_error(missing, dataset_rows, case_rows))
    return merged


def group_by(rows: Iterable[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, "unspecified"))].append(row)
    return grouped


def mode_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    wrong_intent = sum(1 for row in rows if truthy(row.get("grade_wrong_intent_inference")))
    unnecessary_clarification = sum(1 for row in rows if truthy(row.get("grade_unnecessary_clarification")))
    clarifications = sum(1 for row in rows if is_clarification(row))
    metadata_available_rows = [row for row in rows if row.get("expected_action") != "unspecified"]
    action_correct_count = sum(1 for row in metadata_available_rows if action_correct(row))

    clear_direct = [row for row in rows if row.get("category") == "clear_direct"]
    strong_pending = [row for row in rows if row.get("pending_context_strength") == "strong"]
    high_ambiguity_short = [
        row
        for row in rows
        if row.get("category") == "short_fragment"
        and row.get("ambiguity_level") == "high"
        and row.get("expected_action") == "ask_clarification"
    ]

    over_clear_direct = sum(
        1
        for row in clear_direct
        if is_clarification(row) and row.get("expected_action") != "ask_clarification"
    )
    over_strong_pending = sum(
        1
        for row in strong_pending
        if is_clarification(row) and row.get("expected_action") != "ask_clarification"
    )
    under_high_short = sum(1 for row in high_ambiguity_short if not is_clarification(row))

    return {
        "cases": total,
        "metadata_available_cases": len(metadata_available_rows),
        "action_accuracy": pct(action_correct_count, len(metadata_available_rows)),
        "wrong_intent_inference_rate": pct(wrong_intent, total),
        "clarification_rate": pct(clarifications, total),
        "unnecessary_clarification_rate": pct(unnecessary_clarification, total),
        "overclarification_on_clear_direct_rate": pct(over_clear_direct, len(clear_direct)),
        "overclarification_on_strong_pending_context_rate": pct(over_strong_pending, len(strong_pending)),
        "underclarification_on_high_ambiguity_short_fragment_rate": pct(under_high_short, len(high_ambiguity_short)),
        "clear_direct_cases": len(clear_direct),
        "strong_pending_cases": len(strong_pending),
        "high_ambiguity_short_fragment_cases": len(high_ambiguity_short),
    }


def breakdown(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for value, subset in sorted(group_by(rows, field).items()):
        result[value] = mode_summary(subset)
    return result


def metric_delta(summary: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = summary.get("baseline", {})
    strict = summary.get("strict", {})
    metrics = [
        "action_accuracy",
        "wrong_intent_inference_rate",
        "clarification_rate",
        "unnecessary_clarification_rate",
        "overclarification_on_clear_direct_rate",
        "overclarification_on_strong_pending_context_rate",
        "underclarification_on_high_ambiguity_short_fragment_rate",
    ]
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        baseline_value = baseline.get(metric, 0.0)
        strict_value = strict.get(metric, 0.0)
        rows.append(
            {
                "metric": metric,
                "baseline": baseline_value,
                "strict": strict_value,
                "delta_strict_minus_baseline": round(float(strict_value) - float(baseline_value), 1),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], metadata_coverage: dict[str, Any]) -> dict[str, Any]:
    by_mode = group_by(rows, "mode")
    summary = {mode: mode_summary(mode_rows) for mode, mode_rows in sorted(by_mode.items())}
    return {
        "metadata_coverage": metadata_coverage,
        "summary_by_mode": summary,
        "delta_table": metric_delta(summary),
        "action_accuracy_by_expected_action": {
            mode: breakdown(mode_rows, "expected_action") for mode, mode_rows in sorted(by_mode.items())
        },
        "wrong_intent_by_expected_action": {
            mode: {
                expected: {
                    "cases": len(subset),
                    "wrong_intent_inference_rate": pct(
                        sum(1 for row in subset if truthy(row.get("grade_wrong_intent_inference"))),
                        len(subset),
                    ),
                }
                for expected, subset in sorted(group_by(mode_rows, "expected_action").items())
            }
            for mode, mode_rows in sorted(by_mode.items())
        },
        "clarification_by_ambiguity_level": {
            mode: {
                value: {
                    "cases": len(subset),
                    "clarification_rate": pct(sum(1 for row in subset if is_clarification(row)), len(subset)),
                }
                for value, subset in sorted(group_by(mode_rows, "ambiguity_level").items())
            }
            for mode, mode_rows in sorted(by_mode.items())
        },
        "clarification_by_pending_context_strength": {
            mode: {
                value: {
                    "cases": len(subset),
                    "clarification_rate": pct(sum(1 for row in subset if is_clarification(row)), len(subset)),
                }
                for value, subset in sorted(group_by(mode_rows, "pending_context_strength").items())
            }
            for mode, mode_rows in sorted(by_mode.items())
        },
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def write_markdown_report(path: Path, case_results_path: Path, dataset_path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Clarification Trade-off Analysis")
    lines.append("")
    lines.append(f"Case results: `{case_results_path}`")
    lines.append(f"Dataset metadata: `{dataset_path}`")
    lines.append("")

    lines.append("## Metadata coverage")
    lines.append("")
    coverage = report["metadata_coverage"]
    lines.append(f"Dataset cases: **{coverage['cases']}**")
    lines.append(f"Fully annotated cases: **{coverage['fully_annotated_cases']}** ({coverage['fully_annotated_rate']}%)")
    coverage_rows = []
    for field in sorted(METADATA_FIELDS):
        values = coverage[field]
        coverage_rows.append([field, values["present"], values["missing"], values["coverage_rate"]])
    lines.extend(md_table(["metadata_field", "present", "missing", "coverage_rate"], coverage_rows))
    lines.append("")
    if coverage["fully_annotated_cases"] == 0:
        lines.append(
            "> Metadata warning: this dataset has no v0.3 expected-action metadata, so action-accuracy and metadata-specific breakdowns are partial/diagnostic only."
        )
        lines.append("")

    lines.append("## Summary by mode")
    lines.append("")
    metric_names = [
        "cases",
        "metadata_available_cases",
        "action_accuracy",
        "wrong_intent_inference_rate",
        "clarification_rate",
        "unnecessary_clarification_rate",
        "overclarification_on_clear_direct_rate",
        "overclarification_on_strong_pending_context_rate",
        "underclarification_on_high_ambiguity_short_fragment_rate",
    ]
    summary_rows = []
    for mode, metrics in report["summary_by_mode"].items():
        summary_rows.append([mode, *[metrics.get(metric, 0) for metric in metric_names]])
    lines.extend(md_table(["mode", *metric_names], summary_rows))
    lines.append("")

    lines.append("## Baseline vs strict delta")
    lines.append("")
    delta_rows = [
        [row["metric"], row["baseline"], row["strict"], row["delta_strict_minus_baseline"]]
        for row in report["delta_table"]
    ]
    lines.extend(md_table(["metric", "baseline", "strict", "strict - baseline"], delta_rows))
    lines.append("")

    lines.append("## Action accuracy by expected action")
    lines.append("")
    for mode, breakdown_data in report["action_accuracy_by_expected_action"].items():
        lines.append(f"### {mode}")
        rows = [[expected, values["cases"], values["metadata_available_cases"], values["action_accuracy"]] for expected, values in breakdown_data.items()]
        lines.extend(md_table(["expected_action", "cases", "metadata_available_cases", "action_accuracy"], rows))
        lines.append("")

    lines.append("## Wrong intent by expected action")
    lines.append("")
    for mode, breakdown_data in report["wrong_intent_by_expected_action"].items():
        lines.append(f"### {mode}")
        rows = [
            [expected, values["cases"], values["wrong_intent_inference_rate"]]
            for expected, values in breakdown_data.items()
        ]
        lines.extend(md_table(["expected_action", "cases", "wrong_intent_inference_rate"], rows))
        lines.append("")

    lines.append("## Clarification by ambiguity level")
    lines.append("")
    for mode, breakdown_data in report["clarification_by_ambiguity_level"].items():
        lines.append(f"### {mode}")
        rows = [[level, values["cases"], values["clarification_rate"]] for level, values in breakdown_data.items()]
        lines.extend(md_table(["ambiguity_level", "cases", "clarification_rate"], rows))
        lines.append("")

    lines.append("## Clarification by pending context strength")
    lines.append("")
    for mode, breakdown_data in report["clarification_by_pending_context_strength"].items():
        lines.append(f"### {mode}")
        rows = [[level, values["cases"], values["clarification_rate"]] for level, values in breakdown_data.items()]
        lines.extend(md_table(["pending_context_strength", "cases", "clarification_rate"], rows))
        lines.append("")

    lines.append("## Note")
    lines.append("")
    lines.append("This analysis uses existing graded case results and dataset metadata. It does not call any API.")
    lines.append("The analyzer checks the clarification trade-off; it does not replace manual audit.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze clarification trade-off metrics from case_results.csv without API access.")
    parser.add_argument("--case-results", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    case_rows = load_csv(args.case_results)
    dataset_rows = load_jsonl(args.dataset)
    metadata_coverage = detect_metadata_coverage(dataset_rows)
    merged = merge_rows(case_rows, dataset_rows)
    report = summarize(merged, metadata_coverage=metadata_coverage)

    write_markdown_report(args.output_md, args.case_results, args.dataset, report)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote: {args.output_md}")
    if args.output_json:
        print(f"wrote: {args.output_json}")


if __name__ == "__main__":
    main()
