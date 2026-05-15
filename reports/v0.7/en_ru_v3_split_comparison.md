# Dataset Split Comparison

Left split: `benchmark/data/v0.3/dev_en_v3.jsonl`
Right split: `benchmark/data/v0.3/dev_ru_v3.jsonl`
Language-id normalization: **on**

## Size

- `dev_en_v3` cases: **80**
- `dev_ru_v3` cases: **80**
- shared comparable ids: **80**
- left-only comparable ids: **0**
- right-only comparable ids: **0**

## `category` balance

| Value | dev_en_v3 | dev_ru_v3 | Delta |
|---|---:|---:|---:|
| `acknowledgment_or_correction` | 20 | 20 | +0 |
| `clear_direct` | 20 | 20 | +0 |
| `quoted_reply` | 20 | 20 | +0 |
| `short_fragment` | 20 | 20 | +0 |

## `expected_action` balance

| Value | dev_en_v3 | dev_ru_v3 | Delta |
|---|---:|---:|---:|
| `acknowledge_correction` | 12 | 12 | +0 |
| `answer_directly` | 7 | 7 | +0 |
| `ask_clarification` | 31 | 31 | +0 |
| `avoid_unasked_execution` | 4 | 4 | +0 |
| `continue_pending_task` | 26 | 26 | +0 |

## `ambiguity_level` balance

| Value | dev_en_v3 | dev_ru_v3 | Delta |
|---|---:|---:|---:|
| `high` | 10 | 10 | +0 |
| `low` | 45 | 45 | +0 |
| `medium` | 25 | 25 | +0 |

## `pending_context_strength` balance

| Value | dev_en_v3 | dev_ru_v3 | Delta |
|---|---:|---:|---:|
| `none` | 5 | 5 | +0 |
| `strong` | 33 | 33 | +0 |
| `weak` | 42 | 42 | +0 |

## Category × expected action

| Category | Expected action | Left | Right | Delta |
|---|---|---:|---:|---:|
| `acknowledgment_or_correction` | `acknowledge_correction` | 12 | 12 | +0 |
| `acknowledgment_or_correction` | `ask_clarification` | 3 | 3 | +0 |
| `acknowledgment_or_correction` | `continue_pending_task` | 5 | 5 | +0 |
| `clear_direct` | `answer_directly` | 7 | 7 | +0 |
| `clear_direct` | `continue_pending_task` | 13 | 13 | +0 |
| `quoted_reply` | `ask_clarification` | 16 | 16 | +0 |
| `quoted_reply` | `avoid_unasked_execution` | 4 | 4 | +0 |
| `short_fragment` | `ask_clarification` | 12 | 12 | +0 |
| `short_fragment` | `continue_pending_task` | 8 | 8 | +0 |

## Note

This comparison checks structural balance only. It does not prove semantic equivalence between language tracks.
Language-id normalization treats ids like `dev_en_v3_short_01` and `dev_ru_v3_short_01` as comparable slots.
