# Dataset Quality Audit

Dataset: `benchmark/data/v0.3/dev_ru_v3.jsonl`

Cases: **80**

## Summary

Errors: **0**
Warnings: **15**

## Category balance

- `acknowledgment_or_correction`: 20
- `clear_direct`: 20
- `quoted_reply`: 20
- `short_fragment`: 20

## Expected action balance

- `acknowledge_correction`: 12
- `answer_directly`: 7
- `ask_clarification`: 31
- `avoid_unasked_execution`: 4
- `continue_pending_task`: 26

## Ambiguity balance

- `high`: 10
- `low`: 45
- `medium`: 25

## Pending context balance

- `none`: 5
- `strong`: 33
- `weak`: 42

## Issues

- **warning** `dev_ru_v3_short_08`: notes field is very short
- **warning** `dev_ru_v3_short_10`: notes field is very short
- **warning** `dev_ru_v3_short_14`: notes field is very short
- **warning** `dev_ru_v3_short_17`: notes field is very short
- **warning** `dev_ru_v3_short_20`: notes field is very short
- **warning** `dev_ru_v3_ack_04`: notes field is very short
- **warning** `dev_ru_v3_ack_10`: notes field is very short
- **warning** `dev_ru_v3_clear_01`: notes field is very short
- **warning** `dev_ru_v3_clear_05`: notes field is very short
- **warning** `dev_ru_v3_clear_06`: notes field is very short
- **warning** `dev_ru_v3_clear_10`: notes field is very short
- **warning** `dev_ru_v3_clear_12`: notes field is very short
- **warning** `dev_ru_v3_clear_14`: notes field is very short
- **warning** `dev_ru_v3_clear_15`: notes field is very short
- **warning** `dev_ru_v3_clear_19`: notes field is very short

## Note

This audit is heuristic. It flags cases for review; it does not replace manual judgment.
