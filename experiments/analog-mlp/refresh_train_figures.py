"""Regenerate the trainer's report figures from the saved weights, without
retraining. Used when only figure text changes.

    ./claw-spice code build experiments/analog-mlp/refresh_train_figures.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import train_analog_mlp as t


def build(output_dir: str | Path) -> dict[str, str]:
    exp = Path(__file__).resolve().parent
    payload = json.loads((exp / "analog_mlp_weights.json").read_text())
    layers = [
        {"W": np.asarray(item["W"], dtype=np.float32), "b": np.asarray(item["b"], dtype=np.float32)}
        for item in payload["layers"]
    ]
    data = exp / "data"
    test_images = t.read_idx_images(data / t.MNIST_FILES["test_images"])
    test_labels = t.read_idx_labels(data / t.MNIST_FILES["test_labels"])
    x_test = t.downsample_8x8(test_images)
    images = t.report_images_dir()
    t.fig_confusion(layers, x_test, test_labels, images / "matriz_confusao.png")
    t.fig_digit_samples(test_images, x_test, test_labels, images / "amostras_digitos.png")
    return {"figures": str(images)}


if __name__ == "__main__":
    print(build(Path(__file__).parent))
