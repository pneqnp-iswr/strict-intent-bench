from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path
from typing import Any

OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = Any  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRADER_PROMPT = PROJECT_ROOT / "benchmark" / "prompts" / "grader.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Re-grade existing case_results.csv using dataset metadata.")
    parser.add_argument("--case-results", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--grader-prompt", type=Path, default=DEFAULT_GRADER_PROMPT)
    parser.add_argument("--grader-model", default="gpt-5.4")
    parser.add_argument("--grader-reasoning-effort", default="medium")
    parser.add_argument("--mode", choices=["all", "baseline", "strict"], default="all")
    parser.add_argument("--max-rows", type=int, default=0)
    return parser.parse_args()


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")


def require_openai_package() -> None:
    if not OPENAI_AVAILABLE:
        raise SystemExit("The 'openai' package is not installed. Run: pip install -r requirements.txt")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


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


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_json(data: Any, path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text.strip()
    texts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                texts.append(text)
    return "\n".join(texts).strip()


def extract_json_block(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse grader JSON: {text}")
        return json.loads(match.group(0))


def maybe_reasoning_arg(effort: str) -> dict[str, str] | None:
    if not effort or effort.lower() == "none":
        return None
    return {"effort": effort}


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def grade_row(
    client: OpenAI,
    grader_prompt: str,
    grader_model: str,
    grader_reasoning_effort: str,
    row: dict[str, str],
    case: dict[str, Any],
) -> dict[str, Any]:
    grading_input = {
        "mode": row.get("mode"),
        "conversation": case.get("messages", []),
        "candidate_output": row.get("response", ""),
        "acceptable_actions": case.get("acceptable_actions", []),
        "success_criteria": case.get("success_criteria", ""),
        "case_title": case.get("title", row.get("title", "")),
        "category": case.get("category", row.get("category", "")),
        "expected_action": case.get("expected_action"),
        "ambiguity_level": case.get("ambiguity_level"),
        "pending_context_strength": case.get("pending_context_strength"),
        "operation_required": case.get("operation_required"),
        "notes": case.get("notes"),
    }

    payload: dict[str, Any] = {
        "model": grader_model,
        "input": [
            {"role": "developer", "content": grader_prompt},
            {"role": "user", "content": json.dumps(grading_input, ensure_ascii=False, indent=2)},
        ],
    }
    reasoning = maybe_reasoning_arg(grader_reasoning_effort)
    if reasoning is not None:
        payload["reasoning"] = reasoning

    started_at = time.perf_counter()
    response = client.responses.create(**payload)
    latency_seconds = round(time.perf_counter() - started_at, 3)
    parsed = extract_json_block(extract_text(response))

    parsed.setdefault("verdict", "fail")
    parsed.setdefault("primary_action", "other")
    parsed.setdefault("wrong_intent_inference", False)
    parsed.setdefault("unnecessary_clarification", False)
    parsed.setdefault("notes", "")
    parsed["grader_latency_seconds"] = latency_seconds
    return parsed


def main() -> None:
    args = parse_args()
    require_openai_package()
    require_api_key()

    case_rows = load_csv(args.case_results)
    dataset_rows = load_jsonl(args.dataset)
    metadata = {str(row.get("id")): row for row in dataset_rows}
    grader_prompt = load_text(args.grader_prompt)
    client = OpenAI()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_indexes: list[int] = []
    for index, row in enumerate(case_rows):
        if args.mode != "all" and row.get("mode") != args.mode:
            continue
        selected_indexes.append(index)
    if args.max_rows > 0:
        selected_indexes = selected_indexes[: args.max_rows]

    rows_out: list[dict[str, Any]] = [dict(row) for row in case_rows]
    regraded: list[dict[str, Any]] = []

    try:
        for count, index in enumerate(selected_indexes, start=1):
            row = rows_out[index]
            case_id = str(row.get("id", ""))
            case = metadata.get(case_id)
            if case is None:
                raise SystemExit(f"case_results contains id not present in dataset: {case_id}")
            print(f"[{count}/{len(selected_indexes)}] {case_id} {row.get('mode')}")
            grade = grade_row(
                client=client,
                grader_prompt=grader_prompt,
                grader_model=args.grader_model,
                grader_reasoning_effort=args.grader_reasoning_effort,
                row=row,
                case=case,
            )

            row["grade_verdict"] = grade["verdict"]
            row["grade_primary_action"] = grade["primary_action"]
            row["grade_wrong_intent_inference"] = normalize_bool(grade["wrong_intent_inference"])
            row["grade_unnecessary_clarification"] = normalize_bool(grade["unnecessary_clarification"])
            row["grade_notes"] = grade["notes"]
            row["regraded"] = True
            row["regrader_model"] = args.grader_model
            row["regrader_reasoning_effort"] = args.grader_reasoning_effort
            row["regrader_latency_seconds"] = grade["grader_latency_seconds"]
            regraded.append(dict(row))

            write_csv(rows_out, output_dir / "case_results.partial.csv")
            save_json(regraded, output_dir / "regraded_rows.partial.json")
    except Exception as exc:
        if exc.__class__.__module__.startswith("openai"):
            raise SystemExit(f"OpenAI API request failed: {exc}") from None
        raise

    write_csv(rows_out, output_dir / "case_results.csv")
    save_json(regraded, output_dir / "regraded_rows.json")
    print(f"Saved regraded results to {output_dir}")


if __name__ == "__main__":
    main()
