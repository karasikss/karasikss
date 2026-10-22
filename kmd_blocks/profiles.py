"""Сечения прокатных профилей. Точка вставки — центр тяжести сечения."""

from __future__ import annotations

from dataclasses import dataclass

from ezdxf.document import Drawing

from .blocks import BlockMeta, byblock, center_line, new_block, thin
from .data import load_table

FILLET_BULGE = -0.41421356237  # вогнутое скругление 90° при обходе против часовой стрелки
GOST_I_57837 = "ГОСТ Р 57837-2017"


@dataclass(frozen=True)
class IBeam:
    profile: str
    h: float
    b: float
    tw: float
    tf: float
    r: float
    mass: float

    @classmethod
    def from_gost_57837(cls, profile: str) -> "IBeam":
        row = load_table("i_beams_57837.csv", "profile")[profile]
        return cls(profile, row["h"], row["b"], row["tw"], row["tf"], row["r"], row["mass_kg_m"])

    @property
    def code(self) -> str:
        return translit(self.profile)

    def regions(self, web_gap: float = 0.0) -> list[list[tuple[float, float, float]]]:
        """Замкнутые контуры сечения (x, y, bulge) против часовой стрелки.

        web_gap > 0 — сечение проходит через отверстие в стенке по оси Y=0:
        стенка разрывается на высоту web_gap, получаются два контура (верх и низ).
        """
        H, B, w, t, r = self.h / 2, self.b / 2, self.tw / 2, self.tf, self.r
        yi = H - t  # внутренняя грань полки
        fb = FILLET_BULGE
        if web_gap <= 0:
            return [[
                (-B, -H, 0), (B, -H, 0), (B, -yi, 0), (w + r, -yi, fb), (w, -yi + r, 0),
                (w, yi - r, fb), (w + r, yi, 0), (B, yi, 0), (B, H, 0), (-B, H, 0),
                (-B, yi, 0), (-w - r, yi, fb), (-w, yi - r, 0), (-w, -yi + r, fb),
                (-w - r, -yi, 0), (-B, -yi, 0),
            ]]
        g = web_gap / 2
        top = [(w, g, 0), (w, yi - r, fb), (w + r, yi, 0), (B, yi, 0), (B, H, 0), (-B, H, 0),
               (-B, yi, 0), (-w - r, yi, fb), (-w, yi - r, 0), (-w, g, 0)]
        bottom = [(-w, -g, 0), (-w, -yi + r, fb), (-w - r, -yi, 0), (-B, -yi, 0), (-B, -H, 0),
                  (B, -H, 0), (B, -yi, 0), (w + r, -yi, fb), (w, -yi + r, 0), (w, -g, 0)]
        return [top, bottom]


def translit(size: str) -> str:
    table = {"Б": "B", "Ш": "SH", "К": "K", "П": "P", "У": "U", "Д": "D", "С": "S", "Э": "E", "Л": "L"}
    return "".join(table.get(ch, ch) for ch in size)


def define_ibeam_section(doc: Drawing, beam: IBeam, web_hole: float = 0.0,
                         in_modelspace: bool = False) -> BlockMeta:
    """Блок сечения двутавра. web_hole — диаметр отверстия в стенке на оси Y=0 (семейство)."""
    name = f"SEC_I_57837_{beam.code}" + (f"_WH{web_hole:g}" if web_hole else "")
    title = f"Двутавр {beam.profile}, сечение" + (f", отв. Ø{web_hole:g} в стенке" if web_hole else "")
    meta = BlockMeta(
        name=name,
        category="SEC",
        title_ru=title,
        gost=GOST_I_57837,
        size=beam.profile,
        layer="К_Контур",
        insert_point="центр тяжести",
        attrs={"GOST": GOST_I_57837, "PROFILE": beam.profile, "MASS_M": f"{beam.mass:g}"},
        params={"h": beam.h, "b": beam.b, "tw": beam.tw, "tf": beam.tf, "r": beam.r},
    )
    if name in doc.blocks and not in_modelspace:
        return meta
    blk = new_block(doc, meta, in_modelspace)
    regions = beam.regions(web_hole)
    hatch = blk.add_hatch(dxfattribs=thin())
    hatch.set_pattern_fill("ANSI31", scale=1.0)
    for pts in regions:
        blk.add_lwpolyline(pts, format="xyb", close=True, dxfattribs=byblock())
        hatch.paths.add_polyline_path(pts, is_closed=True)
    # оси симметрии с выходом 5 мм за контур; при отверстии на оси горизонтальную ось
    # даёт ось болта, двойная линия не нужна
    ext = 5.0
    if not web_hole:
        blk.add_line((-beam.b / 2 - ext, 0), (beam.b / 2 + ext, 0), dxfattribs=center_line())
    blk.add_line((0, -beam.h / 2 - ext), (0, beam.h / 2 + ext), dxfattribs=center_line())
    return meta
