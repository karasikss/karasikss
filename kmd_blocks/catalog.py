"""Индекс библиотеки catalog/index.csv — единственный файл, по которому Claude ищет блоки."""

from __future__ import annotations

import csv
from pathlib import Path

COLUMNS = ["name", "category", "title_ru", "gost", "size", "file", "layer",
           "insert_point", "scale_mode", "attrs", "params", "lib_ver"]


def write_index(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=";")
        w.writeheader()
        for row in sorted(rows, key=lambda r: r["name"]):
            w.writerow(row)
