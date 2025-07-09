#!/bin/bash
set -eu
biome check --write --unsafe asset/script || true
python -m ruff format src tests *.py
python -m ruff check --fix --unsafe-fixes src tests *.py
python -m mypy src tests *.py
