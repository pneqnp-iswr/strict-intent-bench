# Clarification Trade-off Analysis

Case results: `results\v0.8-dev-en-unseen-balanced-16-v13-unseen-pending\case_results.csv`
Dataset metadata: `benchmark\data\v0.3\dev_en_v3_unseen_balanced_16.jsonl`

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
| baseline | 16 | 16 | 37.5 | 37.5 | 25.0 | 18.8 | 18.8 | 31.2 | 0.0 | 50.0 | 37.5 | 100.0 |
| strict | 16 | 16 | 81.2 | 0.0 | 37.5 | 6.2 | 6.2 | 6.2 | 0.0 | 25.0 | 12.5 | 0.0 |

## Metadata-normalized clarification checks

| mode | cases | metadata_available_cases | metadata_unnecessary_clarification_rate | metadata_needed_clarification_missing_rate | grader_metadata_conflict_rate |
|---|---|---|---|---|---|
| baseline | 16 | 16 | 18.8 | 31.2 | 0.0 |
| strict | 16 | 16 | 6.2 | 6.2 | 0.0 |

These checks are alias-aware: a clarification can be valid for `avoid_unasked_execution`, so it is not automatically treated as unnecessary merely because `expected_action != ask_clarification`.

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 37.5 | 81.2 | 43.7 |
| wrong_intent_inference_rate | 37.5 | 0.0 | -37.5 |
| clarification_rate | 25.0 | 37.5 | 12.5 |
| unnecessary_clarification_rate | 18.8 | 6.2 | -12.6 |
| metadata_unnecessary_clarification_rate | 18.8 | 6.2 | -12.6 |
| metadata_needed_clarification_missing_rate | 31.2 | 6.2 | -25.0 |
| grader_metadata_conflict_rate | 0.0 | 0.0 | 0.0 |
| overclarification_on_clear_direct_rate | 50.0 | 25.0 | -25.0 |
| overclarification_on_strong_pending_context_rate | 37.5 | 12.5 | -25.0 |
| underclarification_on_high_ambiguity_short_fragment_rate | 100.0 | 0.0 | -100.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 1 | 1 | 100.0 |
| answer_directly | 1 | 1 | 100.0 |
| ask_clarification | 6 | 6 | 16.7 |
| avoid_unasked_execution | 1 | 1 | 0.0 |
| continue_pending_task | 7 | 7 | 42.9 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| acknowledge_correction | 1 | 1 | 100.0 |
| answer_directly | 1 | 1 | 100.0 |
| ask_clarification | 6 | 6 | 83.3 |
| avoid_unasked_execution | 1 | 1 | 100.0 |
| continue_pending_task | 7 | 7 | 71.4 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 1 | 0.0 |
| answer_directly | 1 | 0.0 |
| ask_clarification | 6 | 66.7 |
| avoid_unasked_execution | 1 | 100.0 |
| continue_pending_task | 7 | 14.3 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| acknowledge_correction | 1 | 0.0 |
| answer_directly | 1 | 0.0 |
| ask_clarification | 6 | 0.0 |
| avoid_unasked_execution | 1 | 0.0 |
| continue_pending_task | 7 | 0.0 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 2 | 0.0 |
| low | 9 | 33.3 |
| medium | 5 | 20.0 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| high | 2 | 100.0 |
| low | 9 | 11.1 |
| medium | 5 | 60.0 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 0.0 |
| strong | 8 | 37.5 |
| weak | 7 | 14.3 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| none | 1 | 100.0 |
| strong | 8 | 12.5 |
| weak | 7 | 57.1 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
