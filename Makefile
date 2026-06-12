UV := $(shell which uv)
DEPENDENCY_FILE=requirements.txt
NAME=FLY_IN

install:
	@$(UV) sync

run:
	@$(UV) run main.py $(MAP)

run_visual:
	@$(UV) run main.py $(MAP) --visual

debug:
	@echo "Debugging..."
	@.venv/bin/python3 -m ipdb main.py $(MAP)

clean:
	@echo "cleanning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Project cleaned successfully"

lint:
	@echo "Checking code quality (flake8)..."
	@$(UV) run python3 -m flake8 . --exclude=.venv
	@echo "Checking code quality (mypy)..."
	@$(UV) run python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	@echo "Checking code quality (flake8)..."
	@$(UV) run python3 -m flake8 . --exclude=.venv
	@echo "Checking code quality (mypy strict)..."
	@$(UV) run python3 -m mypy --strict . --exclude=.venv

.PHONY: run run_visual install clean lint lint-strict debug
