from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = Any  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STRICT_PROMPT = PROJECT_ROOT / "baselines" / "strict_v13_unseen_pending" / "strict.txt"
DEFAULT_BASELINE_PROMPT = PROJECT_ROOT / "baselines" / "no_prompt" / "baseline.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Strict / Precision playground.")
    parser.add_argument("--mode", choices=["strict", "baseline"], default="strict")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--strict-prompt", type=Path, default=DEFAULT_STRICT_PROMPT)
    parser.add_argument("--baseline-prompt", type=Path, default=DEFAULT_BASELINE_PROMPT)
    return parser.parse_args()


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")


def require_openai_package() -> None:
    if not OPENAI_AVAILABLE:
        raise SystemExit("The 'openai' package is not installed. Run: pip install -r requirements.txt")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def maybe_reasoning_arg(effort: str) -> dict[str, str] | None:
    if not effort or effort.lower() == "none":
        return None
    return {"effort": effort}


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


def call_model(
    client: OpenAI,
    model: str,
    developer_prompt: str,
    messages: list[dict[str, str]],
    reasoning_effort: str,
) -> str:
    input_messages = list(messages)
    if developer_prompt.strip():
        input_messages = [{"role": "developer", "content": developer_prompt}, *input_messages]

    payload: dict[str, Any] = {
        "model": model,
        "input": input_messages,
    }
    reasoning = maybe_reasoning_arg(reasoning_effort)
    if reasoning is not None:
        payload["reasoning"] = reasoning

    response = client.responses.create(**payload)
    return extract_text(response)


def print_help() -> None:
    print(
        "\nCommands:\n"
        "  /help              show this help\n"
        "  /mode strict       switch to Strict / Precision prompt\n"
        "  /mode baseline     switch to no-prompt baseline\n"
        "  /reset             clear conversation history\n"
        "  /history           show current conversation history\n"
        "  /exit              quit\n"
        "\nType normal messages to chat with the selected mode.\n"
    )


def print_history(messages: list[dict[str, str]]) -> None:
    if not messages:
        print("\n[history is empty]\n")
        return
    print()
    for index, message in enumerate(messages, start=1):
        print(f"[{index}] {message['role']}: {message['content']}")
    print()


def main() -> None:
    args = parse_args()
    require_openai_package()
    require_api_key()

    strict_prompt = load_text(args.strict_prompt)
    baseline_prompt = load_text(args.baseline_prompt)
    mode = args.mode
    messages: list[dict[str, str]] = []
    client = OpenAI()

    print("Strict Intent Playground")
    print(f"model: {args.model}")
    print(f"reasoning_effort: {args.reasoning_effort}")
    print(f"mode: {mode}")
    print("Type /help for commands.\n")

    while True:
        try:
            raw = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return

        if not raw:
            continue

        if raw == "/exit":
            print("bye")
            return
        if raw == "/help":
            print_help()
            continue
        if raw == "/reset":
            messages.clear()
            print("history cleared\n")
            continue
        if raw == "/history":
            print_history(messages)
            continue
        if raw.startswith("/mode "):
            requested_mode = raw.split(maxsplit=1)[1].strip().lower()
            if requested_mode not in {"strict", "baseline"}:
                print("mode must be 'strict' or 'baseline'\n")
                continue
            mode = requested_mode
            print(f"mode: {mode}\n")
            continue

        messages.append({"role": "user", "content": raw})
        developer_prompt = strict_prompt if mode == "strict" else baseline_prompt

        try:
            answer = call_model(
                client=client,
                model=args.model,
                developer_prompt=developer_prompt,
                messages=messages,
                reasoning_effort=args.reasoning_effort,
            )
        except Exception as exc:
            messages.pop()
            print(f"OpenAI API request failed: {exc}\n")
            continue

        messages.append({"role": "assistant", "content": answer})
        print(f"\n{mode}> {answer}\n")


if __name__ == "__main__":
    main()
