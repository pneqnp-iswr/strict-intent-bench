# Clarification Trade-off Analysis

Case results: `results\v0.8-dev-en-v13-failures-21-v15-regrade-g54\case_results.csv`
Dataset metadata: `benchmark\data\v0.3\dev_en_v3_v13_failures_21.jsonl`

## Metadata coverage

Dataset cases: **21**
Fully annotated cases: **21** (100.0%)
| metadata_field | present | missing | coverage_rate |
|---|---|---|---|
| ambiguity_level | 21 | 0 | 100.0 |
| expected_action | 21 | 0 | 100.0 |
| notes | 21 | 0 | 100.0 |
| operation_required | 21 | 0 | 100.0 |
| pending_context_strength | 21 | 0 | 100.0 |

## Summary by mode

| mode | cases | metadata_available_cases | action_accuracy | wrong_intent_inference_rate | clarification_rate | unnecessary_clarification_rate | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate | overclarification_on_clear_direct_rate | overclarification_on_strong_pending_context_rate | underclarification_on_high_ambiguity_short_fragment_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 21 | 21 | 28.6 | 42.9 | 23.8 | 19.0 | 23.8 | 28.6 | 4.8 | 42.9 | 45.5 | 100.0 |
| strict | 21 | 21 | 66.7 | 14.3 | 38.1 | 19.0 | 19.0 | 9.5 | 0.0 | 14.3 | 36.4 | 0.0 |

## Metadata-normalized clarification checks

| mode | cases | metadata_available_cases | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate |
|---|---|---|---|---|---|
| baseline | 21 | 21 | 23.8 | 28.6 | 4.8 |
| strict | 21 | 21 | 19.0 | 9.5 | 0.0 |

These checks are alias-aware: a clarification can be valid for `avoid_unasked_execution`, so it is not automatically treated as unnecessary merely because `expected_action != ask_clarification`.

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 28.6 | 66.7 | 38.1 |
| wrong_intent_inference_rate | 42.9 | 14.3 | -28.6 |
| clarification_rate | 23.8 | 38.1 | 14.3 |
| unnecessary_clarification_rate | 19.0 | 19.0 | 0.0 |
| metadata_unnecessary_clarification_rate | 23.8 | 19.0 | -4.8 |
| metadata_needed_clarification_missing_rate | 28.6 | 9.5 | -19.1 |
| grader_metadata_conflict_rate | 4.8 | 0.0 | -4.8 |
| overclarification_on_clear_direct_rate | 42.9 | 14.3 | -28.6 |
| overclarification_on_strong_pending_context_rate | 45.5 | 36.4 | -9.1 |
| underclarification_on_high_ambiguity_short_fragment_rate | 100.0 | 0.0 | -100.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 4 | 4 | 50.0 |
| answer_directly | 3 | 3 | 66.7 |
| ask_clarification | 6 | 6 | 0.0 |
| continue_pending_task | 8 | 8 | 25.0 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 4 | 4 | 100.0 |
| answer_directly | 3 | 3 | 100.0 |
| ask_clarification | 6 | 6 | 66.7 |
| continue_pending_task | 8 | 8 | 37.5 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 4 | 75.0 |
| answer_directly | 3 | 33.3 |
| ask_clarification | 6 | 33.3 |
| continue_pending_task | 8 | 37.5 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 4 | 0.0 |
| answer_directly | 3 | 0.0 |
| ask_clarification | 6 | 0.0 |
| continue_pending_task | 8 | 37.5 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 3 | 0.0 |
| low | 15 | 33.3 |
| medium | 3 | 0.0 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 3 | 100.0 |
| low | 15 | 26.7 |
| medium | 3 | 33.3 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 0.0 |
| strong | 11 | 45.5 |
| weak | 9 | 0.0 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 0.0 |
| strong | 11 | 36.4 |
| weak | 9 | 44.4 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
