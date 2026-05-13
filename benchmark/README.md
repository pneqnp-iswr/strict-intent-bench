# Benchmark

This repository is benchmark-first.

The `benchmark/` directory contains the assets used to measure wrong intent inference in conversational assistants:

- `data/` - seed cases and public holdout datasets in Russian and English
- `prompts/grader.txt` - automated grading prompt
- `manual/` - blind manual review protocol and scoring template

The published benchmark categories are:

- `quoted_reply`
- `short_fragment`
- `acknowledgment_or_correction`
- `clear_direct`

The weakest remaining category across the published runs is `short_fragment`.
