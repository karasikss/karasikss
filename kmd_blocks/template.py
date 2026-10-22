"""Документ DXF с настройками шаблона пользователя (SP_Шаблон_РД.dwt): слои, типы линий, стили."""

from __future__ import annotations

import ezdxf
from ezdxf.document import Drawing

TEXT_STYLE = "ISOCPEUR"

# Типы линий ISO из acadiso.lin (единицы — мм).
LINETYPES = {
    "ACAD_ISO02W100": ("ISO dash __ __ __", [15.0, 12.0, -3.0]),
    "ACAD_ISO04W100": ("ISO long-dash dot ____ . ____ .", [30.0, 24.0, -3.0, 0.0, -3.0]),
    "ACAD_ISO05W100": ("ISO long-dash double-dot ____ .. ____", [33.0, 24.0, -3.0, 0.0, -3.0, 0.0, -3.0]),
}

# Слои шаблона: имя -> (вес линии в сотых мм, тип линии, цвет ACI, печать)
LAYERS = {
    "К_Контур": (50, "Continuous", 7, True),
    "К_Контур_тонк": (18, "Continuous", 7, True),
    "К_Невидимый": (25, "ACAD_ISO02W100", 7, True),
    "К_Схема": (50, "Continuous", 7, True),
    "К_Примыкающие": (18, "ACAD_ISO05W100", 8, True),
    "О_Оси": (18, "ACAD_ISO04W100", 1, True),
    "О_Центровые": (18, "ACAD_ISO04W100", 1, True),
    "Р_Размеры": (18, "Continuous", 3, True),
    "Р_Отметки": (18, "Continuous", 3, True),
    "А_Марки": (18, "Continuous", 2, True),
    "А_Текст": (18, "Continuous", 2, True),
    "А_Разрезы": (70, "Continuous", 7, True),
    "А_Узлы": (18, "Continuous", 2, True),
    "А_Сварка": (18, "Continuous", 6, True),
    "А_Крепёж": (25, "Continuous", 4, True),
    "Ш_Штриховка": (13, "Continuous", 8, True),
    "Л_Обрыв": (18, "Continuous", 7, True),
    "Л_Рамка": (50, "Continuous", 7, True),
    "Л_ВЭкраны": (18, "Continuous", 8, False),
    "Z_Вспомог": (18, "Continuous", 9, False),
}


def new_doc(scale: int = 1) -> Drawing:
    """Новый документ в мм с слоями, ISOCPEUR и размерным стилем для масштаба 1:scale."""
    doc = ezdxf.new("R2018", setup=False)
    doc.units = 4  # мм
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LWDISPLAY"] = 1
    doc.header["$PSLTSCALE"] = 1
    doc.header["$LTSCALE"] = 1
    for name, (desc, pattern) in LINETYPES.items():
        doc.linetypes.add(name, pattern=pattern, description=desc)
    for name, (lw, lt, color, plot) in LAYERS.items():
        layer = doc.layers.add(name, color=color, linetype=lt, lineweight=lw)
        layer.dxf.plot = 1 if plot else 0
    doc.styles.add(TEXT_STYLE, font="isocpeur.ttf")
    add_dimstyle(doc, scale)
    return doc


def dimstyle_name(scale: int) -> str:
    return f"KMD_1-{scale}"


def add_dimstyle(doc: Drawing, scale: int) -> None:
    """Размерный стиль СПДС: засечки, текст 3.5 мм ISOCPEUR, масштаб через DIMSCALE."""
    name = dimstyle_name(scale)
    if name in doc.dimstyles:
        return
    doc.dimstyles.add(
        name,
        dxfattribs={
            "dimtxsty": TEXT_STYLE,
            "dimtxt": 3.5,
            "dimblk": "ARCHTICK",
            "dimasz": 2.5,
            "dimexe": 2.0,
            "dimexo": 0.0,
            "dimdle": 2.0,
            "dimgap": 1.0,
            "dimtad": 1,
            "dimdec": 1,
            "dimdsep": ord(","),
            "dimtzin": 8,
            "dimscale": float(scale),
            "dimclrd": 256,
            "dimclre": 256,
            "dimclrt": 256,
        },
    )
