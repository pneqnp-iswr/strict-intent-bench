# Clarification Trade-off Analysis

Case results: `results\v0.8-dev-en-full-80-v13-unseen-pending\case_results.csv`
Dataset metadata: `benchmark\data\v0.3\dev_en_v3.jsonl`

## Metadata coverage

Dataset cases: **80**
Fully annotated cases: **80** (100.0%)
| metadata_field | present | missing | coverage_rate |
|---|---|---|---|
| ambiguity_level | 80 | 0 | 100.0 |
| expected_action | 80 | 0 | 100.0 |
| notes | 80 | 0 | 100.0 |
| operation_required | 80 | 0 | 100.0 |
| pending_context_strength | 80 | 0 | 100.0 |

## Summary by mode

| mode | cases | metadata_available_cases | action_accuracy | wrong_intent_inference_rate | clarification_rate | unnecessary_clarification_rate | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate | overclarification_on_clear_direct_rate | overclarification_on_strong_pending_context_rate | underclarification_on_high_ambiguity_short_fragment_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 80 | 80 | 38.8 | 37.5 | 23.8 | 16.2 | 15.0 | 30.0 | 2.5 | 35.0 | 36.4 | 60.0 |
| strict | 80 | 80 | 66.2 | 5.0 | 38.8 | 16.2 | 11.2 | 15.0 | 7.5 | 25.0 | 24.2 | 0.0 |

## Metadata-normalized clarification checks

| mode | cases | metadata_available_cases | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate |
|---|---|---|---|---|---|
| baseline | 80 | 80 | 15.0 | 30.0 | 2.5 |
| strict | 80 | 80 | 11.2 | 15.0 | 7.5 |

These checks are alias-aware: a clarification can be valid for `avoid_unasked_execution`, so it is not automatically treated as unnecessary merely because `expected_action != ask_clarification`.

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 38.8 | 66.2 | 27.4 |
| wrong_intent_inference_rate | 37.5 | 5.0 | -32.5 |
| clarification_rate | 23.8 | 38.8 | 15.0 |
| unnecessary_clarification_rate | 16.2 | 16.2 | 0.0 |
| metadata_unnecessary_clarification_rate | 15.0 | 11.2 | -3.8 |
| metadata_needed_clarification_missing_rate | 30.0 | 15.0 | -15.0 |
| grader_metadata_conflict_rate | 2.5 | 7.5 | 5.0 |
| overclarification_on_clear_direct_rate | 35.0 | 25.0 | -10.0 |
| overclarification_on_strong_pending_context_rate | 36.4 | 24.2 | -12.2 |
| underclarification_on_high_ambiguity_short_fragment_rate | 60.0 | 0.0 | -60.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 12 | 12 | 66.7 |
| answer_directly | 7 | 7 | 85.7 |
| ask_clarification | 31 | 31 | 22.6 |
| avoid_unasked_execution | 4 | 4 | 0.0 |
| continue_pending_task | 26 | 26 | 38.5 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 12 | 12 | 75.0 |
| answer_directly | 7 | 7 | 71.4 |
| ask_clarification | 31 | 31 | 61.3 |
| avoid_unasked_execution | 4 | 4 | 100.0 |
| continue_pending_task | 26 | 26 | 61.5 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 12 | 16.7 |
| answer_directly | 7 | 0.0 |
| ask_clarification | 31 | 61.3 |
| avoid_unasked_execution | 4 | 75.0 |
| continue_pending_task | 26 | 23.1 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 12 | 16.7 |
| answer_directly | 7 | 0.0 |
| ask_clarification | 31 | 3.2 |
| avoid_unasked_execution | 4 | 0.0 |
| continue_pending_task | 26 | 3.8 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 10 | 40.0 |
| low | 45 | 26.7 |
| medium | 25 | 12.0 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 10 | 100.0 |
| low | 45 | 20.0 |
| medium | 25 | 48.0 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 5 | 20.0 |
| strong | 33 | 36.4 |
| weak | 42 | 14.3 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 5 | 20.0 |
| strong | 33 | 24.2 |
| weak | 42 | 52.4 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
