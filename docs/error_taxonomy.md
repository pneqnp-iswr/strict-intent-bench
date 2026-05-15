# Error Taxonomy

This document defines the main error labels used by `strict-intent-bench`.

The benchmark is about **action choice**, not only text quality. A response can be fluent and still fail if it chooses the wrong conversational action.

## Core failure labels

### `wrong_intent_inference`

The assistant answers a plausible but unstated request.

Typical pattern:

- the user gives a short or context-dependent message;
- the assistant infers a likely task;
- the inferred task is not actually justified by the conversation.

Example shape:

```text
Assistant: I can rewrite it in a formal or casual tone.
User: formal
```

Correct behavior: continue with the formal rewrite.

Wrong intent inference would be explaining what the word "formal" means or asking unrelated questions.

### `unnecessary_clarification`

The assistant asks for clarification even though the intended action is already clear from context.

This is the main trade-off risk for Strict / Precision behavior. A strict assistant should not become a clarification machine.

### `needed_clarification_missing`

The assistant should ask a clarification because the user's intent is underdetermined, but it guesses instead.

This is common for isolated short fragments like:

```text
User: SSL
```

Without pending context, the user may be asking for a definition, translation, rewrite, debugging help, or something else.

### `correction_mishandled`

The assistant treats a correction as a new request instead of acknowledging and applying it.

Example shape:

```text
Assistant: The deadline is in 2024.
User: not 2024, 2025
```

Correct behavior: acknowledge the correction and update the relevant fact.

### `pending_task_missed`

The user clearly selects from a pending task, but the assistant fails to execute it.

Example shape:

```text
Assistant: Choose JSON or YAML.
User: JSON
```

Correct behavior: provide JSON directly.

Asking "Do you mean JSON?" is usually unnecessary.

## Non-core labels

### `other_failure`

Use this when the response fails for a reason unrelated to intent selection, such as:

- hallucinated facts;
- formatting failure;
- refusal where refusal is not warranted;
- severe irrelevance not explained by wrong intent inference.

## Action-level framing

The benchmark primarily checks whether the assistant selected the right action type:

- `answer_directly`
- `ask_clarification`
- `acknowledge_correction`
- `continue_pending_task`
- `avoid_unasked_execution`

Only after action correctness should the evaluator consider style, fluency, or completeness.

## Why this taxonomy matters

The point is to avoid vague judgments like "the answer feels bad".

A response should be judged by whether it chose the correct conversational action under the given context.
