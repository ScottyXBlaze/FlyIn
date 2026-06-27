# FlyIn — AGENTS.md

Single-module MAPF project (42 curriculum). Python 3.13+, `uv` package manager.

## Setup & commands

| Action | Command |
|---|---|
| Install deps | `uv sync` / `make install` |
| Run (no visual) | `make run MAP=<mapfile>` or `uv run main.py <mapfile>` |
| Run (visual) | `make run_visual MAP=<mapfile>` or `uv run main.py <mapfile> --visual` |
| Debug | `make debug MAP=<mapfile>` (pdb) |
| Clean caches | `make clean` (`__pycache__` + `.mypy_cache`) |
| Lint | `make lint` — flake8 + mypy (lenient flags) |
| Strict lint | `make lint-strict` — flake8 + mypy `--strict` |

- `.venv/` is gitignored, `uv.lock` is checked in.
- No test suite exists. Map examples: `test.conf`, `challenger.txt`.

## Architecture (entry → exit)

`main.py` → `Parsers` (parse map file via Pydantic) → `Algorithm.run()` (two-phase per turn: finish connections → move idle drones; uses `ReverseDijkstra` heuristic precomputed from all hubs to end) → optional `StateManager` (pygame rendering with `pygame-ce`, not regular pygame).

## Key conventions

- All Python files carry the 42 header style.
- Uses `pygame-ce` (community edition, package name `pygame` in `pyproject.toml`).
- Pydantic `BaseModel` for data models (`main_model.py`).
- `PYGAME_HIDE_SUPPORT_PROMPT=hide` set early in `main.py`.
- `# noqa: 402` on late imports in `main.py` (lines 69–71).
- Map format: custom text directives (`nb_drones:`, `start_hub:`, `end_hub:`, `hub:`, `connection:`); metadata in square brackets.
