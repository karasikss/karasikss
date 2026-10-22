"""Общие правила создания блоков (docs/STANDARD.md, разделы 3–5)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ezdxf.document import Drawing
from ezdxf.layouts import BaseLayout

from . import LIB_VER
from .template import TEXT_STYLE

BYBLOCK = 0
THIN = 18  # вес тонких линий внутри блока (оси, штриховка, резьба), сотые мм
CENTER_LT = "ACAD_ISO04W100"


@dataclass
class BlockMeta:
    """Метаданные блока: попадают в описание, скрытые атрибуты и индекс."""

    name: str
    category: str
    title_ru: str
    gost: str = ""
    size: str = ""
    layer: str = "К_Контур"
    insert_point: str = ""
    scale_mode: str = "model"  # model — натура 1:1; sheet — умножать на знаменатель масштаба
    attrs: dict[str, str] = field(default_factory=dict)  # скрытые атрибуты: тег -> значение
    params: dict[str, float] = field(default_factory=dict)

    def index_row(self, file: str) -> dict[str, str]:
        return {
            "name": self.name,
            "category": self.category,
            "title_ru": self.title_ru,
            "gost": self.gost,
            "size": self.size,
            "file": file,
            "layer": self.layer,
            "insert_point": self.insert_point,
            "scale_mode": self.scale_mode,
            "attrs": ",".join(self.attrs),
            "params": ",".join(f"{k}={_num(v)}" for k, v in self.params.items()),
            "lib_ver": LIB_VER,
        }


def _num(v: float) -> str:
    return f"{v:g}"


def new_block(doc: Drawing, meta: BlockMeta, in_modelspace: bool = False) -> BaseLayout:
    """Создаёт определение блока с описанием и скрытыми атрибутами метаданных.

    in_modelspace=True — геометрия кладётся в пространство модели: так устроен файл
    «один блок = один файл», который AutoCAD подгружает командой -INSERT ИМЯ=файл.
    """
    if in_modelspace:
        blk = doc.modelspace()
        doc.header["$INSBASE"] = (0, 0, 0)
    else:
        blk = doc.blocks.new(meta.name, base_point=(0, 0))
        blk.block.dxf.description = f"{meta.title_ru} {meta.gost}".strip()  # видно в палитре «Блоки»
    attrs = {"LIB_ID": meta.name, "LIB_VER": LIB_VER, **meta.attrs}
    for i, (tag, value) in enumerate(attrs.items()):
        ad = blk.add_attdef(
            tag,
            insert=(0, -5.0 * (i + 1)),
            text=str(value),
            dxfattribs={"height": 2.5, "style": TEXT_STYLE, "layer": "0", "color": BYBLOCK},
        )
        ad.dxf.flags = 1 | 8  # невидимый + предустановленный (AutoCAD не спрашивает значение)
        ad.dxf.prompt = tag
    return blk


def byblock(extra: dict | None = None) -> dict:
    """Атрибуты геометрии внутри блока: слой 0, цвет/тип/вес ПоБлоку."""
    attrs = {"layer": "0", "color": BYBLOCK, "linetype": "ByBlock", "lineweight": -2}
    if extra:
        attrs.update(extra)
    return attrs


def thin() -> dict:
    return byblock({"lineweight": THIN})


def center_line() -> dict:
    return byblock({"lineweight": THIN, "linetype": CENTER_LT})
