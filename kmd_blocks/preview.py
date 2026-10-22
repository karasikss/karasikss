"""PNG-превью чертежей и блоков (ezdxf + matplotlib)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy  # noqa: E402
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402
from ezdxf.document import Drawing  # noqa: E402


def render_png(doc: Drawing, path: Path, dpi: int = 200, lineweight_scaling: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE,
        color_policy=ColorPolicy.BLACK,
        lineweight_policy=LineweightPolicy.ABSOLUTE,
        lineweight_scaling=lineweight_scaling,
    )
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=True)
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
