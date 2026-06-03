UV=uv
DEPENDENCY_FILE=requirements.txt
NAME=FLY_IN

install:
	$(UV) pip install -r $(DEPENDENCY_FILE)

run:
	$(UV) run python3 main.py

debug:
	echo "Debugging"
	$(UV) run pydb main.py

clean:
	@echo "cleanning"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Project cleaned"

lint:
	$(UV) run python3 -m flake8 . --exclude=.venv
	$(UV) run python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	flake8 . --exclude=.venv
	mypy --strict . --exclude=.venv
