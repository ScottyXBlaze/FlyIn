#!/usr/bin/env python3
"""Validate all test map files against the parser."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main_parsers import Parsers
from pydantic import ValidationError

TEST_DIR = Path(__file__).resolve().parent

def classify(name: str) -> str:
    if name.startswith("invalid"):
        return "invalid"
    if name.startswith("valid"):
        return "valid"
    return "unknown"

results = {"pass": 0, "fail": 0, "skipped": 0}

for fpath in sorted(TEST_DIR.iterdir()):
    if not fpath.name.endswith(".conf") or fpath.name == "run_tests.py":
        continue

    category = classify(fpath.name)
    if category == "unknown":
        results["skipped"] += 1
        print(f"  SKIP  {fpath.name}  (unclassified)")
        continue

    try:
        parser = Parsers(str(fpath))
        parser.read_line()
        if category == "valid":
            results["pass"] += 1
            print(f"  PASS  {fpath.name}")
        else:
            results["fail"] += 1
            print(f"  FAIL  {fpath.name}  (expected error, got success)")
    except ValidationError as e:
        msg = str(e.errors()[0]["msg"]) if e.errors() else str(e)
        if category == "invalid":
            results["pass"] += 1
            print(f"  PASS  {fpath.name}  [{msg}]")
        else:
            results["fail"] += 1
            print(f"  FAIL  {fpath.name}  (expected success, got: {msg})")
    except ValueError as e:
        msg = e.args[0] if e.args else str(e)
        if category == "invalid":
            results["pass"] += 1
            print(f"  PASS  {fpath.name}  [{msg}]")
        else:
            results["fail"] += 1
            print(f"  FAIL  {fpath.name}  (expected success, got: {msg})")

print(f"\n{'='*40}")
print(f"  {results['pass']} passed, {results['fail']} failed, {results['skipped']} skipped")
print(f"{'='*40}")

sys.exit(1 if results["fail"] else 0)
