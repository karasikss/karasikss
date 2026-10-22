"""Метизы. Болтокомплект — семейство: строится под толщину пакета (grip).

Болт по ГОСТ 2.305 в продольном разрезе показывается нерассечённым.
Шестигранник на виде сбоку показан по диагонали (видны три грани).
"""

from __future__ import annotations

import math

from ezdxf.document import Drawing

from .blocks import BlockMeta, byblock, center_line, new_block, thin
from .data import load_table

GOST_BOLT = "ГОСТ 7798-70"
GOST_NUT = "ГОСТ 5915-70"
GOST_WASHER = "ГОСТ 11371-78"


def _hex_side(blk, x0: float, x1: float, s: float) -> None:
    """Шестигранник на виде сбоку от x0 до x1: высота по диагонали e, рёбра граней на ±e/4."""
    e = s / math.cos(math.radians(30))
    blk.add_lwpolyline([(x0, -e / 2), (x1, -e / 2), (x1, e / 2), (x0, e / 2)], close=True, dxfattribs=byblock())
    for y in (-e / 4, e / 4):
        blk.add_line((x0, y), (x1, y), dxfattribs=byblock())


def define_bolt_set(doc: Drawing, d: int, length: float, grip: float, strength: str = "5.8",
                    in_modelspace: bool = False) -> BlockMeta:
    """Болтокомплект: болт + 2 шайбы + гайка, вид сбоку, ось по X, головка слева.

    Точка вставки — середина пакета на оси болта. grip — толщина пакета, мм.
    """
    bolt = load_table("bolts_7798.csv", "d")[str(d)]
    nut = load_table("nuts_5915.csv", "d")[str(d)]
    wash = load_table("washers_11371.csv", "d")[str(d)]
    sw, m = wash["s"], nut["m"]

    x_head = -grip / 2 - sw  # опорная грань головки
    x_end = x_head + length
    x_nut1 = grip / 2 + sw + m
    if x_end < x_nut1 + bolt["p"]:
        raise ValueError(f"Болт M{d}x{length:g} короток для пакета {grip:g} мм: нужно не меньше "
                         f"{x_nut1 + 2 * bolt['p'] - x_head:g} мм")

    bolt_txt = f"М{d}-6gx{length:g}.{strength.replace('.', '')} {GOST_BOLT}"
    meta = BlockMeta(
        name=f"HW_SET_7798_M{d}x{length:g}_G{grip:g}",
        category="HW",
        title_ru=f"Болтокомплект М{d}x{length:g}, пакет {grip:g} мм, вид сбоку",
        gost=GOST_BOLT,
        size=f"M{d}x{length:g}",
        layer="К_Контур",  # крепёж на сборочных видах — основной линией
        insert_point="середина пакета на оси болта",
        attrs={
            "BOLT": f"Болт {bolt_txt}",
            "NUT": f"Гайка М{d}-6H.5 {GOST_NUT}",
            "WASHER": f"Шайба {d} {GOST_WASHER}",
            "QTY_WASHER": "2",
        },
        params={"d": d, "L": length, "grip": grip},
    )
    if meta.name in doc.blocks and not in_modelspace:
        return meta
    blk = new_block(doc, meta, in_modelspace)

    R, r1 = d / 2, bolt["d1"] / 2
    c = R - r1  # фаска на конце болта
    # головка, шайбы, гайка
    _hex_side(blk, x_head - bolt["k"], x_head, bolt["s"])
    for x0 in (x_head, grip / 2):
        blk.add_lwpolyline([(x0, -wash["D"] / 2), (x0 + sw, -wash["D"] / 2),
                            (x0 + sw, wash["D"] / 2), (x0, wash["D"] / 2)], close=True, dxfattribs=byblock())
    _hex_side(blk, grip / 2 + sw, x_nut1, nut["s"])
    # стержень в пакете (виден в разрезе через отверстие)
    for y in (-R, R):
        blk.add_line((-grip / 2, y), (grip / 2, y), dxfattribs=byblock())
    # выступающий конец с фаской
    blk.add_lwpolyline([(x_nut1, R), (x_end - c, R), (x_end, r1), (x_end, -r1), (x_end - c, -R), (x_nut1, -R)],
                       dxfattribs=byblock())
    # резьба — тонкие линии по внутреннему диаметру
    for y in (-r1, r1):
        blk.add_line((-grip / 2, y), (grip / 2, y), dxfattribs=thin())
        blk.add_line((x_nut1, y), (x_end, y), dxfattribs=thin())
    # ось
    blk.add_line((x_head - bolt["k"] - 3, 0), (x_end + 3, 0), dxfattribs=center_line())
    return meta
