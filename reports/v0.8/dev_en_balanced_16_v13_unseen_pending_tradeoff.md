# Clarification Trade-off Analysis

Case results: `results\v0.8-dev-en-balanced-16-v13-unseen-pending\case_results.csv`
Dataset metadata: `benchmark\data\v0.3\dev_en_v3_balanced_16.jsonl`

## Metadata coverage

Dataset cases: **16**
Fully annotated cases: **16** (100.0%)
| metadata_field | present | missing | coverage_rate |
|---|---|---|---|
| ambiguity_level | 16 | 0 | 100.0 |
| expected_action | 16 | 0 | 100.0 |
| notes | 16 | 0 | 100.0 |
| operation_required | 16 | 0 | 100.0 |
| pending_context_strength | 16 | 0 | 100.0 |

## Summary by mode

| mode | cases | metadata_available_cases | action_accuracy | wrong_intent_inference_rate | clarification_rate | unnecessary_clarification_rate | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate | overclarification_on_clear_direct_rate | overclarification_on_strong_pending_context_rate | underclarification_on_high_ambiguity_short_fragment_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 16 | 16 | 43.8 | 37.5 | 25.0 | 18.8 | 12.5 | 31.2 | 6.2 | 25.0 | 40.0 | 100.0 |
| strict | 16 | 16 | 93.8 | 6.2 | 56.2 | 18.8 | 6.2 | 0.0 | 12.5 | 0.0 | 20.0 | 0.0 |

## Metadata-normalized clarification checks

| mode | cases | metadata_available_cases | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate |
|---|---|---|---|---|---|
| baseline | 16 | 16 | 12.5 | 31.2 | 6.2 |
| strict | 16 | 16 | 6.2 | 0.0 | 12.5 |

These checks are alias-aware: a clarification can be valid for `avoid_unasked_execution`, so it is not automatically treated as unnecessary merely because `expected_action != ask_clarification`.

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 43.8 | 93.8 | 50.0 |
| wrong_intent_inference_rate | 37.5 | 6.2 | -31.3 |
| clarification_rate | 25.0 | 56.2 | 31.2 |
| unnecessary_clarification_rate | 18.8 | 18.8 | 0.0 |
| metadata_unnecessary_clarification_rate | 12.5 | 6.2 | -6.3 |
| metadata_needed_clarification_missing_rate | 31.2 | 0.0 | -31.2 |
| grader_metadata_conflict_rate | 6.2 | 12.5 | 6.3 |
| overclarification_on_clear_direct_rate | 25.0 | 0.0 | -25.0 |
| overclarification_on_strong_pending_context_rate | 40.0 | 20.0 | -20.0 |
| underclarification_on_high_ambiguity_short_fragment_rate | 100.0 | 0.0 | -100.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 3 | 3 | 66.7 |
| answer_directly | 2 | 2 | 100.0 |
| ask_clarification | 7 | 7 | 28.6 |
| avoid_unasked_execution | 1 | 1 | 0.0 |
| continue_pending_task | 3 | 3 | 33.3 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 3 | 3 | 100.0 |
| answer_directly | 2 | 2 | 100.0 |
| ask_clarification | 7 | 7 | 100.0 |
| avoid_unasked_execution | 1 | 1 | 100.0 |
| continue_pending_task | 3 | 3 | 66.7 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 3 | 33.3 |
| answer_directly | 2 | 0.0 |
| ask_clarification | 7 | 57.1 |
| avoid_unasked_execution | 1 | 100.0 |
| continue_pending_task | 3 | 0.0 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 3 | 0.0 |
| answer_directly | 2 | 0.0 |
| ask_clarification | 7 | 14.3 |
| avoid_unasked_execution | 1 | 0.0 |
| continue_pending_task | 3 | 0.0 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 3 | 0.0 |
| low | 8 | 25.0 |
| medium | 5 | 40.0 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 3 | 100.0 |
| low | 8 | 12.5 |
| medium | 5 | 100.0 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 0.0 |
| strong | 5 | 40.0 |
| weak | 10 | 20.0 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 0.0 |
| strong | 5 | 20.0 |
| weak | 10 | 80.0 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
