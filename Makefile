.PHONY: install install-pre-commit test style check

install:
	pip install -e .

install-pre-commit:
	pre-commit install

test:
	pip install pytest
	PYTHONPATH=. pytest

style:
	pre-commit run --all-files

check: style test