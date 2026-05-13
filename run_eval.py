from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = Any  # type: ignore[assignment]


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_ROOT / "benchmark" / "data" / "seed_cases.jsonl"
BASELINE_PROMPT_PATH = PROJECT_ROOT / "baselines" / "no_prompt" / "baseline.txt"
STRICT_PROMPT_PATH = PROJECT_ROOT / "baselines" / "strict_v8" / "strict.txt"
GRADER_PROMPT_PATH = PROJECT_ROOT / "benchmark" / "prompts" / "grader.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a baseline vs strict ambiguity eval.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--baseline-prompt", type=Path, default=BASELINE_PROMPT_PATH)
    parser.add_argument("--strict-prompt", type=Path, default=STRICT_PROMPT_PATH)
    parser.add_argument("--grader-prompt", type=Path, default=GRADER_PROMPT_PATH)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--grader-model", default="gpt-5.4-mini")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--grader-reasoning-effort", default="low")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")


def require_openai_package() -> None:
    if not OPENAI_AVAILABLE:
        raise SystemExit("The 'openai' package is not installed. Run: pip install -r requirements.txt")


def extract_openai_error_info(exc: Exception) -> tuple[str | None, str | None, str]:
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            return error.get("code"), error.get("type"), error.get("message") or str(exc)
    return None, None, str(exc)


def format_openai_error(exc: Exception, output_dir: Path, partial_rows: int) -> str:
    code, error_type, message = extract_openai_error_info(exc)
    lines = ["OpenAI API request failed."]

    if code == "billing_not_active" or error_type == "billing_not_active":
        lines.extend(
            [
                "Reason: API billing is not active for this account or organization.",
                "This is separate from a ChatGPT subscription. ChatGPT Plus/Pro does not automatically enable API billing.",
                "Fix: open https://platform.openai.com/settings/organization/billing and activate billing or add credits, then create or reuse a key from that billed org.",
            ]
        )
    else:
        lines.append(f"Reason: {message}")

    if partial_rows:
        lines.append(f"Partial results were saved to: {output_dir}")

    return "\n".join(lines)


def maybe_save_partial_results(rows: list[dict[str, Any]], output_dir: Path) -> None:
    if not rows:
        return
    write_csv(rows, output_dir / "case_results.partial.csv")
    save_json(rows, output_dir / "case_results.partial.json")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


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
                raise ValueError(f"Invalid JSONL on line {line_number}: {exc}") from exc
    return items


def output_dir_from_args(args: argparse.Namespace) -> Path:
    if args.output_dir is not None:
        return args.output_dir
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return PROJECT_ROOT / "results" / f"run-{timestamp}"


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


def extract_usage(response: Any) -> dict[str, int | None]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    return {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


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


def call_model(
    client: OpenAI,
    model: str,
    developer_prompt: str,
    messages: list[dict[str, str]],
    reasoning_effort: str,
) -> dict[str, Any]:
    input_messages = [*messages]
    if developer_prompt.strip():
        input_messages = [{"role": "developer", "content": developer_prompt}, *messages]

    payload: dict[str, Any] = {
        "model": model,
        "input": input_messages,
    }
    reasoning = maybe_reasoning_arg(reasoning_effort)
    if reasoning is not None:
        payload["reasoning"] = reasoning

    started_at = time.perf_counter()
    response = client.responses.create(**payload)
    latency_seconds = time.perf_counter() - started_at

    return {
        "text": extract_text(response),
        "latency_seconds": round(latency_seconds, 3),
        "usage": extract_usage(response),
    }


def grade_output(
    client: OpenAI,
    grader_model: str,
    grader_prompt: str,
    case: dict[str, Any],
    candidate_output: str,
    mode: str,
    reasoning_effort: str,
) -> dict[str, Any]:
    grading_input = {
        "mode": mode,
        "conversation": case["messages"],
        "candidate_output": candidate_output,
        "acceptable_actions": case["acceptable_actions"],
        "success_criteria": case["success_criteria"],
        "case_title": case["title"],
        "category": case["category"],
    }

    payload: dict[str, Any] = {
        "model": grader_model,
        "input": [
            {"role": "developer", "content": grader_prompt},
            {"role": "user", "content": json.dumps(grading_input, ensure_ascii=False, indent=2)},
        ],
    }
    reasoning = maybe_reasoning_arg(reasoning_effort)
    if reasoning is not None:
        payload["reasoning"] = reasoning

    response = client.responses.create(**payload)
    parsed = extract_json_block(extract_text(response))
    parsed.setdefault("verdict", "fail")
    parsed.setdefault("primary_action", "other")
    parsed.setdefault("wrong_intent_inference", False)
    parsed.setdefault("unnecessary_clarification", False)
    parsed.setdefault("notes", "")
    return parsed


def to_percent(value: float) -> float:
    return round(value * 100, 1)


def mean_or_zero(values: list[float]) -> float:
    return round(statistics.mean(values), 3) if values else 0.0


def aggregate_mode_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    passed = [row for row in rows if row["grade_verdict"] == "pass"]
    wrong_intent = [row for row in rows if row["grade_wrong_intent_inference"]]
    unnecessary_clarifications = [row for row in rows if row["grade_unnecessary_clarification"]]
    clarifications = [row for row in rows if row["grade_primary_action"] == "clarify"]

    input_tokens = [row["input_tokens"] for row in rows if isinstance(row["input_tokens"], int)]
    output_tokens = [row["output_tokens"] for row in rows if isinstance(row["output_tokens"], int)]
    total_tokens = [row["total_tokens"] for row in rows if isinstance(row["total_tokens"], int)]

    return {
        "cases": total,
        "pass_rate": to_percent(len(passed) / total) if total else 0.0,
        "wrong_intent_inference_rate": to_percent(len(wrong_intent) / total) if total else 0.0,
        "unnecessary_clarification_rate": to_percent(len(unnecessary_clarifications) / total) if total else 0.0,
        "clarification_rate": to_percent(len(clarifications) / total) if total else 0.0,
        "avg_latency_seconds": mean_or_zero([row["latency_seconds"] for row in rows]),
        "avg_input_tokens": mean_or_zero([float(value) for value in input_tokens]),
        "avg_output_tokens": mean_or_zero([float(value) for value in output_tokens]),
        "avg_total_tokens": mean_or_zero([float(value) for value in total_tokens]),
    }


def aggregate_by_category(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)

    result: dict[str, dict[str, Any]] = {}
    for category, category_rows in grouped.items():
        result[category] = {
            "cases": len(category_rows),
            "pass_rate": to_percent(
                sum(1 for row in category_rows if row["grade_verdict"] == "pass") / len(category_rows)
            ),
        }
    return result


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(data: Any, path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def chart_bar(summary: dict[str, dict[str, Any]], metric: str, title: str, output_path: Path) -> None:
    modes = list(summary.keys())
    values = [summary[mode][metric] for mode in modes]
    colors = ["#6c7ae0", "#2ca58d"]

    plt.figure(figsize=(7, 4))
    plt.bar(modes, values, color=colors[: len(modes)])
    plt.title(title)
    plt.ylabel("Percent" if metric.endswith("rate") else "Value")
    for index, value in enumerate(values):
        plt.text(index, value + 1, str(value), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def chart_tradeoff(summary: dict[str, dict[str, Any]], output_path: Path) -> None:
    modes = list(summary.keys())
    clarification = [summary[mode]["clarification_rate"] for mode in modes]
    unnecessary = [summary[mode]["unnecessary_clarification_rate"] for mode in modes]
    x_positions = range(len(modes))
    width = 0.35

    plt.figure(figsize=(8, 4))
    plt.bar([x - width / 2 for x in x_positions], clarification, width=width, label="Clarification rate", color="#2ca58d")
    plt.bar([x + width / 2 for x in x_positions], unnecessary, width=width, label="Unnecessary clarification", color="#ff7f50")
    plt.xticks(list(x_positions), modes)
    plt.ylabel("Percent")
    plt.title("Clarification Tradeoff")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def chart_category_pass_rates(category_summaries: dict[str, dict[str, dict[str, Any]]], output_path: Path) -> None:
    categories = sorted({category for summary in category_summaries.values() for category in summary.keys()})
    modes = list(category_summaries.keys())
    x_positions = range(len(categories))
    width = 0.35

    plt.figure(figsize=(11, 5))
    for index, mode in enumerate(modes):
        values = [category_summaries[mode].get(category, {}).get("pass_rate", 0.0) for category in categories]
        offsets = [x + (index - (len(modes) - 1) / 2) * width for x in x_positions]
        plt.bar(offsets, values, width=width, label=mode)

    plt.xticks(list(x_positions), categories, rotation=20, ha="right")
    plt.ylabel("Pass rate (%)")
    plt.title("Pass Rate by Category")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def write_report(
    path: Path,
    summary: dict[str, dict[str, Any]],
    improvements: list[dict[str, Any]],
    regressions: list[dict[str, Any]],
) -> None:
    lines: list[str] = []
    lines.append("Strict Mode Eval Report")
    lines.append("")
    for mode, metrics in summary.items():
        lines.append(f"[{mode}]")
        for key, value in metrics.items():
            lines.append(f"{key}: {value}")
        lines.append("")

    lines.append("Strict improved on these cases:")
    if improvements:
        for item in improvements:
            lines.append(f"- {item['id']}: {item['title']}")
    else:
        lines.append("- none")
    lines.append("")

    lines.append("Strict regressed on these cases:")
    if regressions:
        for item in regressions:
            lines.append(f"- {item['id']}: {item['title']}")
    else:
        lines.append("- none")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_case_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(row["id"], row["mode"]): row for row in rows}


def diff_cases(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lookup = build_case_lookup(rows)
    improvements: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []

    case_ids = sorted({row["id"] for row in rows})
    for case_id in case_ids:
        baseline = lookup.get((case_id, "baseline"))
        strict = lookup.get((case_id, "strict"))
        if baseline is None or strict is None:
            continue
        if baseline["grade_verdict"] == "fail" and strict["grade_verdict"] == "pass":
            improvements.append({"id": strict["id"], "title": strict["title"]})
        if baseline["grade_verdict"] == "pass" and strict["grade_verdict"] == "fail":
            regressions.append({"id": strict["id"], "title": strict["title"]})

    return improvements, regressions


def main() -> None:
    args = parse_args()
    require_openai_package()
    require_api_key()

    dataset = load_jsonl(args.dataset)
    if args.max_cases > 0:
        dataset = dataset[: args.max_cases]

    output_dir = output_dir_from_args(args)
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_prompt = load_text(args.baseline_prompt)
    strict_prompt = load_text(args.strict_prompt)
    grader_prompt = load_text(args.grader_prompt)

    client = OpenAI()
    all_rows: list[dict[str, Any]] = []

    try:
        for index, case in enumerate(dataset, start=1):
            print(f"[{index}/{len(dataset)}] {case['id']}")
            for mode, developer_prompt in (("baseline", baseline_prompt), ("strict", strict_prompt)):
                candidate = call_model(
                    client=client,
                    model=args.model,
                    developer_prompt=developer_prompt,
                    messages=case["messages"],
                    reasoning_effort=args.reasoning_effort,
                )
                grade = grade_output(
                    client=client,
                    grader_model=args.grader_model,
                    grader_prompt=grader_prompt,
                    case=case,
                    candidate_output=candidate["text"],
                    mode=mode,
                    reasoning_effort=args.grader_reasoning_effort,
                )

                all_rows.append(
                    {
                        "id": case["id"],
                        "title": case["title"],
                        "category": case["category"],
                        "mode": mode,
                        "acceptable_actions": ", ".join(case["acceptable_actions"]),
                        "success_criteria": case["success_criteria"],
                        "response": candidate["text"],
                        "latency_seconds": candidate["latency_seconds"],
                        "input_tokens": candidate["usage"]["input_tokens"],
                        "output_tokens": candidate["usage"]["output_tokens"],
                        "total_tokens": candidate["usage"]["total_tokens"],
                        "grade_verdict": grade["verdict"],
                        "grade_primary_action": grade["primary_action"],
                        "grade_wrong_intent_inference": bool(grade["wrong_intent_inference"]),
                        "grade_unnecessary_clarification": bool(grade["unnecessary_clarification"]),
                        "grade_notes": grade["notes"],
                    }
                )
    except Exception as exc:
        if exc.__class__.__module__.startswith("openai"):
            maybe_save_partial_results(all_rows, output_dir)
            raise SystemExit(format_openai_error(exc, output_dir, len(all_rows))) from None
        raise

    rows_by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        rows_by_mode[row["mode"]].append(row)

    summary = {mode: aggregate_mode_rows(rows) for mode, rows in rows_by_mode.items()}
    category_summaries = {mode: aggregate_by_category(rows) for mode, rows in rows_by_mode.items()}
    improvements, regressions = diff_cases(all_rows)

    write_csv(all_rows, output_dir / "case_results.csv")
    save_json(summary, output_dir / "summary.json")
    save_json(category_summaries, output_dir / "category_summary.json")
    save_json(improvements, output_dir / "strict_improvements.json")
    save_json(regressions, output_dir / "strict_regressions.json")
    write_report(output_dir / "report.txt", summary, improvements, regressions)

    chart_bar(summary, "pass_rate", "Pass Rate", output_dir / "pass_rate.png")
    chart_bar(summary, "wrong_intent_inference_rate", "Wrong Intent Inference Rate", output_dir / "wrong_intent_inference_rate.png")
    chart_tradeoff(summary, output_dir / "clarification_tradeoff.png")
    chart_category_pass_rates(category_summaries, output_dir / "category_pass_rates.png")

    print(f"Saved results to {output_dir}")


if __name__ == "__main__":
    main()
