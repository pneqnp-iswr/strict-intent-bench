# v0.7 Summary: Dataset Quality and Auditability

v0.7 focuses on dataset quality tooling and auditability for the v0.3 English/Russian development splits.

This release does not add new model claims. It improves the project by making the benchmark data easier to validate, compare, and inspect without API access.

## What was added

### Dataset quality audit

Tool:

```text
tools/audit_dataset_quality.py
```

Purpose:

- validate category and expected-action metadata;
- detect duplicate ids and duplicate message signatures;
- flag weak or underspecified notes;
- flag suspicious action/context combinations;
- produce Markdown reports.

### Dataset split comparison

Tool:

```text
tools/compare_dataset_splits.py
```

Purpose:

- compare EN/RU split size;
- compare category balance;
- compare expected-action balance;
- compare ambiguity and pending-context metadata;
- normalize language-prefixed ids such as `dev_en_v3_short_01` and `dev_ru_v3_short_01` into comparable slots.

### RU note cleanup

Tool:

```text
tools/expand_ru_v3_notes.py
```

Purpose:

- expand short notes in the Russian v0.3 development split;
- remove the final `notes field is very short` warnings from the quality audit;
- keep the update targeted and reproducible.

## Final v0.7 audit result

### English v0.3 development split

Report:

```text
reports/v0.7/dev_en_v3_quality.md
```

Result:

- cases: **80**
- errors: **0**
- warnings: **0**

### Russian v0.3 development split

Report:

```text
reports/v0.7/dev_ru_v3_quality.md
```

Result:

- cases: **80**
- errors: **0**
- warnings: **0**

### EN/RU split comparison

Report:

```text
reports/v0.7/en_ru_v3_split_comparison.md
```

Result:

- EN cases: **80**
- RU cases: **80**
- shared comparable ids: **80**
- left-only comparable ids: **0**
- right-only comparable ids: **0**
- category balance: matched exactly
- expected-action balance: matched exactly
- ambiguity-level balance: matched exactly
- pending-context-strength balance: matched exactly

## Interpretation

v0.7 closes the dataset-quality pass for the current v0.3 EN/RU development splits.

This does not prove semantic equivalence between English and Russian cases, and it does not replace manual audit. It does establish that the current splits are structurally balanced and pass the project’s heuristic quality checks.

## Remaining limitations

- The audit is heuristic.
- Structural balance does not prove semantic equivalence.
- Manual review is still needed.
- The dataset remains small.
- The strongest remaining behavior problem is still the clarification trade-off, especially around short fragments.

## Next planned version

v0.8 should focus on measuring the clarification trade-off more directly:

- over-clarification on clear pending tasks;
- under-clarification on genuinely ambiguous short fragments;
- action accuracy by expected action;
- ambiguity-level breakdowns.
