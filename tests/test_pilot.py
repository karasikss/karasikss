import csv
from pathlib import Path

import ezdxf
import pytest
from ezdxf import bbox

from kmd_blocks.build import ROOT, build
from kmd_blocks.hardware import define_bolt_set
from kmd_blocks.profiles import IBeam, define_ibeam_section
from kmd_blocks.template import new_doc


@pytest.fixture(scope="module")
def rows():
    return build()


def test_ibeam_section_extents_match_gost():
    beam = IBeam.from_gost_57837("20Б1")
    doc = new_doc()
    meta = define_ibeam_section(doc, beam)
    outline = [e for e in doc.blocks[meta.name] if e.dxftype() == "LWPOLYLINE"]
    ext = bbox.extents(outline)
    assert ext.size.x == pytest.approx(beam.b, abs=0.01)
    assert ext.size.y == pytest.approx(beam.h, abs=0.01)
    assert ext.center.x == pytest.approx(0, abs=0.01) and ext.center.y == pytest.approx(0, abs=0.01)


def test_web_hole_splits_section():
    beam = IBeam.from_gost_57837("20Б1")
    top, bottom = beam.regions(web_gap=18)
    assert min(p[1] for p in top) == pytest.approx(9)
    assert max(p[1] for p in bottom) == pytest.approx(-9)


def test_short_bolt_refused():
    with pytest.raises(ValueError):
        define_bolt_set(new_doc(), 16, 20, grip=20)


def test_index_points_to_files_and_attrs(rows):
    index = list(csv.DictReader((ROOT / "catalog/index.csv").open(encoding="utf-8"), delimiter=";"))
    assert {r["name"] for r in index} == {r["name"] for r in rows}
    for r in index:
        doc = ezdxf.readfile(ROOT / r["file"])
        auditor = doc.audit()
        assert not auditor.has_errors, r["name"]
        tags = {a.dxf.tag for a in doc.modelspace().query("ATTDEF")}
        assert {"LIB_ID", "LIB_VER"} <= tags
        assert set(filter(None, r["attrs"].split(","))) <= tags
        assert (ROOT / "dist/previews" / f"{r['name']}.png").exists()


def test_library_file_has_all_blocks(rows):
    lib = ezdxf.readfile(ROOT / "dist/KMD_LIB.dxf")
    assert not lib.audit().has_errors
    for r in rows:
        assert r["name"] in lib.blocks
