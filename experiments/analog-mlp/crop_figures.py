"""Auto-crop white margins of the schematic PNGs used by the report.

The .asc sheet bounds include generous slack, so the rendered PNGs have
large empty borders that shrink the useful drawing when placed at
\\textwidth in LaTeX. This trims each PNG to its ink bounding box plus a
small pad, in place.

    ./claw-spice code build experiments/analog-mlp/crop_figures.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

PAD = 24
TARGETS = ["neuronio_oculto.png", "neuronio_saida.png"]


def crop(path: Path) -> tuple[int, int]:
    image = mpimg.imread(str(path))
    if image.shape[2] == 4:
        alpha = image[:, :, 3]
        ink = (alpha > 0) & (image[:, :, :3].min(axis=2) < 0.98)
    else:
        ink = image.min(axis=2) < 0.98
    rows = np.flatnonzero(ink.any(axis=1))
    cols = np.flatnonzero(ink.any(axis=0))
    r0, r1 = max(rows[0] - PAD, 0), min(rows[-1] + PAD, image.shape[0])
    c0, c1 = max(cols[0] - PAD, 0), min(cols[-1] + PAD, image.shape[1])
    cropped = image[r0:r1, c0:c1]
    plt.imsave(str(path), cropped)
    return cropped.shape[1], cropped.shape[0]


def build(output_dir: str | Path) -> dict[str, str]:
    images = Path(__file__).resolve().parents[2] / "reports" / "analog-mlp" / "imagens" / "generated"
    result = {}
    for name in TARGETS:
        target = images / name
        if target.exists():
            width, height = crop(target)
            result[name] = f"{width}x{height}"
    return result


if __name__ == "__main__":
    print(build(Path(__file__).parent))
