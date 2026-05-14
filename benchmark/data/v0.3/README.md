# v0.3 development splits

v0.3 focuses on the clarification trade-off: reducing over-clarification while preserving the reduction in wrong intent inference.

Files:

- `dev_en_v3.jsonl` — 80 English cases
- `dev_ru_v3.jsonl` — 80 Russian cases

Each file contains exactly 20 cases per category:

- `quoted_reply`
- `short_fragment`
- `acknowledgment_or_correction`
- `clear_direct`

## Optional v0.3 fields

Cases may include:

- `expected_action`: `answer_directly`, `ask_clarification`, `acknowledge_correction`, `continue_pending_task`, or `avoid_unasked_execution`
- `ambiguity_level`: `low`, `medium`, or `high`
- `pending_context_strength`: `none`, `weak`, or `strong`
- `operation_required`: boolean
- `notes`: short explanation of why the expected action is correct

The evaluation runner treats these fields as optional, so older v0.1/v0.2 JSONL files remain valid.
