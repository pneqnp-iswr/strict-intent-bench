# strict-intent-bench Report

## 1. Project framing

`strict-intent-bench` is benchmark-first.

The project is not primarily a "Strict Mode repo." It is a benchmark for **wrong intent inference** in conversational assistants, with **Strict / Precision v8** included as one tested intervention.

Wrong intent inference is a failure mode where the assistant answers a plausible but unstated question instead of the task actually justified by the visible conversation.

## 2. Evaluated methods

Two methods are compared:

1. **Baseline / no_prompt**: the model with no added behavior layer.
2. **Strict / Precision v8**: the same model with a strict clarify-first behavior prompt.

This repository treats Strict v8 as one evaluated intervention, not as the benchmark itself.

## 3. Benchmark categories

The published benchmark covers four categories:

| Category | Description |
|---|---|
| `quoted_reply` | The user quotes part of the assistant's previous answer without an explicit task. |
| `short_fragment` | The user sends a short standalone fragment or term. |
| `acknowledgment_or_correction` | The user agrees, confirms, or corrects the assistant. |
| `clear_direct` | The user clearly selects a pending task, format, language, platform, or next step. |

## 4. Main result: holdout-v2, v8

### English mirror track

| Metric | Baseline | Strict v8 |
|---|---:|---:|
| Pass rate | 47.5% | 72.5% |
| Wrong intent inference rate | 32.5% | 22.5% |
| Unnecessary clarification rate | 10.0% | 10.0% |
| Clarification rate | 22.5% | 37.5% |

### Russian source track

| Metric | Baseline | Strict v8 |
|---|---:|---:|
| Pass rate | 35.0% | 77.5% |
| Wrong intent inference rate | 42.5% | 10.0% |
| Unnecessary clarification rate | 15.0% | 12.5% |
| Clarification rate | 25.0% | 45.0% |

## 5. Cross-language interpretation

The benchmark is published in two aligned tracks:

- **Russian source track**: original authored datasets and runs.
- **English mirror track**: translated mirror datasets and runs.

The same overall pattern appears in both tracks:

- Strict / Precision improves pass rate.
- Strict / Precision reduces wrong intent inference.
- The largest gains appear in quoted replies and acknowledgments/corrections.
- `short_fragment` remains the weakest category.

The Russian source track currently shows a larger gain than the English mirror track.

The most defensible explanation is not that the idea only works in Russian, but that:

- the English baseline is already stronger on some categories;
- translated mirror cases reshape some ambiguity;
- the English track is useful for public discussion, but is not a fully independent benchmark from the Russian source track.

## 6. Category summary on holdout-v2, v8

| Category | EN baseline | EN strict | RU baseline | RU strict |
|---|---:|---:|---:|---:|
| `quoted_reply` | 20.0% | 80.0% | 10.0% | 100.0% |
| `short_fragment` | 30.0% | 40.0% | 10.0% | 50.0% |
| `acknowledgment_or_correction` | 60.0% | 90.0% | 60.0% | 90.0% |
| `clear_direct` | 80.0% | 80.0% | 60.0% | 70.0% |

## 7. Remaining weak spot

The weakest category remains:

> `short_fragment`

This is the class of ambiguous standalone fragments with a tempting default interpretation.

Examples:

- `Blue`
- `Throughput`
- `Wednesday`
- `more expensive`
- `2`
- `SSL`

These fragments are short enough to be ambiguous, but semantically tempting enough that the assistant often picks a default interpretation instead of asking what relation or operation the user intends.

## 8. Earlier supporting result

Earlier holdout runs are also preserved:

- English: `results/holdout-v1-v7-40/en/`
- Russian: `results/holdout-v1-v7-40/ru/`

| Language | Baseline pass | Strict pass | Baseline wrong intent | Strict wrong intent |
|---|---:|---:|---:|---:|
| English v7 | 25.0% | 55.0% | 45.0% | 20.0% |
| Russian v7 | 25.0% | 67.5% | 50.0% | 12.5% |

## 9. What the benchmark supports

The strongest narrow claim supported by the published runs is:

**assistant behavior can be made measurably better on wrong-intent-inference cases through an optional strict clarify-first mode, especially for quoted replies, corrections, and context-sensitive follow-ups.**

The benchmark does not support a broad claim that strict prompting is universally better for all conversations.

## 10. Limitations

- small datasets;
- automated grading;
- prompt-layer intervention, not model training;
- exact results may vary across model versions and sampling behavior;
- the English sets are translated mirrors of the Russian source, not independently authored benchmarks;
- cross-language comparisons are informative, but not perfectly apples-to-apples;
- token usage in this prototype is inflated by the explicit behavior prompt and should not be treated as a product-ready cost estimate;
- `short_fragment` remains the weakest category.
