# Clarification Trade-off Analysis

Case results: `results\holdout-v2-v8-40\en\case_results.csv`
Dataset metadata: `benchmark\data\holdout_cases_en_v2.jsonl`

## Metadata coverage

Dataset cases: **40**
Fully annotated cases: **0** (0.0%)
| metadata_field | present | missing | coverage_rate |
|---|---|---|---|
| ambiguity_level | 0 | 40 | 0.0 |
| expected_action | 0 | 40 | 0.0 |
| notes | 0 | 40 | 0.0 |
| operation_required | 0 | 40 | 0.0 |
| pending_context_strength | 0 | 40 | 0.0 |

> Metadata warning: this dataset has no v0.3 expected-action metadata, so action-accuracy and metadata-specific breakdowns are partial/diagnostic only.

## Summary by mode

| mode | cases | metadata_available_cases | action_accuracy | wrong_intent_inference_rate | clarification_rate | unnecessary_clarification_rate | overclarification_on_clear_direct_rate | overclarification_on_strong_pending_context_rate | underclarification_on_high_ambiguity_short_fragment_rate |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 40 | 0 | 0.0 | 32.5 | 22.5 | 10.0 | 10.0 | 0.0 | 0.0 |
| strict | 40 | 0 | 0.0 | 22.5 | 37.5 | 10.0 | 20.0 | 0.0 | 0.0 |

## Baseline vs strict delta

| metric | baseline | strict | strict - baseline |
|---|---|---|---|
| action_accuracy | 0.0 | 0.0 | 0.0 |
| wrong_intent_inference_rate | 32.5 | 22.5 | -10.0 |
| clarification_rate | 22.5 | 37.5 | 15.0 |
| unnecessary_clarification_rate | 10.0 | 10.0 | 0.0 |
| overclarification_on_clear_direct_rate | 10.0 | 20.0 | 10.0 |
| overclarification_on_strong_pending_context_rate | 0.0 | 0.0 | 0.0 |
| underclarification_on_high_ambiguity_short_fragment_rate | 0.0 | 0.0 | 0.0 |

## Action accuracy by expected action

### baseline
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| unspecified | 40 | 0 | 0.0 |

### strict
| expected_action | cases | metadata_available_cases | action_accuracy |
|---|---|---|---|
| unspecified | 40 | 0 | 0.0 |

## Wrong intent by expected action

### baseline
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| unspecified | 40 | 32.5 |

### strict
| expected_action | cases | wrong_intent_inference_rate |
|---|---|---|
| unspecified | 40 | 22.5 |

## Clarification by ambiguity level

### baseline
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| unspecified | 40 | 22.5 |

### strict
| ambiguity_level | cases | clarification_rate |
|---|---|---|
| unspecified | 40 | 37.5 |

## Clarification by pending context strength

### baseline
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| unspecified | 40 | 22.5 |

### strict
| pending_context_strength | cases | clarification_rate |
|---|---|---|
| unspecified | 40 | 37.5 |

## Note

This analysis uses existing graded case results and dataset metadata. It does not call any API.
The analyzer checks the clarification trade-off; it does not replace manual audit.
