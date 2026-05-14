# v0.2 benchmark expansion

This directory contains the v0.2 expanded development splits for `strict-intent-bench`.

Generated files:

- `dev_en_v2.jsonl` — 80 English development cases
- `dev_ru_v2.jsonl` — 80 Russian development cases

Each development split contains exactly:

- 20 `quoted_reply` cases
- 20 `short_fragment` cases
- 20 `acknowledgment_or_correction` cases
- 20 `clear_direct` cases

## Purpose

v0.2 expands the benchmark beyond the v0.1 proof-of-concept. The goal is to improve category balance, add more hard cases, and stress-test the remaining weak category: `short_fragment`.

The v0.2 dev splits are **not hidden test sets**. They are public development sets for dataset expansion, prompt/error analysis, and benchmark refinement.

Hidden-ish holdout files such as `holdout_en_v3.jsonl` and `holdout_ru_v3.jsonl` should be created separately only after the tested intervention is frozen.

## Methodological note

Do not tune a prompt repeatedly on these files and then present the result as an independent holdout score. Treat these files as development/evaluation material, not final proof.

## Current scope

This v0.2 step does not add:

- leaderboard infrastructure
- a hidden evaluation server
- arXiv-style paper packaging
- 500+ cases
- a new `strict_v9` or `strict_v10` prompt

The current best tested intervention remains `baselines/strict_v8/strict.txt`.
