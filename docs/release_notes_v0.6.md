# Release Notes v0.6

v0.6 turns `strict-intent-bench` from a result dump plus demo into a more inspectable benchmark package.

## Added

- Public summary: `reports/v0.6/public_summary.md`
- Dataset card: `docs/dataset_card.md`
- Error taxonomy: `docs/error_taxonomy.md`
- Annotation guidelines: `docs/annotation_guidelines.md`
- Case quality checklist: `docs/case_quality_checklist.md`
- Manual audit protocol: `benchmark/manual/audit_protocol_v0.6.md`
- No-API reproduction guide: `benchmark/manual/no_api_reproduction.md`
- Roadmap: `ROADMAP.md`
- Contributing guide: `CONTRIBUTING.md`

## Improved

- README now links the public documentation set.
- README now includes a no-API inspection section.
- The project is clearer about the distinction between:
  - measured results;
  - illustrative demo examples;
  - manual audit workflow;
  - future development targets.

## Why this matters

The benchmark should be inspectable without asking readers to trust private API runs.

v0.6 therefore focuses on documentation, auditability, and public review rather than new model claims.

## Main unresolved weakness

The main unresolved benchmark weakness remains the clarification trade-off:

- Strict / Precision reduces wrong-intent behavior on the current splits;
- but a naive strict mode can over-clarify;
- short fragments remain the hardest category.

## Next

v0.7 should focus on dataset quality:

- stronger case review;
- metadata consistency checks;
- clearer separation between source and mirror language tracks;
- audit-ready sample selection.
