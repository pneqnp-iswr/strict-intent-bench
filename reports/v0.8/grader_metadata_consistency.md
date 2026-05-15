# Grader / Metadata Consistency

v0.8 reports both raw grader flags and metadata-normalized clarification checks.

This is necessary because the automated grader and the dataset metadata answer related but different questions.

## Two sources of truth

### Grader flags

The evaluator writes fields such as:

```text
grade_primary_action
grade_unnecessary_clarification
grade_wrong_intent_inference
```

These are useful because they describe the judged model response.

However, a grader can be too broad. In a smoke run, it may mark a clarification as unnecessary even when the dataset expected action is `ask_clarification`.

### Dataset metadata

v0.3 cases include:

```text
expected_action
ambiguity_level
pending_context_strength
operation_required
notes
```

These fields describe what the benchmark case is intended to test.

They are especially important for the clarification trade-off because not every clarification is bad.

## Why disagreement happens

A disagreement can occur when:

- the grader treats any clarification as unnecessary;
- the dataset expects clarification because the user intent is genuinely underdetermined;
- the expected action allows more than one safe behavior;
- `avoid_unasked_execution` permits a narrow clarification or acknowledgment;
- old datasets lack v0.3 metadata entirely.

## Metadata-normalized metrics

The v0.8 analyzer adds alias-aware checks:

- `metadata_unnecessary_clarification_rate`
- `metadata_needed_clarification_missing_rate`
- `grader_metadata_conflict_rate`

These do not replace raw grader metrics. They make the conflict visible.

## Alias-aware handling

The analyzer does not use the blunt rule:

```text
clarification + expected_action != ask_clarification => unnecessary
```

That would be wrong for cases where `avoid_unasked_execution` permits clarification as one valid response.

Instead, it checks whether the graded primary action is compatible with the expected action alias set.

## Smoke run policy

Before larger API runs, use a small smoke run to check:

- API access works;
- result files are written;
- metadata coverage is nonzero;
- analyzer output is coherent;
- grader/metadata conflicts are visible.

Do not spend budget on larger runs while the measurement layer is internally inconsistent.

## Reporting rule

When reporting v0.8 results, include both:

- raw `unnecessary_clarification_rate` from the grader;
- metadata-normalized clarification metrics from the analyzer.

This prevents overclaiming and makes grader disagreement inspectable.
