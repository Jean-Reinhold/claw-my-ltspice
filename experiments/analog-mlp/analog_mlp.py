"""Generate the analog MLP op-amp network from trained weights.

Reads ``analog_mlp_weights.json`` (produced by ``train_analog_mlp.py``) and
emits:

- ``analog_mlp.cir`` — the full 5-stage op-amp network netlist. Every weight
  ``w`` is one resistor ``Ri = RF/|w|`` (E96 value by construction) into an
  inverting summing amplifier. Positive weights take the negated rail of the
  previous activation, negative weights the direct rail, so the inverting
  summer realizes ``z = sum(w*a) + b`` with positive resistors only.
- Hidden neurons are SINGLE-SUPPLY summers (VCC=5 V, VEE=-0.2 V): the op-amp
  saturates at 0 V and 4.8 V, so the amplifier itself is the bounded-ReLU
  activation. Each hidden neuron also has a unity-gain inverter that
  publishes the negated rail for the next layer.
- The 10 output summers run on dual rails (linear logits), and one open-loop
  comparator per digit fires when its logit crosses the shared VTH rail:
  one op-amp output per digit, individually activated.
- ``neuronio_oculto.asc`` / ``neuronio_saida.asc`` — readable schematic
  details of one real hidden neuron and one real output chain, with the
  trained E96 resistor values.
- ``rede_topologia.png|svg`` — full network graph with weight-colored edges.

Run inside Docker:

    ./claw-spice code build experiments/analog-mlp/analog_mlp.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mpl-"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from claw_spice.ir import Circuit

RF = 100_000.0

# Variants: the ideal repo macromodel and the vendor LM741 Boyle macromodel.
# The LM741 is not rail-to-rail, so its supplies are calibrated (see
# bench_741_sat.cir) to place the real saturation levels at ~[0, 4.8] V for
# the hidden neurons, and at ~[-4.8, +4.8] V for the output summers.
VARIANTS = {
    "ideal": {
        "subckt": "CLAW_IDEAL_OPAMP",
        "include_line": ".include claw_opamps.lib",
        "vcc": 5.0,
        "vee": -5.0,
        "veer": -0.2,
        "options": [],
        "save_hidden": True,
        "suffix": "",
    },
    # Rails calibrated with bench_741_sat.cir: the LM741 macromodel clips
    # 0.99 V below V+ and 0.97 V above V-, so 5.8/-0.97 puts the hidden
    # saturation at [0.00, 4.81] V and +-5.8 gives the output summers
    # +-4.83 V of swing.
    # 260 Boyle macromodels ring numerically under trapezoidal integration
    # (timestep collapses to sub-ns at t=0); Gear damping plus a small node
    # shunt and looser tolerances keep the transient moving.
    "741": {
        "subckt": "LM741",
        "include_line": ".include models/lm741.lib",
        "vcc": 5.8,
        "vee": -5.8,
        "veer": -0.97,
        "options": [
            "method=Gear",
            "cshunt=100f",
            "trtol=7",
            "reltol=2e-3",
            "vntol=1e-5",
            "abstol=1e-9",
            "itl4=100",
            "gmin=1e-10",
        ],
        "save_hidden": False,
        "suffix": "_741",
    },
    # AmpOp moderno: LT1810 (325 MHz, 350 V/us, saida rail-to-rail, modelo
    # embarcado no LTspice). Bancada bench_moderno_sat.cir: satura 2.4 mV
    # abaixo de V+ e 1.2 mV acima de V-, entao os neuronios ocultos rodam
    # com 4.8 V e TERRA (sem trilho negativo).
    "moderno": {
        "subckt": "LT1810",
        "include_line": ".lib LTC.lib",
        "vcc": 4.8,
        "vee": -4.8,
        "veer": 0.0,
        "options": [
            "method=Gear",
            "trtol=7",
            "reltol=2e-3",
            "vntol=1e-5",
            "abstol=1e-9",
            "itl4=100",
            "gmin=1e-10",
        ],
        "save_hidden": False,
        "tran_startup": True,
        "suffix": "_moderno",
    },
}
T_WINDOW_US = 250
T_EDGE_US = 10
T_MEAS_US = 200
MAX_DRAWN_BRANCHES = 6

C_POS = "#2a78d6"
C_NEG = "#eb6834"
INK = "#33322e"
INK_2 = "#63615a"


def experiment_dir() -> Path:
    return Path(__file__).resolve().parent


def load_model() -> tuple[list[dict[str, np.ndarray]], dict]:
    payload = json.loads((experiment_dir() / "analog_mlp_weights.json").read_text())
    layers = [
        {"W": np.asarray(item["W"], dtype=np.float64), "b": np.asarray(item["b"], dtype=np.float64)}
        for item in payload["layers"]
    ]
    return layers, payload["meta"]


def load_vectors() -> dict:
    return json.loads((experiment_dir() / "spice_test_vectors.json").read_text())


def fmt_r(ohms: float) -> str:
    if ohms >= 1e6:
        return f"{ohms / 1e6:.6g}Meg"
    if ohms >= 1e3:
        return f"{ohms / 1e3:.6g}k"
    return f"{ohms:.6g}"


def weight_resistor(w: float) -> str:
    return fmt_r(RF / abs(w))


def fmt_v(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".") or "0"


# ---------------------------------------------------------------- netlist


def pos_rail(layer_index: int, i: int) -> str:
    return f"x{i}" if layer_index == 0 else f"a{layer_index}_{i}"


def neg_rail(layer_index: int, i: int) -> str:
    return f"nx{i}" if layer_index == 0 else f"na{layer_index}_{i}"


def pwl_source(values: list[float]) -> str:
    if all(v == values[0] for v in values):
        return fmt_v(values[0])
    points = ["0", fmt_v(values[0])]
    for j in range(1, len(values)):
        start = j * T_WINDOW_US
        points += [f"{start}u", fmt_v(values[j - 1]), f"{start + T_EDGE_US}u", fmt_v(values[j])]
    return f"PWL({' '.join(points)})"


def build_netlist(layers, meta, vectors, variant="ideal") -> str:
    spec = VARIANTS[variant]
    subckt = spec["subckt"]
    theta = meta["threshold"]
    n_vec = len(vectors["vectors"])
    total_us = n_vec * T_WINDOW_US
    lines = [
        f"* Analog MLP - 5-stage op-amp MNIST classifier ({subckt} variant)",
        "* Generated by analog_mlp.py from analog_mlp_weights.json - do not edit by hand.",
        spec["include_line"],
        f"VCC vcc 0 {spec['vcc']:.4g}",
        f"VEE vee 0 {spec['vee']:.4g}",
        f"VEER veer 0 {spec['veer']:.4g}",
        "VBP bp 0 1",
        "VBN bn 0 -1",
        f"VTH vth 0 {theta:.4g}",
    ]

    w1 = layers[0]["W"]
    pixel_used = np.abs(w1).sum(axis=1) > 0
    pixel_needs_neg = (w1 > 0).any(axis=1)
    for i in range(w1.shape[0]):
        if not pixel_used[i]:
            lines.append(f"* pixel {i} fully pruned - no source")
            continue
        values = [vec["pixels"][i] for vec in vectors["vectors"]]
        lines.append(f"VX{i} x{i} 0 {pwl_source(values)}")
        if pixel_needs_neg[i]:
            lines.append(f"BNX{i} nx{i} 0 V=-V(x{i})")

    last = len(layers) - 1
    for l_index, layer in enumerate(layers):
        stage = l_index + 1
        weights, biases = layer["W"], layer["b"]
        hidden = l_index < last
        next_w = layers[l_index + 1]["W"] if hidden else None
        lines.append(f"* ---- stage {stage}: {weights.shape[0]} -> {weights.shape[1]}"
                     f" ({'hidden, single-supply ReLU' if hidden else 'output, linear'})")
        for n in range(weights.shape[1]):
            out_node = f"a{stage}_{n}" if hidden else f"z{n}"
            sum_node = f"s{stage}_{n}"
            vee_node = "veer" if hidden else "vee"
            lines.append(f"XS{stage}_{n} 0 {sum_node} vcc {vee_node} {out_node} {subckt}")
            lines.append(f"RF{stage}_{n} {out_node} {sum_node} {fmt_r(RF)}")
            for i in range(weights.shape[0]):
                w = weights[i][n]
                if w == 0:
                    continue
                source = neg_rail(l_index, i) if w > 0 else pos_rail(l_index, i)
                lines.append(f"R{stage}_{n}_{i} {source} {sum_node} {weight_resistor(w)}")
            b = biases[n]
            if b > 0:
                lines.append(f"RB{stage}_{n} bn {sum_node} {weight_resistor(b)}")
            elif b < 0:
                lines.append(f"RB{stage}_{n} bp {sum_node} {weight_resistor(b)}")
            if hidden and (next_w[n] > 0).any():
                inv_sum = f"si{stage}_{n}"
                lines.append(f"XI{stage}_{n} 0 {inv_sum} vcc vee na{stage}_{n} {subckt}")
                lines.append(f"RIA{stage}_{n} {out_node} {inv_sum} {fmt_r(RF)}")
                lines.append(f"RIF{stage}_{n} na{stage}_{n} {inv_sum} {fmt_r(RF)}")

    lines.append("* ---- comparators: one op-amp per digit, fires above VTH")
    for k in range(10):
        lines.append(f"XC{k} z{k} vth vcc veer out{k} {subckt}")
        lines.append(f"RL{k} out{k} 0 100k")

    save_list = [f"V(z{k})" for k in range(10)] + [f"V(out{k})" for k in range(10)]
    if spec["save_hidden"]:
        save_list += [
            f"V(a{l_index + 1}_{n})"
            for l_index, layer in enumerate(layers[:-1])
            for n in range(layer["W"].shape[1])
        ]
        save_list += ["V(s4_7)", "V(s5_3)"]
        lines.append(".options plotwinsize=0")
    lines.append(f".save {' '.join(save_list)}")
    for option in spec["options"]:
        lines.append(f".options {option}")
    for j in range(n_vec):
        t = f"{j * T_WINDOW_US + T_MEAS_US}u"
        for k in range(10):
            lines.append(f".meas TRAN z_v{j}_d{k} FIND V(z{k}) AT={t}")
            lines.append(f".meas TRAN out_v{j}_d{k} FIND V(out{k}) AT={t}")
    tran_extra = " startup" if spec.get("tran_startup") else ""
    lines.append(f".tran 0 {total_us}u 0 2u{tran_extra}")
    lines.append(".end")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- schematics


def draw_summer(
    circuit: Circuit,
    name: str,
    sources: list[tuple[str, str]],
    sum_node: str,
    out_node: str,
    *,
    at: tuple[int, int],
    vcc: str = "vcc",
    vee: str = "veer",
    elided: int = 0,
) -> tuple[int, int]:
    """Inverting summing amplifier with explicit bus routing.

    ``sources`` is a list of (source_node, resistor_value). Returns the
    (x, y) of the op-amp output pin.
    """
    x, y = at
    opamp_x, opamp_y = x + 480, y + 88
    sum_bus_x = x + 400
    out_bus_x = opamp_x + 220
    circuit.opamp(f"X{name}", "0", sum_node, vcc, vee, out_node, at=(opamp_x, opamp_y))
    circuit.flag(opamp_x, opamp_y + 32, "0")
    circuit.opamp_supply_flags(opamp_x, opamp_y, vcc=vcc, vee=vee)
    circuit.resistor(f"RF{name}", out_node, sum_node, fmt_r(RF), at=(x + 260, y))
    circuit.flag(x + 260, y, out_node)
    circuit.wire(x + 356, y, sum_bus_x, y)
    circuit.wire(opamp_x + 144, opamp_y + 64, out_bus_x, opamp_y + 64)
    circuit.wire(out_bus_x, opamp_y + 64, out_bus_x, y)
    circuit.wire(out_bus_x, y, x + 260, y)
    last_row = y
    for index, (source_node, value) in enumerate(sources):
        ry = y + 128 + index * 144
        circuit.resistor(f"R{name}_{index}", source_node, sum_node, value, at=(x, ry))
        circuit.flag(x, ry, source_node)
        circuit.wire(x + 96, ry, sum_bus_x, ry)
        last_row = ry
    circuit.wire(sum_bus_x, y, sum_bus_x, max(last_row, opamp_y + 96))
    circuit.wire(sum_bus_x, opamp_y + 96, opamp_x, opamp_y + 96)
    circuit.flag(opamp_x, opamp_y + 96, sum_node)
    if elided:
        circuit.text(x, last_row + 128, f";... + {elided} ramos de entrada omitidos (ver netlist)", size=2)
    return opamp_x + 144, opamp_y + 64


def neuron_sources(layers, l_index: int, n: int) -> tuple[list[tuple[str, str]], int]:
    weights = layers[l_index]["W"][:, n]
    entries: list[tuple[str, str]] = []
    for i in np.flatnonzero(weights):
        w = weights[i]
        source = neg_rail(l_index, i) if w > 0 else pos_rail(l_index, i)
        entries.append((source, weight_resistor(w)))
    bias_entry = None
    b = layers[l_index]["b"][n]
    if b > 0:
        bias_entry = ("bn", weight_resistor(b))
    elif b < 0:
        bias_entry = ("bp", weight_resistor(b))
    keep = MAX_DRAWN_BRANCHES - (1 if bias_entry else 0)
    drawn = entries[:keep]
    elided = len(entries) - len(drawn)
    if bias_entry:
        drawn = [*drawn, bias_entry]
    return drawn, elided


def pick_min_fan_in(layers, candidates: list[int]) -> tuple[int, int]:
    best = None
    for l_index in candidates:
        counts = (layers[l_index]["W"] != 0).sum(axis=0)
        n = int(counts.argmin())
        if best is None or counts[n] < best[2]:
            best = (l_index, n, int(counts[n]))
    return best[0], best[1]


def build_hidden_neuron_asc(layers, path: Path) -> Path:
    l_index, n = pick_min_fan_in(layers, [1, 2, 3])
    stage = l_index + 1
    sources, elided = neuron_sources(layers, l_index, n)
    circuit = Circuit(f"Neuronio oculto a{stage}_{n} - somador single-supply (ReLU) + inversor")
    circuit.text(96, 32, f";Neuronio oculto a{stage}_{n}: soma ponderada com saturacao (ReLU)", size=2)
    circuit.text(1280, 32, ";Inversor: publica -a para a proxima camada", size=2)
    out_x, out_y = draw_summer(
        circuit,
        f"S{stage}_{n}",
        sources,
        f"s{stage}_{n}",
        f"a{stage}_{n}",
        at=(96, 96),
        vee="veer",
        elided=elided,
    )
    circuit.flag(out_x, out_y, f"a{stage}_{n}")
    inv_x, inv_y = draw_summer(
        circuit,
        f"I{stage}_{n}",
        [(f"a{stage}_{n}", fmt_r(RF))],
        f"si{stage}_{n}",
        f"na{stage}_{n}",
        at=(1280, 96),
        vee="vee",
    )
    circuit.iopin(inv_x + 96, inv_y, f"na{stage}_{n}", "Out")
    circuit.wire(inv_x, inv_y, inv_x + 96, inv_y)
    circuit.write_asc(path)
    return path


def build_output_neuron_asc(layers, meta, path: Path) -> Path:
    counts = (layers[-1]["W"] != 0).sum(axis=0)
    k = int(counts.argmin())
    sources, elided = neuron_sources(layers, len(layers) - 1, k)
    theta = meta["threshold"]
    circuit = Circuit(f"Saida do digito {k}: somador linear + comparador contra VTH")
    circuit.text(96, 32, f";Somador da saida z{k} (alimentacao simetrica)", size=2)
    circuit.text(1280, 32, f";Comparador: out{k} dispara quando z{k} > {theta:.2f} V", size=2)
    out_x, out_y = draw_summer(
        circuit,
        f"S5_{k}",
        sources,
        f"s5_{k}",
        f"z{k}",
        at=(96, 96),
        vee="vee",
        elided=elided,
    )
    circuit.flag(out_x, out_y, f"z{k}")
    comp_x, comp_y = 1300, 184
    circuit.opamp(f"XC{k}", f"z{k}", "vth", "vcc", "veer", f"out{k}", at=(comp_x, comp_y))
    circuit.flag(comp_x, comp_y + 32, f"z{k}")
    circuit.flag(comp_x, comp_y + 96, "vth")
    circuit.opamp_supply_flags(comp_x, comp_y, vcc="vcc", vee="veer")
    load_x = comp_x + 320
    circuit.wire(comp_x + 144, comp_y + 64, load_x, comp_y + 64)
    circuit.resistor(f"RL{k}", f"out{k}", "0", "100k", at=(load_x, comp_y + 64), symbol="res_v")
    circuit.flag(load_x, comp_y + 160, "0")
    circuit.iopin(load_x + 128, comp_y + 64, f"out{k}", "Out")
    circuit.wire(load_x, comp_y + 64, load_x + 128, comp_y + 64)
    circuit.write_asc(path)
    return path


# ---------------------------------------------------------------- topology figure


def fig_topology(layers, meta, out_base: Path) -> None:
    sizes = meta["layer_sizes"]
    x_positions = np.arange(len(sizes), dtype=float) * 1.6
    y_positions = []
    for size in sizes:
        span = 10.0
        y_positions.append(np.linspace(span / 2, -span / 2, size))

    segments, colors, widths = [], [], []
    max_w = max(np.abs(layer["W"]).max() for layer in layers)
    for l_index, layer in enumerate(layers):
        weights = layer["W"]
        rows, cols = np.nonzero(weights)
        for i, j in zip(rows, cols, strict=False):
            w = weights[i][j]
            segments.append(
                [
                    (x_positions[l_index], y_positions[l_index][i]),
                    (x_positions[l_index + 1], y_positions[l_index + 1][j]),
                ]
            )
            strength = abs(w) / max_w
            colors.append(
                matplotlib.colors.to_rgba(C_POS if w > 0 else C_NEG, 0.04 + 0.5 * strength)
            )
            widths.append(0.3 + 1.2 * strength)

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.add_collection(LineCollection(segments, colors=colors, linewidths=widths, zorder=1))
    for l_index, size in enumerate(sizes):
        ax.scatter(
            np.full(size, x_positions[l_index]),
            y_positions[l_index],
            s=26 if size > 32 else 44,
            color="white",
            edgecolor=INK_2,
            linewidth=0.8,
            zorder=3,
        )
    for k in range(10):
        ax.annotate(
            str(k),
            (x_positions[-1] + 0.12, y_positions[-1][k]),
            fontsize=9,
            color=INK,
            va="center",
        )
    stage_names = [
        f"Entrada\n{sizes[0]} px (8x8)",
        *[f"Oculta {i}\n{size} neuronios" for i, size in enumerate(sizes[1:-1], start=1)],
        f"Saida\n{sizes[-1]} saidas",
    ]
    for l_index, label in enumerate(stage_names):
        ax.annotate(
            label,
            (x_positions[l_index], y_positions[l_index][0] + 0.7),
            fontsize=9,
            color=INK,
            ha="center",
        )
    nonzero = meta["parameters_nonzero"]
    ax.set_title(
        f"Topologia treinada: {nonzero} resistores de peso, "
        "azul = peso positivo, laranja = negativo",
        fontsize=11,
        color=INK,
    )
    ax.set_xlim(x_positions[0] - 0.5, x_positions[-1] + 0.6)
    ax.set_ylim(-6.2, 6.8)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_base.with_suffix(".png"), dpi=200, facecolor="white")
    fig.savefig(out_base.with_suffix(".svg"), facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- entry point


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    layers, meta = load_model()
    vectors = load_vectors()

    library = output / "claw_opamps.lib"
    source_lib = experiment_dir().parents[1] / "examples" / "lib" / "claw_opamps.lib"
    if source_lib.resolve() != library.resolve():
        shutil.copyfile(source_lib, library)

    cir_path = output / "analog_mlp.cir"
    cir_path.write_text(build_netlist(layers, meta, vectors, "ideal"))
    cir_741_path = output / "analog_mlp_741.cir"
    cir_741_path.write_text(build_netlist(layers, meta, vectors, "741"))
    cir_moderno_path = output / "analog_mlp_moderno.cir"
    cir_moderno_path.write_text(build_netlist(layers, meta, vectors, "moderno"))

    hidden_asc = build_hidden_neuron_asc(layers, output / "neuronio_oculto.asc")
    output_asc = build_output_neuron_asc(layers, meta, output / "neuronio_saida.asc")

    report_images = experiment_dir().parents[1] / "reports" / "analog-mlp" / "imagens" / "generated"
    report_images.mkdir(parents=True, exist_ok=True)
    fig_topology(layers, meta, report_images / "rede_topologia")

    return {
        "cir": cir_path,
        "cir_741": cir_741_path,
        "cir_moderno": cir_moderno_path,
        "hidden_asc": hidden_asc,
        "output_asc": output_asc,
        "lib": library,
        "topologia": report_images / "rede_topologia.png",
    }


if __name__ == "__main__":
    print(build(experiment_dir()))
