"""Compensated LT1810 full-network run (exploratory, not part of the report).

Post-processes analog_mlp.py's uncompensated "moderno" netlist to add the two
fixes bench_chain_moderno.cir validates but the generator never applies to the
full 260-op-amp network:

  - a 2 pF capacitor across every feedback resistor (RF*/RIF*) on each
    summing/inverting stage, closing the loop below the pole the LT1810's
    input capacitance forms with the 100k feedback resistor;
  - a bias-current balance resistor on every summing/inverting stage's
    non-inverting input, sized to the *exact* Thevenin resistance seen at
    that stage's summing node (1 / sum(1/R) over every resistor wired to
    that node: RF, every weight resistor, and the bias resistor if present)
    instead of the bench's single fixed 49.9k, which only matches its own
    unity-gain stages.

Comparators are left open-loop / uncompensated, matching the report (they
have no feedback network, so there's no equivalent Thevenin resistance to
balance against).

    ./claw-spice code build experiments/analog-mlp/analog_mlp_moderno_comp.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analog_mlp as base

N_VECTORS = 6
T_WINDOW_US = 15
T_EDGE_US = 0.3
T_MEAS_US = 11
CF = "2p"


def parse_ohms(value: str) -> float:
    if value.endswith("Meg"):
        return float(value[:-3]) * 1e6
    if value.endswith("k"):
        return float(value[:-1]) * 1e3
    return float(value)


def compensate(netlist: str) -> str:
    lines = netlist.splitlines()
    conductance: dict[str, float] = defaultdict(float)
    for line in lines:
        tokens = line.split()
        if len(tokens) == 4 and tokens[0].startswith("R"):
            _name, n1, n2, val = tokens
            g = 1.0 / parse_ohms(val)
            conductance[n1] += g
            conductance[n2] += g

    out_lines = []
    for line in lines:
        tokens = line.split()
        if len(tokens) == 7 and tokens[0][:2] in ("XS", "XI") and tokens[1] == "0":
            name, _zero, sum_node, vcc, vee_node, out_node, subckt = tokens
            bal_node = f"b{name[1:]}"
            r_bal = 1.0 / conductance[sum_node]
            out_lines.append(f"{name} {bal_node} {sum_node} {vcc} {vee_node} {out_node} {subckt}")
            out_lines.append(f"RBAL{name[1:]} {bal_node} 0 {base.fmt_r(r_bal)}")
            continue
        out_lines.append(line)
        if len(tokens) == 4 and (tokens[0].startswith("RF") or tokens[0].startswith("RIF")):
            name, n1, n2, _val = tokens
            out_lines.append(f"CF{name} {n1} {n2} {CF}")
    return "\n".join(out_lines) + "\n"


def build(output_dir: str | Path) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    base.T_WINDOW_US = T_WINDOW_US
    base.T_EDGE_US = T_EDGE_US
    base.T_MEAS_US = T_MEAS_US

    layers, meta = base.load_model()
    vectors = base.load_vectors()
    vectors["vectors"] = vectors["vectors"][:N_VECTORS]

    raw_netlist = base.build_netlist(layers, meta, vectors, "moderno")
    compensated = compensate(raw_netlist)

    cir_path = output / "analog_mlp_moderno_comp.cir"
    cir_path.write_text(compensated)

    return {
        "cir": cir_path,
        "n_vectors": N_VECTORS,
        "window_us": T_WINDOW_US,
        "labels": [v["label"] for v in vectors["vectors"]],
    }


if __name__ == "__main__":
    print(build(base.experiment_dir()))
