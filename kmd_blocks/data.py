"""Чтение таблиц ГОСТ из data/*.csv."""

from __future__ import annotations

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_table(name: str, key: str) -> dict[str, dict]:
    """Строки таблицы, проиндексированные по колонке `key`. Числа приводятся к float."""
    path = DATA_DIR / name
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    rows = {}
    for row in csv.DictReader(lines, delimiter=";"):
        for k, v in row.items():
            try:
                row[k] = float(v)
            except ValueError:
                pass
        rows[str(row[key]).removesuffix(".0")] = row
    return rows
