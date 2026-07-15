"""Time the numpy forward pass of the trained analog MLP on the host Mac.

Runs NATIVELY on the host (needs only numpy, no project dependencies) so the
comparison against the 741 circuit latency is fair — the Docker container
runs under emulation and would understate the Mac.

    python3 experiments/analog-mlp/bench_host_inference.py

Writes reports/analog-mlp/gerado/valores_host.tex with LaTeX macros.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

VSAT = 4.8
REPEATS = 2000
BATCH = 10_000


def main() -> None:
    exp = Path(__file__).resolve().parent
    payload = json.loads((exp / "analog_mlp_weights.json").read_text())
    layers = [
        (np.asarray(item["W"], dtype=np.float32), np.asarray(item["b"], dtype=np.float32))
        for item in payload["layers"]
    ]
    vectors = json.loads((exp / "spice_test_vectors.json").read_text())["vectors"]
    x_one = np.asarray([vectors[3]["pixels"]], dtype=np.float32)
    rng = np.random.default_rng(0)
    x_batch = rng.random((BATCH, 64), dtype=np.float32)

    def forward(x: np.ndarray) -> np.ndarray:
        activation = x
        for index, (weights, bias) in enumerate(layers):
            z = activation @ weights + bias
            if index == len(layers) - 1:
                activation = np.clip(z, -VSAT, VSAT)
            else:
                activation = np.clip(z, 0.0, VSAT)
        return activation

    forward(x_one)  # warm-up
    t0 = time.perf_counter()
    for _ in range(REPEATS):
        forward(x_one)
    t_single_us = (time.perf_counter() - t0) / REPEATS * 1e6

    forward(x_batch)  # warm-up
    t0 = time.perf_counter()
    forward(x_batch)
    t_batch_us = (time.perf_counter() - t0) / BATCH * 1e6

    ops = sum(2 * w.size for w, _ in layers)
    print(f"single-image forward: {t_single_us:.1f} us")
    print(f"amortized in a {BATCH}-image batch: {t_batch_us:.3f} us/image")
    print(f"multiply-accumulate ops per image: {ops // 2}")

    # fps calculado sobre os valores ja arredondados, para a tabela e o
    # grafico do relatorio contarem a mesma historia
    t_single_r = round(t_single_us)
    t_batch_r = round(t_batch_us, 2)
    single = f"{t_single_r:.0f}"
    batch = f"{t_batch_r:.2f}".replace(".", ",")
    fps_single = f"{1e6 / t_single_r:,.0f}".replace(",", " ")
    fps_batch = f"{1e6 / t_batch_r:,.0f}".replace(",", " ")
    out = exp.parents[1] / "reports" / "analog-mlp" / "gerado"
    out.mkdir(parents=True, exist_ok=True)
    (out / "valores_host.tex").write_text(
        "% Gerado por bench_host_inference.py (host) - nao editar a mao.\n"
        f"\\newcommand{{\\vMacUmaImagem}}{{{single}}}\n"
        f"\\newcommand{{\\vMacLote}}{{{batch}}}\n"
        f"\\newcommand{{\\vMacFpsUma}}{{{fps_single}}}\n"
        f"\\newcommand{{\\vMacFpsLote}}{{{fps_batch}}}\n"
    )


if __name__ == "__main__":
    main()
