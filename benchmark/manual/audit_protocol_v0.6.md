# Manual Audit Protocol v0.6

This protocol is for manually checking `strict-intent-bench` results without relying only on automated grading.

The goal is not to create a perfect human-evaluation system. The goal is to provide a simple, repeatable review process for a subset of benchmark cases.

## What to audit

Audit a mixed sample across all categories:

- `quoted_reply`
- `short_fragment`
- `acknowledgment_or_correction`
- `clear_direct`

For each audited case, review:

- the conversation context;
- the expected action;
- the assistant response;
- whether the response answered the intended task;
- whether the response asked an unnecessary clarification;
- whether the response failed to ask a needed clarification.

## Recommended sample

For a small audit:

- 5 cases per category;
- 20 total cases per language track.

For a stronger audit:

- 10 cases per category;
- 40 total cases per language track.

Keep the sample balanced. Do not only audit cases that make one intervention look good.

## Labels

Use these audit labels:

- `pass`: response chose the correct action and satisfied the success criteria.
- `wrong_intent_inference`: response answered a plausible but unstated request.
- `unnecessary_clarification`: response asked for clarification when the intended action was already clear.
- `needed_clarification_missing`: response should have asked a clarification but instead guessed.
- `other_failure`: response failed for another reason.

A response may have multiple failure labels if needed, but prefer the primary failure label when possible.

## Action-level check

Each case has an expected action:

- `answer_directly`
- `ask_clarification`
- `acknowledge_correction`
- `continue_pending_task`
- `avoid_unasked_execution`

The first audit question should be:

> Did the assistant choose the right action type?

Only after that should the auditor judge fluency or helpfulness.

## Avoid these mistakes

Do not mark a response as correct merely because it is fluent.

Do not reward a response for answering a useful question if that question was not actually asked.

Do not punish clarification when the user intent is genuinely underdetermined.

Do not reward clarification when the previous context already makes the intended action clear.

## Audit output format

Use a CSV with these columns:

```text
case_id,category,expected_action,response_source,audit_label,action_correct,notes
```

Where:

- `response_source` is `baseline`, `strict`, `manual`, or another clearly named source.
- `action_correct` is `true` or `false`.
- `notes` should briefly explain the decision.

## Why this matters

Automated grading is useful for fast iteration, but wrong intent inference is subtle. Manual audit helps check whether the benchmark is measuring real intent handling instead of only matching surface phrasing.
