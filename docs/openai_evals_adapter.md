# OpenAI Evals Adapter

This document describes how to adapt `strict-intent-bench` to an OpenAI-style model optimization workflow.

The goal is not to replace the existing local runner. The goal is to make the benchmark easier to inspect, export, and reuse as an eval artifact.

## Why this adapter exists

OpenAI's model optimization workflow starts with evals: define test inputs, establish a baseline, measure prompt/model behavior, then iterate on prompts or training data based on measured feedback.

`strict-intent-bench` already follows that loop locally:

1. define conversational cases;
2. run a no-prompt baseline;
3. run a Strict / Precision prompt variant;
4. grade action selection;
5. inspect failures;
6. update the behavior prompt;
7. rerun smaller checks before scaling back to full evaluation.

The adapter makes that workflow more explicit and portable.

## What gets exported

The exporter converts the repository's JSONL cases into OpenAI-eval-style JSONL items.

Each exported row has this shape:

```json
{
  "item": {
    "id": "dev_en_v3_short_01",
    "title": "...",
    "category": "short_fragment",
    "conversation": [
      {"role": "assistant", "content": "..."},
      {"role": "user", "content": "..."}
    ],
    "acceptable_actions": ["clarify"],
    "expected_action": "ask_clarification",
    "success_criteria": "...",
    "ambiguity_level": "high",
    "pending_context_strength": "weak",
    "operation_required": "...",
    "notes": "..."
  }
}
```

This keeps both the conversational input and the benchmark metadata together.

## Export command

Run:

```bash
python tools/export_openai_eval_items.py \
  --dataset benchmark/data/v0.3/dev_en_v3.jsonl \
  --output benchmark/data/openai_eval_items/dev_en_v3_items.jsonl
```

For the current v0.8 full English set, use:

```bash
python tools/export_openai_eval_items.py --dataset benchmark/data/v0.3/dev_en_v3.jsonl --output benchmark/data/openai_eval_items/dev_en_v3_items.jsonl
```

For smaller diagnostic splits:

```bash
python tools/export_openai_eval_items.py --dataset benchmark/data/v0.3/dev_en_v3_balanced_16.jsonl --output benchmark/data/openai_eval_items/dev_en_v3_balanced_16_items.jsonl

python tools/export_openai_eval_items.py --dataset benchmark/data/v0.3/dev_en_v3_unseen_balanced_16.jsonl --output benchmark/data/openai_eval_items/dev_en_v3_unseen_balanced_16_items.jsonl

python tools/export_openai_eval_items.py --dataset benchmark/data/v0.3/dev_en_v3_v13_failures_21.jsonl --output benchmark/data/openai_eval_items/dev_en_v3_v13_failures_21_items.jsonl
```

## Recommended evaluation mapping

Each item should be evaluated as a two-turn conversation:

1. assistant context message;
2. user reply;
3. candidate assistant response.

The grader should decide whether the candidate selected the correct action:

- `answer_directly`
- `ask_clarification`
- `acknowledge_correction`
- `continue_pending_task`
- `avoid_unasked_execution`

The grader should also record:

- whether wrong intent inference occurred;
- whether an unnecessary clarification occurred;
- whether a needed clarification was missed;
- a short explanation.

## Suggested grader output

A grader should return JSON like:

```json
{
  "verdict": "pass",
  "primary_action": "clarify",
  "wrong_intent_inference": false,
  "unnecessary_clarification": false,
  "notes": "The user sent a standalone fragment with no clear operation, so a short clarification was appropriate."
}
```

The existing local grader already uses this style.

## Current v0.8 benchmark result

Current English v0.8 champion:

```text
baselines/strict_v13_unseen_pending/strict.txt
```

Full EN 80 result:

| Metric | Baseline | Strict v13 | Delta |
|---|---:|---:|---:|
| action_accuracy | 38.8 | 66.2 | +27.4 |
| wrong_intent_inference_rate | 37.5 | 5.0 | -32.5 |
| metadata_unnecessary_clarification_rate | 15.0 | 11.2 | -3.8 |
| metadata_needed_clarification_missing_rate | 30.0 | 15.0 | -15.0 |

The main claim is narrow:

```text
On the English v0.3 development set of 80 cases, Strict / Precision v13 improved action accuracy from 38.8% to 66.2% and reduced wrong intent inference from 37.5% to 5.0%.
```

## Why this is not fine-tuning yet

This benchmark is currently too small for a serious fine-tuning claim.

The right order is:

1. stabilize the eval;
2. improve grader reliability;
3. expand the dataset;
4. test across more models;
5. only then consider fine-tuning or preference optimization.

For now, `strict-intent-bench` is best treated as an eval-first prompt-behavior benchmark.

## Next adapter work

Recommended next steps:

1. Add an example exported JSONL artifact under `benchmark/data/openai_eval_items/`.
2. Add a dashboard setup note once the exact OpenAI Eval UI configuration is verified.
3. Add a stronger-grader final-report workflow.
4. Add model-family comparison runs after v0.8 is frozen.
