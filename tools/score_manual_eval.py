from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from run_eval import aggregate_by_category, aggregate_mode_rows, diff_cases, write_report  # noqa: E402


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "да"}


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, Any]] = []
        for row in reader:
            if not row.get("grade_verdict"):
                continue
            row["grade_wrong_intent_inference"] = parse_bool(row.get("grade_wrong_intent_inference"))
            row["grade_unnecessary_clarification"] = parse_bool(row.get("grade_unnecessary_clarification"))
            row["latency_seconds"] = 0.0
            row["input_tokens"] = ""
            row["output_tokens"] = ""
            row["total_tokens"] = ""
            rows.append(row)
    return rows


def save_json(data: Any, path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a filled manual-eval CSV without any API calls.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    rows = load_rows(args.input)
    if not rows:
        raise SystemExit("No graded rows found. Fill grade_* columns first, or run heuristic_grade_manual_eval.py.")

    rows_by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_mode[row["mode"]].append(row)

    summary = {mode: aggregate_mode_rows(mode_rows) for mode, mode_rows in rows_by_mode.items()}
    category_summary = {mode: aggregate_by_category(mode_rows) for mode, mode_rows in rows_by_mode.items()}
    improvements, regressions = diff_cases(rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_json(summary, args.output_dir / "summary.json")
    save_json(category_summary, args.output_dir / "category_summary.json")
    save_json(improvements, args.output_dir / "strict_improvements.json")
    save_json(regressions, args.output_dir / "strict_regressions.json")
    write_report(args.output_dir / "report.txt", summary, improvements, regressions)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved no-API score report to {args.output_dir}")


if __name__ == "__main__":
    main()
