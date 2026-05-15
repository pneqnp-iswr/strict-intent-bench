# Roadmap

This roadmap tracks the next development targets for `strict-intent-bench`.

The project goal is not to prove that one prompt solves assistant reliability. The goal is to build a clean, inspectable benchmark for one measurable failure mode: wrong intent inference.

## v0.6: Public inspection package

Status: done.

Focus:

- public static demo;
- public summary;
- manual audit protocol;
- no-API reproduction guide;
- error taxonomy.

Purpose:

Make the benchmark understandable without requiring readers to trust private scripts or private API runs.

## v0.7: Dataset quality and auditability

Status: next.

Focus:

- add a dataset card;
- document annotation rules;
- add case-quality checklist;
- improve metadata consistency;
- separate illustrative examples from measured model outputs more explicitly.

Success condition:

A reader should be able to understand how cases are constructed, what each label means, and how to review a case without asking the author.

## v0.8: Clarification trade-off measurement

Status: planned.

Focus:

- measure over-clarification on clear pending tasks;
- measure under-clarification on genuinely ambiguous short fragments;
- report action accuracy by expected action;
- report ambiguity-level breakdowns.

Success condition:

Show whether Strict / Precision can reduce wrong intent inference without becoming too cautious.

## v0.9: Manual audit release

Status: planned.

Focus:

- manually audit a balanced subset of cases;
- publish audit CSV;
- compare manual labels with automated grading;
- document disagreement examples.

Success condition:

The benchmark should not rely only on automated grading. A small manual audit should confirm whether the metric is tracking the intended behavior.

## v1.0: Stable benchmark release

Status: open.

Focus:

- freeze a stable dataset split;
- freeze schema version;
- publish a clean report;
- include limitations prominently;
- avoid overclaiming.

Success condition:

A stable version that can be cited, inspected, and rerun.

## Non-goals

The roadmap does not target:

- proving that Strict / Precision is universally better;
- replacing full human evaluation;
- benchmarking every assistant behavior failure;
- optimizing for leaderboard-style claims;
- hiding weaknesses such as short-fragment ambiguity and over-clarification.
