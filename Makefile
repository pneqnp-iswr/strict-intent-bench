PYTHON ?= python

.PHONY: validate demo-data quality quality-en quality-ru

validate:
	$(PYTHON) tools/validate_dataset.py benchmark/data/v0.3/dev_en_v3.jsonl --require-v03
	$(PYTHON) tools/validate_dataset.py benchmark/data/v0.3/dev_ru_v3.jsonl --require-v03

demo-data:
	$(PYTHON) tools/export_demo_cases.py

quality: quality-en quality-ru

quality-en:
	$(PYTHON) tools/audit_dataset_quality.py benchmark/data/v0.3/dev_en_v3.jsonl --output reports/v0.7/dev_en_v3_quality.md

quality-ru:
	$(PYTHON) tools/audit_dataset_quality.py benchmark/data/v0.3/dev_ru_v3.jsonl --output reports/v0.7/dev_ru_v3_quality.md
