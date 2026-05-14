PYTHON ?= python

.PHONY: validate demo-data

validate:
	$(PYTHON) tools/validate_dataset.py benchmark/data/v0.3/dev_en_v3.jsonl --require-v03
	$(PYTHON) tools/validate_dataset.py benchmark/data/v0.3/dev_ru_v3.jsonl --require-v03

demo-data:
	$(PYTHON) tools/export_demo_cases.py
