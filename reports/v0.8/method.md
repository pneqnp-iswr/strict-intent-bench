# v0.8 Method: Clarification Trade-off Analysis

v0.8 focuses on measuring the clarification trade-off more directly.

The goal is not to add a new dataset or make a new model claim. The goal is to make existing and future evaluation results easier to inspect through action-level and metadata-aware metrics.

## Motivation

Earlier results show the core trade-off:

- Strict / Precision can reduce wrong intent inference;
- but it can also increase clarification behavior;
- a useful strict mode should avoid guessing without becoming a clarification machine.

This is why v0.8 separates general clarification rate from more specific failures such as over-clarification on clear pending tasks.

## Analyzer

Tool:

```text
tools/analyze_clarification_tradeoff.py
```

Inputs:

```text
--case-results path/to/case_results.csv
--dataset path/to/dataset.jsonl
--output-md path/to/report.md
--output-json path/to/report.json
```

The tool does not call any API. It only reads existing graded outputs and dataset metadata.

## Metrics

The analyzer reports:

- `action_accuracy`
- `wrong_intent_inference_rate`
- `clarification_rate`
- `unnecessary_clarification_rate`
- `overclarification_on_clear_direct_rate`
- `overclarification_on_strong_pending_context_rate`
- `underclarification_on_high_ambiguity_short_fragment_rate`
- action accuracy by `expected_action`
- wrong intent inference by `expected_action`
- clarification rate by `ambiguity_level`
- clarification rate by `pending_context_strength`
- baseline vs strict deltas

## Metadata requirement

Full v0.8 analysis requires v0.3-style metadata:

```text
expected_action
ambiguity_level
pending_context_strength
operation_required
notes
```

Without this metadata, the analyzer can still report broad metrics such as wrong-intent rate and clarification rate, but action-level metrics become partial or diagnostic only.

## Current partial result

The old English holdout-v2 result can be analyzed only partially because `benchmark/data/holdout_cases_en_v2.jsonl` has 0% coverage for v0.3 metadata fields.

Partial English holdout-v2 result:

- wrong intent inference: baseline 32.5%, strict 22.5%
- clarification rate: baseline 22.5%, strict 37.5%
- unnecessary clarification: baseline 10.0%, strict 10.0%
- over-clarification on clear-direct cases: baseline 10.0%, strict 20.0%

This supports the v0.8 motivation: the intervention reduces wrong-intent behavior on this run, but increases clarification behavior.

## Known issue in old RU holdout-v2 result

The old RU holdout-v2 result file appears to contain English-style case ids such as `holdout2_*_en_*`, while the RU dataset uses `holdout2_*_ru_*` ids.

Because of that id mismatch, the old RU holdout-v2 CSV should not be used for metadata-aware v0.8 analysis unless the source/result alignment is corrected.

## Full v0.8 target

A full v0.8 result should run evaluation on:

```text
benchmark/data/v0.3/dev_en_v3.jsonl
benchmark/data/v0.3/dev_ru_v3.jsonl
```

Then analyze the resulting `case_results.csv` files with:

```text
tools/analyze_clarification_tradeoff.py
```

Success condition:

- wrong intent inference remains low;
- unnecessary clarification does not rise materially;
- over-clarification on strong pending context is visible and controlled;
- under-clarification on high-ambiguity short fragments is visible and controlled.

## Non-goals

v0.8 does not claim:

- that Strict / Precision is universally better;
- that old holdout-v2 files provide full metadata-aware analysis;
- that automated grading replaces manual audit;
- that structural metadata proves semantic quality.
