from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_DATASET = Path("benchmark/data/v0.3/dev_ru_v3.jsonl")

NOTE_UPDATES = {
    "dev_ru_v3_short_08": "Формат JSON выбран из явного списка форматов, поэтому нужно продолжать задачу без повторного уточнения.",
    "dev_ru_v3_short_10": "Слово обозначает тему из предыдущего перечисления, но не задаёт операцию: объяснить, выбрать, сравнить или развить.",
    "dev_ru_v3_short_14": "Формат JSONL выбран из явного списка экспортов, поэтому нужно выполнить экспорт в этом формате без нового уточнения.",
    "dev_ru_v3_short_17": "Стиль выбран из активной задачи переписывания, поэтому фрагмент закрывает pending task и требует прямого продолжения.",
    "dev_ru_v3_short_20": "Название поля выделено отдельно, но пользователь не сказал, нужно ли объяснить, изменить схему или показать пример.",
    "dev_ru_v3_ack_04": "Пользователь явно исправляет опечатку в названии, поэтому нужно принять исправление, а не начинать новую тему.",
    "dev_ru_v3_ack_10": "Пользователь корректирует выбранную букву варианта, поэтому нужно обновить выбор и не трактовать это как новый запрос.",
    "dev_ru_v3_clear_01": "Формат PowerShell выбран после явного вопроса о варианте команды, поэтому нужно сразу выдать PowerShell-версию.",
    "dev_ru_v3_clear_05": "Пользователь выбирает краткую версию из предложенных вариантов длины ответа, поэтому уточнение было бы лишним.",
    "dev_ru_v3_clear_06": "Пользователь выбирает второй вариант из явно перечисленного списка, поэтому нужно выполнить выбранный вариант напрямую.",
    "dev_ru_v3_clear_10": "Пользователь выбирает тон из заранее предложенных вариантов, поэтому это не самостоятельное слово, а завершение pending task.",
    "dev_ru_v3_clear_12": "Пользователь выбирает Markdown как формат вывода из предложенного списка, поэтому нужно продолжить в Markdown.",
    "dev_ru_v3_clear_14": "Пользователь подтверждает выполнение уже предложенного действия, поэтому нужно продолжать, а не задавать новый вопрос.",
    "dev_ru_v3_clear_15": "Пользователь выбирает первый вариант из явного списка, поэтому корректное действие — выполнить option 1 напрямую.",
    "dev_ru_v3_clear_19": "Пользователь выбирает режим вывода из активного выбора, поэтому нужно применить выбранный режим без повторного уточнения.",
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


def write_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Expand short notes in the RU v0.3 development dataset.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    items = load_jsonl(args.dataset)
    seen: set[str] = set()
    changed = 0

    for item in items:
        case_id = str(item.get("id", ""))
        if case_id in NOTE_UPDATES:
            seen.add(case_id)
            old_note = str(item.get("notes", ""))
            new_note = NOTE_UPDATES[case_id]
            if old_note != new_note:
                changed += 1
                if args.dry_run:
                    print(f"would update {case_id}: {old_note!r} -> {new_note!r}")
                else:
                    item["notes"] = new_note

    missing = sorted(set(NOTE_UPDATES) - seen)
    if missing:
        raise SystemExit("missing expected case ids: " + ", ".join(missing))

    if not args.dry_run:
        write_jsonl(args.dataset, items)

    print(f"dataset: {args.dataset}")
    print(f"note updates applied: {changed}")
    if args.dry_run:
        print("dry run only; no file written")


if __name__ == "__main__":
    main()
