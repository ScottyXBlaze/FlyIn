NAME=FLY_IN

install:
	poetry install

run:
	poetry run python3 main.py

debug:
	echo "Debugging"
	poetry run pydb main.py

clean:
	echo "cleanning"

lint:
	flake8 . --exclude=.venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	poetry run flake8 .
	poetry run mypy --strict .
