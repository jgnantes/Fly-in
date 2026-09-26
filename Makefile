VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(PYTHON) -m pip
REQ := requirements.txt
ARGS ?=

.PHONY: venv install run lint clean debug

venv:
	@test -x $(PYTHON) || python3 -m venv $(VENV)

install: venv
	@$(PIP) install -r $(REQ)

install-quiet: venv
	@$(PIP) install -q -r $(REQ)

run: install-quiet
	@$(PYTHON) main.py $(ARGS)

clean:
	@find . -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) -prune -exec rm -rf {} +

debug: venv
	@$(PYTHON) -m pdb main.py $(ARGS)

lint: install
	@$(VENV)/bin/flake8 .
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs