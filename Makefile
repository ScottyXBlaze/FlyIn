UV=uv
DEPENDENCY_FILE=requirements.txt
NAME=FLY_IN

install:
	@$(UV) sync

run:
	@$(UV) run main.py $(MAP)

debug:
	@echo "Debugging..."
	$(UV) run pydb main.py

clean:
	@echo "cleanning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Project cleaned successfully"

fclean: clean
	@echo "Removing the virtual environment file..."
	@rm -rf .venv

lint:
	@echo "Checking code quality..."
	@$(UV) run python3 -m flake8 . --exclude=.venv
	@$(UV) run python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	@echo "Checking code quality (strict mode)..."
	@$(UV) run python3 -m flake8 . --exclude=.venv
	@$(UV) run python3 -m mypy --strict . --exclude=.venv

re: fclean install
