from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

FIELDS = [
    "category",
    "expected_action",
    "ambiguity_level",
    "pending_context_strength",
]


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


def count_field(items: list[dict[str, Any]], field: str) -> Counter[str]:
    return Counter(str(item.get(field, "unspecified")) for item in items)


def canonical_pair_key(case_id: str) -> str:
    # dev_en_v3_quoted_01 and dev_ru_v3_quoted_01 should compare as the same slot.
    return re.sub(r"^dev_(en|ru)_", "dev_", case_id)


def paired_ids(left: list[dict[str, Any]], right: list[dict[str, Any]], normalize_language_ids: bool) -> tuple[set[str], set[str], set[str]]:
    def key(item: dict[str, Any]) -> str | None:
        if "id" not in item:
            return None
        case_id = str(item["id"])
        return canonical_pair_key(case_id) if normalize_language_ids else case_id

    left_ids = {value for item in left if (value := key(item)) is not None}
    right_ids = {value for item in right if (value := key(item)) is not None}
    return left_ids & right_ids, left_ids - right_ids, right_ids - left_ids


def table_for_counts(left_name: str, right_name: str, left: Counter[str], right: Counter[str]) -> list[str]:
    keys = sorted(set(left) | set(right))
    lines = [f"| Value | {left_name} | {right_name} | Delta |", "|---|---:|---:|---:|"]
    for key in keys:
        left_value = left.get(key, 0)
        right_value = right.get(key, 0)
        lines.append(f"| `{key}` | {left_value} | {right_value} | {right_value - left_value:+d} |")
    return lines


def build_report(
    left_path: Path,
    right_path: Path,
    left_items: list[dict[str, Any]],
    right_items: list[dict[str, Any]],
    normalize_language_ids: bool,
) -> str:
    left_name = left_path.stem
    right_name = right_path.stem
    shared, left_only, right_only = paired_ids(left_items, right_items, normalize_language_ids=normalize_language_ids)

    lines: list[str] = []
    lines.append("# Dataset Split Comparison")
    lines.append("")
    lines.append(f"Left split: `{left_path}`")
    lines.append(f"Right split: `{right_path}`")
    lines.append(f"Language-id normalization: **{'on' if normalize_language_ids else 'off'}**")
    lines.append("")
    lines.append("## Size")
    lines.append("")
    lines.append(f"- `{left_name}` cases: **{len(left_items)}**")
    lines.append(f"- `{right_name}` cases: **{len(right_items)}**")
    lines.append(f"- shared comparable ids: **{len(shared)}**")
    lines.append(f"- left-only comparable ids: **{len(left_only)}**")
    lines.append(f"- right-only comparable ids: **{len(right_only)}**")
    lines.append("")

    for field in FIELDS:
        lines.append(f"## `{field}` balance")
        lines.append("")
        lines.extend(table_for_counts(left_name, right_name, count_field(left_items, field), count_field(right_items, field)))
        lines.append("")

    lines.append("## Category × expected action")
    lines.append("")
    left_matrix: dict[str, Counter[str]] = defaultdict(Counter)
    right_matrix: dict[str, Counter[str]] = defaultdict(Counter)
    for item in left_items:
        left_matrix[str(item.get("category", "unspecified"))][str(item.get("expected_action", "unspecified"))] += 1
    for item in right_items:
        right_matrix[str(item.get("category", "unspecified"))][str(item.get("expected_action", "unspecified"))] += 1

    categories = sorted(set(left_matrix) | set(right_matrix))
    actions = sorted(set().union(*(counter.keys() for counter in left_matrix.values()), *(counter.keys() for counter in right_matrix.values())))
    lines.append("| Category | Expected action | Left | Right | Delta |")
    lines.append("|---|---|---:|---:|---:|")
    for category in categories:
        for action in actions:
            left_value = left_matrix[category].get(action, 0)
            right_value = right_matrix[category].get(action, 0)
            if left_value == 0 and right_value == 0:
                continue
            lines.append(f"| `{category}` | `{action}` | {left_value} | {right_value} | {right_value - left_value:+d} |")
    lines.append("")

    if left_only or right_only:
        lines.append("## ID mismatch details")
        lines.append("")
        if left_only:
            lines.append("Left-only comparable ids:")
            lines.extend(f"- `{case_id}`" for case_id in sorted(left_only))
            lines.append("")
        if right_only:
            lines.append("Right-only comparable ids:")
            lines.extend(f"- `{case_id}`" for case_id in sorted(right_only))
            lines.append("")

    lines.append("## Note")
    lines.append("")
    lines.append("This comparison checks structural balance only. It does not prove semantic equivalence between language tracks.")
    if normalize_language_ids:
        lines.append("Language-id normalization treats ids like `dev_en_v3_short_01` and `dev_ru_v3_short_01` as comparable slots.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two strict-intent-bench JSONL dataset splits.")
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path, help="Optional Markdown report path.")
    parser.add_argument(
        "--no-normalize-language-ids",
        action="store_true",
        help="Do not normalize dev_en_/dev_ru_ id prefixes when comparing language mirror splits.",
    )
    args = parser.parse_args()

    left_items = load_jsonl(args.left)
    right_items = load_jsonl(args.right)
    report = build_report(
        args.left,
        args.right,
        left_items,
        right_items,
        normalize_language_ids=not args.no_normalize_language_ids,
    )
    print(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote: {args.output}")


if __name__ == "__main__":
    main()
