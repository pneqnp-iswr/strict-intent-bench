# No-API Reproduction Guide

This guide explains how to inspect and partially reproduce `strict-intent-bench` without paid API access.

The no-API path is not a replacement for full measured model evaluation. It is for public inspection, dataset validation, manual review, and low-cost development.

## 1. Inspect the live demo

Open the static demo:

```text
https://pneqnp-iswr.github.io/strict-intent-bench/
```

The demo includes:

- side-by-side illustrative examples;
- benchmark case browsing;
- filters for category and expected action metadata;
- measured summary bars from existing published runs.

The side-by-side examples are illustrative unless explicitly marked as measured outputs.

## 2. Validate datasets locally

Install Python 3.10+.

Then run:

```bash
python tools/validate_dataset.py benchmark/data/v0.3/dev_en_v3.jsonl --require-v03
python tools/validate_dataset.py benchmark/data/v0.3/dev_ru_v3.jsonl --require-v03
```

This checks that the v0.3 JSONL files are valid and include the expected schema fields.

## 3. Regenerate demo data

```bash
python tools/export_demo_cases.py
```

This reads the v0.3 EN/RU JSONL files and writes:

```text
docs/demo_cases.json
```

The static demo reads this JSON file directly.

## 4. Serve the demo locally

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/docs/demo.html
```

## 5. Manual review workflow

Create a manual evaluation sheet:

```bash
python tools/make_manual_eval_sheet.py \
  --dataset benchmark/data/v0.3/dev_en_v3.jsonl \
  --output manual/v0.3_dev_en_manual.csv \
  --max-cases 20
```

Fill the response and audit fields manually.

Then score the completed sheet:

```bash
python tools/score_manual_eval.py \
  --input manual/v0.3_dev_en_manual.csv \
  --output-dir results/no_api_manual_en
```

## 6. Optional heuristic smoke test

A heuristic grader can be used only for development smoke tests:

```bash
python tools/heuristic_grade_manual_eval.py \
  --input manual/v0.3_dev_en_manual.csv \
  --output manual/v0.3_dev_en_manual.heuristic.csv \
  --overwrite-existing
```

Then score:

```bash
python tools/score_manual_eval.py \
  --input manual/v0.3_dev_en_manual.heuristic.csv \
  --output-dir results/no_api_heuristic_en
```

Do not use heuristic results as strong public evidence. They are useful for catching obvious mistakes and testing the workflow.

## What no-API reproduction can verify

It can verify:

- dataset validity;
- case categories;
- expected action metadata;
- public demo behavior;
- manual audit protocol;
- rough qualitative examples.

It cannot fully verify:

- live model behavior;
- exact pass-rate claims from API runs;
- automated grader consistency across model versions;
- future model behavior after provider updates.

## Recommended public wording

When using no-API artifacts, say:

> This repository is inspectable without API access. Full measured model runs require API access, but the dataset, demo, manual audit protocol, and existing published result files are public.
