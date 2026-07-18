"""Reduced-window LT1810 full-network run (exploratory, not part of the report).

The published report only characterizes the LT1810 (325 MHz) variant on two
small benches (`bench_moderno_sat.cir`, `bench_chain_moderno.cir`) because the
full 260-op-amp network at the report's window (20 images x 250us = 5ms) needs
sub-ns transient steps throughout and would take days of CPU (see
metodologia.tex). A prior attempt at the full network+window was killed after
~29 min having only reached t=114us of simulated time.

This script reuses analog_mlp.py's netlist builder unchanged, but monkeypatches
its timing constants to a much shorter per-image window (still >5x the 1.9us
critical-path latency measured on bench_chain_moderno.cir) and trims the
vector count, so the *actual* full network can run to completion instead of
only the bench approximation.

    ./claw-spice code build experiments/analog-mlp/analog_mlp_moderno_fast.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analog_mlp as base

N_VECTORS = 6
T_WINDOW_US = 15
T_EDGE_US = 0.3
T_MEAS_US = 11


def build(output_dir: str | Path) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    base.T_WINDOW_US = T_WINDOW_US
    base.T_EDGE_US = T_EDGE_US
    base.T_MEAS_US = T_MEAS_US

    layers, meta = base.load_model()
    vectors = base.load_vectors()
    vectors["vectors"] = vectors["vectors"][:N_VECTORS]

    netlist = base.build_netlist(layers, meta, vectors, "moderno")
    cir_path = output / "analog_mlp_moderno_fast.cir"
    cir_path.write_text(netlist)

    return {
        "cir": cir_path,
        "n_vectors": N_VECTORS,
        "window_us": T_WINDOW_US,
        "total_us": N_VECTORS * T_WINDOW_US,
        "labels": [v["label"] for v in vectors["vectors"]],
    }


if __name__ == "__main__":
    print(build(base.experiment_dir()))
