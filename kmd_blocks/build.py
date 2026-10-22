"""Сборка библиотеки: dist/dxf/<категория>/<ИМЯ>.dxf, dist/KMD_LIB.dxf, catalog/index.csv, превью.

Запуск: python -m kmd_blocks.build
"""

from __future__ import annotations

from pathlib import Path

from .blocks import BlockMeta
from .catalog import write_index
from .hardware import define_bolt_set
from .preview import render_png
from .profiles import IBeam, define_ibeam_section
from .template import new_doc

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def _items():
    """Что входит в библиотеку: (функция, аргументы). Пока — блоки пилота."""
    beam = IBeam.from_gost_57837("20Б1")
    return [
        (define_ibeam_section, (beam,), {}),
        (define_ibeam_section, (beam,), {"web_hole": 18}),
        (define_bolt_set, (16, 30, beam.tw), {}),
    ]


def build() -> list[dict]:
    rows: list[dict] = []
    lib = new_doc()
    for func, args, kwargs in _items():
        meta: BlockMeta = func(lib, *args, **kwargs)
        # отдельный файл: геометрия в пространстве модели (для -INSERT ИМЯ=файл)
        one = new_doc()
        func(one, *args, in_modelspace=True, **kwargs)
        rel = Path("dist/dxf") / meta.category / f"{meta.name}.dxf"
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        one.saveas(ROOT / rel)
        render_png(one, DIST / "previews" / f"{meta.name}.png", dpi=150)
        rows.append(meta.index_row(rel.as_posix()))
    lib.saveas(DIST / "KMD_LIB.dxf")
    write_index(rows, ROOT / "catalog" / "index.csv")
    return rows


if __name__ == "__main__":
    for r in build():
        print(r["name"], "->", r["file"])
