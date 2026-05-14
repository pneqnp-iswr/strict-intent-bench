#!/usr/bin/env python3
"""Export JSONL benchmark cases into a static demo JSON file.

Default input:
- benchmark/data/v0.3/dev_en_v3.jsonl
- benchmark/data/v0.3/dev_ru_v3.jsonl

Default output:
- docs/demo_cases.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    PROJECT_ROOT / "benchmark" / "data" / "v0.3" / "dev_en_v3.jsonl",
    PROJECT_ROOT / "benchmark" / "data" / "v0.3" / "dev_ru_v3.jsonl",
]
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "demo_cases.json"

FIELDS_TO_KEEP = [
    "id",
    "title",
    "category",
    "messages",
    "expected_action",
    "ambiguity_level",
    "pending_context_strength",
    "acceptable_actions",
    "success_criteria",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export benchmark JSONL cases for docs/demo.html")
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        dest="inputs",
        help="JSONL dataset to include. May be passed multiple times. Defaults to v0.3 EN + RU dev files.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-cases", type=int, default=0, help="Optional cap across all inputs. 0 means no cap.")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input dataset: {path}")

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}:{line_no}: {exc}") from exc
            if not isinstance(case, dict):
                raise ValueError(f"Expected object in {path}:{line_no}")
            rows.append(case)
    return rows


def normalize_case(case: dict[str, Any], source_file: Path) -> dict[str, Any]:
    normalized = {field: case.get(field) for field in FIELDS_TO_KEEP}
    normalized["source_file"] = str(source_file.relative_to(PROJECT_ROOT)) if source_file.is_relative_to(PROJECT_ROOT) else str(source_file)

    if normalized.get("messages") is None:
        normalized["messages"] = []
    if normalized.get("acceptable_actions") is None:
        normalized["acceptable_actions"] = []

    return normalized


def main() -> None:
    args = parse_args()
    inputs = args.inputs or DEFAULT_INPUTS

    exported: list[dict[str, Any]] = []
    for input_path in inputs:
        input_path = input_path if input_path.is_absolute() else PROJECT_ROOT / input_path
        for case in load_jsonl(input_path):
            exported.append(normalize_case(case, input_path))
            if args.max_cases and len(exported) >= args.max_cases:
                break
        if args.max_cases and len(exported) >= args.max_cases:
            break

    output_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Exported {len(exported)} cases to {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
