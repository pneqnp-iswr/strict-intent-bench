# strict-intent-bench

`strict-intent-bench` is a benchmark-first repository for **wrong intent inference** in conversational AI assistants.

Wrong intent inference is a failure mode where the assistant answers a plausible but unstated question. The response may be fluent and locally reasonable, but it is grounded in the wrong interpretation of the user's intent.

This repository presents:

- a public benchmark for that failure class;
- a reproducible evaluation runner;
- published English and Russian result tracks;
- **Strict / Precision v8** as one tested intervention, not the whole project.

## Repository structure

```text
strict-intent-bench/
├─ benchmark/
│  ├─ data/
│  ├─ prompts/
│  ├─ manual/
│  └─ README.md
├─ baselines/
│  ├─ no_prompt/
│  └─ strict_v8/
├─ results/
├─ README.md
├─ report.md
├─ requirements.txt
├─ run_eval.py
├─ LICENSE
├─ .gitignore
└─ .gitattributes
```

## What is benchmarked

The benchmark covers four conversational categories:

- `quoted_reply`
- `short_fragment`
- `acknowledgment_or_correction`
- `clear_direct`

The main remaining weak spot is `short_fragment`.

## Tested intervention

The current best tested intervention is:

- `baselines/strict_v8/strict.txt`

The baseline comparison is:

- `baselines/no_prompt/baseline.txt`

`baseline.txt` is intentionally empty. It represents the same model with no added behavior layer.

## Main published result

Primary published runs:

- English mirror: `results/holdout-v2-v8-40/en/`
- Russian source track: `results/holdout-v2-v8-40/ru/`

### English holdout-v2, v8

| Metric | Baseline | Strict v8 |
|---|---:|---:|
| Pass rate | 47.5% | 72.5% |
| Wrong intent inference rate | 32.5% | 22.5% |
| Unnecessary clarification rate | 10.0% | 10.0% |
| Clarification rate | 22.5% | 37.5% |

### Russian holdout-v2, v8

| Metric | Baseline | Strict v8 |
|---|---:|---:|
| Pass rate | 35.0% | 77.5% |
| Wrong intent inference rate | 42.5% | 10.0% |
| Unnecessary clarification rate | 15.0% | 12.5% |
| Clarification rate | 25.0% | 45.0% |

## Cross-language comparison

The repository keeps two aligned tracks:

- **Russian source track**: original authored datasets and result runs.
- **English mirror track**: translated mirror datasets and result runs for an English-speaking audience.

The English mirror is useful for communication and cross-language sanity checking, but it is not a fully independent benchmark from the Russian source track.

### v8 comparison on holdout-v2

| Language | Baseline pass | Strict pass | Pass delta | Baseline wrong intent | Strict wrong intent | Wrong-intent delta |
|---|---:|---:|---:|---:|---:|---:|
| English | 47.5% | 72.5% | +25.0 | 32.5% | 22.5% | -10.0 |
| Russian | 35.0% | 77.5% | +42.5 | 42.5% | 10.0% | -32.5 |

### Category breakdown on holdout-v2, v8

| Category | EN baseline | EN strict | RU baseline | RU strict |
|---|---:|---:|---:|---:|
| `quoted_reply` | 20.0% | 80.0% | 10.0% | 100.0% |
| `short_fragment` | 30.0% | 40.0% | 10.0% | 50.0% |
| `acknowledgment_or_correction` | 60.0% | 90.0% | 60.0% | 90.0% |
| `clear_direct` | 80.0% | 80.0% | 60.0% | 70.0% |

## Earlier supporting result

Earlier holdout runs are also preserved:

- English: `results/holdout-v1-v7-40/en/`
- Russian: `results/holdout-v1-v7-40/ru/`

| Language | Baseline pass | Strict pass | Baseline wrong intent | Strict wrong intent |
|---|---:|---:|---:|---:|
| English v7 | 25.0% | 55.0% | 45.0% | 20.0% |
| Russian v7 | 25.0% | 67.5% | 50.0% | 12.5% |

## Interpretation

The strongest benchmark-supported claim is narrow and practical:

**assistant behavior can be made measurably better on wrong-intent-inference cases through an optional strict clarify-first mode, especially for quoted replies, corrections, and context-sensitive follow-ups.**

This repository does **not** support a broad claim that strict prompting is universally better for all conversations.

## Reproducing the evaluation

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main English mirror evaluation:

```bash
python run_eval.py --dataset benchmark/data/holdout_cases_en_v2.jsonl --output-dir results/holdout-en-v2-v8-40
```

Run the Russian source-track evaluation:

```bash
python run_eval.py --dataset benchmark/data/holdout_cases_ru_v2.jsonl --output-dir results/holdout-ru-v2-v8-40
```

Default paths:

- dataset: `benchmark/data/seed_cases.jsonl`
- grader: `benchmark/prompts/grader.txt`
- baseline prompt: `baselines/no_prompt/baseline.txt`
- strict prompt: `baselines/strict_v8/strict.txt`

## Limitations

- small datasets;
- automated grading;
- prompt-layer intervention, not model training;
- exact results may vary across model versions and sampling behavior;
- the English sets are translated mirrors of the Russian source, not independently authored benchmarks;
- cross-language comparisons are informative, but not perfectly apples-to-apples;
- token usage in this prototype is inflated by the explicit behavior prompt and should not be treated as a product-ready cost estimate;
- `short_fragment` remains the weakest category.

## Discussion

OpenAI Community discussion: [Click here](https://community.openai.com/t/wrong-intent-inference-is-measurable-benchmark-strict-precision-mode-proposal/1380779)

## License

MIT
