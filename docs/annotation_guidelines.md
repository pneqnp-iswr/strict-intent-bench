# Annotation Guidelines

These guidelines define how benchmark cases should be written and reviewed in `strict-intent-bench`.

The main target is **wrong intent inference**: cases where an assistant gives a plausible answer, but to a user intent that was not actually established by the conversation.

## Core principle

Annotate the intended conversational action before judging the text quality of the answer.

A response can be polished, detailed, and helpful-looking while still being wrong if it chooses the wrong action.

## Expected action labels

### `answer_directly`

Use when the user clearly asks a direct question or gives enough context to answer without clarification.

The assistant should answer the requested question, not ask for unnecessary clarification.

### `ask_clarification`

Use when the user's message is underdetermined and there is no strong pending context.

Typical examples:

```text
User: SSL
User: Wednesday
User: blue
```

These may refer to a definition, a translation, a selection, a rewrite, a debugging issue, or a prior task. If context does not disambiguate, clarification is correct.

### `acknowledge_correction`

Use when the user corrects a previous statement.

Example:

```text
Assistant: The event is in 2024.
User: not 2024, 2025
```

The assistant should acknowledge the correction and apply it. It should not treat the correction as a new unrelated request.

### `continue_pending_task`

Use when the user selects from a clearly established pending task.

Example:

```text
Assistant: I can output this as JSON or YAML.
User: JSON
```

The assistant should continue with JSON directly. Clarifying again is usually unnecessary.

### `avoid_unasked_execution`

Use when the user quotes, repeats, or references part of the prior answer but does not actually request an operation.

The assistant should not automatically rewrite, translate, summarize, calculate, or execute a new task unless the operation is clear from context.

## Ambiguity levels

### `low`

The intended action is clear from the immediate conversation.

Incorrect clarification is likely `unnecessary_clarification`.

### `medium`

There is some context, but more than one reasonable action remains possible.

A short clarification may be acceptable.

### `high`

The user's message is too short or context-free to infer the intended operation.

Guessing is likely `needed_clarification_missing` or `wrong_intent_inference`.

## Pending context strength

### `none`

There is no active task or previous option that disambiguates the user's message.

### `weak`

There is some related context, but it does not uniquely determine the intended action.

### `strong`

The prior assistant turn clearly establishes a pending task, choice, or output format.

When pending context is strong, the model should usually continue rather than clarify.

## Writing good cases

A good case should have:

- a compact conversation;
- one main intended action;
- a clear failure mode;
- realistic user phrasing;
- a success criterion that can be checked without mind-reading;
- no hidden assumptions outside the provided messages.

## Writing bad cases

Avoid cases that require:

- private knowledge not shown in the messages;
- broad factual research;
- subjective style preferences with no stated target;
- multiple unrelated tasks at once;
- hidden author intent that is not recoverable from context.

## Review checklist

For each case, ask:

1. Is the correct action type clear?
2. Is the category appropriate?
3. Is the case testing intent selection rather than general intelligence?
4. Would a fluent but wrong-action response be counted as failure?
5. Would an unnecessary clarification be counted correctly?
6. Would a missing clarification be counted correctly?
7. Are `acceptable_actions` and `success_criteria` aligned?

## Style guidance

Keep user messages realistic. Short fragments should look like real chat turns, not synthetic riddles.

Keep assistant context minimal but sufficient.

Do not make every case adversarial. The goal is to test a common reliability failure, not to trick the model with impossible prompts.
