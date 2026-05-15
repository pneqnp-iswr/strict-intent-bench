# Contributing

Contributions to `strict-intent-bench` should preserve the benchmark's narrow focus: measuring wrong intent inference and related clarification trade-offs in conversational assistants.

## What belongs here

Good contributions include:

- new benchmark cases for existing categories;
- clearer annotation rules;
- improved manual audit tooling;
- better result reporting;
- documentation that makes the benchmark easier to inspect;
- examples that reveal wrong-intent behavior without overclaiming.

## What does not belong here

Avoid contributions that turn the project into a generic chatbot benchmark.

Out of scope:

- broad factual QA evaluation;
- general preference ranking;
- jailbreak or safety testing;
- leaderboard-style model comparison without clear intent labels;
- claims that Strict / Precision is universally better;
- synthetic trick cases that no reasonable human could interpret.

## Adding cases

Before adding a case, read:

- `docs/dataset_card.md`
- `docs/error_taxonomy.md`
- `docs/annotation_guidelines.md`
- `docs/case_quality_checklist.md`

Every new case should make the expected conversational action explicit.

For v0.3+ cases, prefer including:

```json
{
  "expected_action": "...",
  "ambiguity_level": "low | medium | high",
  "pending_context_strength": "none | weak | strong",
  "operation_required": true,
  "notes": "..."
}
```

## Review checklist

A contribution is stronger if it answers:

1. What wrong-intent failure does this case test?
2. Why is the expected action recoverable from visible context?
3. Could a fluent answer still be wrong here?
4. Is clarification correct or unnecessary?
5. Does the case duplicate an existing pattern?

## Reporting results

When publishing or adding results, include:

- dataset file;
- model/version if known;
- intervention prompt;
- grader method;
- pass rate;
- wrong intent inference rate;
- unnecessary clarification rate;
- clarification rate;
- category breakdown;
- limitations.

## Tone of claims

Keep claims narrow.

Correct:

> On this small RU/EN benchmark split, Strict / Precision reduced wrong-intent errors while preserving or changing clarification behavior.

Incorrect:

> Strict prompting solves assistant reliability.

## Development without API access

No-API contributions are welcome if they improve:

- dataset validity;
- documentation;
- static demo;
- manual audit protocols;
- reproducibility instructions;
- case quality.

Measured model results require API access, but the project should remain inspectable without it.
