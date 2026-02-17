.PHONY: install test lint run watch config clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

lint:
	python -m flake8 deepstock/ --max-line-length=120
	python -m mypy deepstock/ --ignore-missing-imports

run:
	deepstock scan

watch:
	deepstock watch

config:
	deepstock config

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf *.egg-info dist build
