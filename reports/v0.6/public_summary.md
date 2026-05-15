# v0.6 Public Summary

`strict-intent-bench` is a small reproducible benchmark for **wrong intent inference** in conversational AI assistants.

Wrong intent inference is the failure mode where an assistant gives a plausible answer, but to the wrong implied user request. The answer may be fluent, useful-looking, and locally reasonable, while still being grounded in the wrong interpretation of the user's message.

## What this project tests

The benchmark focuses on conversational turns where user intent is easy to over-infer:

- `quoted_reply`: the user quotes a phrase from the assistant's previous answer.
- `short_fragment`: the user sends a short fragment such as `SSL`, `blue`, or `Wednesday`.
- `acknowledgment_or_correction`: the user acknowledges or corrects a previous answer.
- `clear_direct`: the user clearly selects from an existing pending task.

These are not exotic failures. They are common conversational boundary cases where a model can appear helpful while actually starting from the wrong task.

## Tested intervention

The current tested intervention is **Strict / Precision v8**.

It is not treated as the whole project. It is one behavior-layer intervention tested against a no-prompt baseline on the same benchmark cases.

The intended behavior is simple:

- do not execute an unstated task;
- ask a short clarification only when the user's intent is underdetermined;
- acknowledge corrections instead of treating them as new requests;
- continue directly when the user clearly selects from a pending task.

## Main published result

The strongest published run is the RU/EN holdout-v2 comparison.

| Split | Method | Pass rate ↑ | Wrong intent inference ↓ | Unnecessary clarification ↓ |
|---|---:|---:|---:|---:|
| RU holdout v2 | No prompt baseline | 35.0% | 42.5% | 15.0% |
| RU holdout v2 | Strict / Precision v8 | **77.5%** | **10.0%** | **12.5%** |
| EN holdout v2 | No prompt baseline | 47.5% | 32.5% | **10.0%** |
| EN holdout v2 | Strict / Precision v8 | **72.5%** | **22.5%** | **10.0%** |

Interpretation: the intervention improves pass rate and reduces wrong-intent errors on these benchmark splits. The result should be read as a narrow benchmark result, not a universal claim about assistant behavior.

## Clarification trade-off

The central open weakness is not only wrong intent inference. It is the trade-off between:

- reducing wrong assumptions; and
- avoiding unnecessary clarification.

A naive strict mode can become too cautious. The next meaningful improvement is not simply increasing the number of cases. It is reducing unnecessary clarification while preserving the wrong-intent reduction.

## Why v0.6 exists

v0.6 is focused on public credibility and inspection:

- live static demo;
- side-by-side illustrative examples;
- benchmark case browser;
- no-API reproduction path;
- manual audit protocol;
- clear limitations.

The point is to make the artifact inspectable without asking readers to trust private scripts or private API runs.

## What this project does not claim

This project does not claim that:

- Strict / Precision solves assistant reliability;
- the current dataset is large enough for broad product conclusions;
- prompt-layer intervention is equivalent to model training;
- illustrative demo examples are measured API outputs;
- one benchmark category captures all forms of user-intent handling.

The strongest supported claim is narrower: wrong intent inference is measurable, and this repository provides a small public benchmark and demo for inspecting it.

## Next target

A meaningful next result would show:

- wrong intent inference remains low;
- unnecessary clarification decreases;
- short-fragment behavior improves;
- manual audit confirms the automated grading trend.
