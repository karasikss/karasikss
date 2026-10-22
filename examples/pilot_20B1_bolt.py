"""Пилот: сечение двутавра 20Б1 с болтом М16 через стенку посередине высоты. М 1:2.

Запуск: python -m examples.pilot_20B1_bolt  →  dist/examples/pilot_20B1_bolt.dxf (+ .png)
"""

from __future__ import annotations

from pathlib import Path

from kmd_blocks.hardware import define_bolt_set
from kmd_blocks.preview import render_png
from kmd_blocks.profiles import IBeam, define_ibeam_section
from kmd_blocks.template import TEXT_STYLE, dimstyle_name, new_doc

SCALE = 2  # М 1:2
TH = 3.5 * SCALE  # высота текста 3.5 мм на листе
OUT = Path(__file__).resolve().parent.parent / "dist" / "examples"


def leader(msp, start, knee, lines: list[str], shelf_right: bool = True) -> None:
    """Выноска с полкой: точка на объекте, наклонная линия, полка, текст над полкой."""
    width = max(len(s) for s in lines) * TH * 0.62
    end = (knee[0] + width, knee[1]) if shelf_right else (knee[0] - width, knee[1])
    msp.add_lwpolyline([start, knee, end], dxfattribs={"layer": "А_Текст"})
    dot = msp.add_hatch(dxfattribs={"layer": "А_Текст"})
    dot.paths.add_edge_path().add_arc(start, 0.75 * SCALE, 0, 360)
    x0 = min(knee[0], end[0])
    mt = msp.add_mtext("\\P".join(lines), dxfattribs={"layer": "А_Текст", "style": TEXT_STYLE, "char_height": TH})
    mt.set_location((x0 + TH * 0.3, knee[1] + TH * 0.4), attachment_point=7)  # низ-лево
    mt.dxf.line_spacing_factor = 1.0


def main() -> Path:
    doc = new_doc(scale=SCALE)
    msp = doc.modelspace()
    beam = IBeam.from_gost_57837("20Б1")
    hole = 18.0
    sec = define_ibeam_section(doc, beam, web_hole=hole)
    bset = define_bolt_set(doc, 16, 30, grip=beam.tw)

    msp.add_blockref(sec.name, (0, 0), dxfattribs={"layer": sec.layer}).add_auto_attribs({})
    msp.add_blockref(bset.name, (0, 0), dxfattribs={"layer": bset.layer}).add_auto_attribs({})

    ds = dimstyle_name(SCALE)
    H, B = beam.h / 2, beam.b / 2
    dims = [
        dict(base=(0, H + 16), p1=(-B, H), p2=(B, H)),                       # b
        dict(base=(-B - 32, 0), p1=(-B, -H), p2=(-B, H), angle=90),          # h
        dict(base=(-B - 16, 0), p1=(-B, -H), p2=(-24, 0), angle=90),         # до оси болта
        dict(base=(-B - 16, 0), p1=(-24, 0), p2=(-B, H), angle=90),
        dict(base=(B + 12, 0), p1=(B, H), p2=(B, H - beam.tf), angle=90,    # tf
             text_at=(B + 24, H + 16)),
        dict(base=(0, 55), p1=(-beam.tw / 2, 55), p2=(beam.tw / 2, 55),     # tw
             text_at=(16, 70)),
    ]
    for d in dims:
        text_at = d.pop("text_at", None)
        dim = msp.add_linear_dim(dimstyle=ds, dxfattribs={"layer": "Р_Размеры"}, **d)
        if text_at:  # малый размер: текст на полке с выноской (DIMTMOVE=1)
            dim.set_location(text_at, leader=True)
        dim.render()

    leader(msp, (12, -10), (62, -75), [
        "Болт М16-6gx30.58 ГОСТ 7798-70",
        "Гайка М16-6H.5 ГОСТ 5915-70",
        "Шайба 16 ГОСТ 11371-78 - 2 шт.",
        f"Отв. Ø{hole:g} в стенке",
    ])
    leader(msp, (-30, H - 3), (-62, 150), [f"{beam.profile} ГОСТ Р 57837-2017"], shelf_right=False)

    title = msp.add_text("1-1", dxfattribs={"layer": "А_Текст", "style": TEXT_STYLE, "height": 5 * SCALE})
    title.set_placement((0, -H - 35), align=ezdxf_align("MIDDLE_CENTER"))
    note = msp.add_text("М 1:2", dxfattribs={"layer": "А_Текст", "style": TEXT_STYLE, "height": TH})
    note.set_placement((0, -H - 50), align=ezdxf_align("MIDDLE_CENTER"))

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "pilot_20B1_bolt.dxf"
    doc.saveas(path)
    render_png(doc, path.with_suffix(".png"), dpi=250, lineweight_scaling=1.0)
    return path


def ezdxf_align(name: str):
    from ezdxf.enums import TextEntityAlignment

    return TextEntityAlignment[name]


if __name__ == "__main__":
    print(main())
