# Clarification Trade-off Analysis

Case results: `results\v0.8-smoke-en-4\case_results.csv`
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

| mode | cases | metadata_available_cases | action_accuracy | wrong_intent_inference_rate | clarification_rate | unnecessary_clarification_rate | overclarification_on_clear_direct_rate | overclarification_on_strong_pending_context_rate | underclarification_on_high_ambiguity_short_fragment_rate |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 4 | 4 | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| strict | 4 | 4 | 100.0 | 75.0 | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 |

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 0.0 | 100.0 | 100.0 |
| wrong_intent_inference_rate | 100.0 | 75.0 | -25.0 |
| clarification_rate | 0.0 | 100.0 | 100.0 |
| unnecessary_clarification_rate | 0.0 | 100.0 | 100.0 |
| overclarification_on_clear_direct_rate | 0.0 | 0.0 | 0.0 |
| overclarification_on_strong_pending_context_rate | 0.0 | 0.0 | 0.0 |
| underclarification_on_high_ambiguity_short_fragment_rate | 0.0 | 0.0 | 0.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| ask_clarification | 3 | 3 | 0.0 |
| avoid_unasked_execution | 1 | 1 | 0.0 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| ask_clarification | 3 | 3 | 100.0 |
| avoid_unasked_execution | 1 | 1 | 100.0 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| ask_clarification | 3 | 100.0 |
| avoid_unasked_execution | 1 | 100.0 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| ask_clarification | 3 | 66.7 |
| avoid_unasked_execution | 1 | 100.0 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| medium | 4 | 0.0 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| medium | 4 | 100.0 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| weak | 4 | 0.0 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| weak | 4 | 100.0 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
