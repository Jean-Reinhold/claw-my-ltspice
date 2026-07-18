"""Analyze the two LT1810 full-network runs and the input/activation benches.

Produces the report figures and macros that document:

- ``entrada_pwl.png`` — the discrete-input scheme of the main experiment:
  zero-order hold with 10 us linear ramps, reconstructed from
  ``spice_test_vectors.json`` with the same constants as ``analog_mlp.py``;
- ``saturacao_vtc.png`` — measured transfer curve of the inverting summer
  with the three op-amps at their calibrated rails (``bench_vtc.cir``),
  i.e. the activation function as the circuit realizes it;
- ``moderno_rede_saidas.png`` / ``moderno_rede_ondas.png`` — comparator
  states and waveforms of the reduced-window LT1810 full-network runs,
  uncompensated (``analog_mlp_moderno_fast``) against compensated
  (``analog_mlp_moderno_comp``);
- ``moderno_rede_decisao.png`` — decision latency of the compensated run,
  measured on the windows not affected by the 20 us ``startup`` ramp;
- ``gerado/valores_moderno.tex`` — number macros for the report and
  ``moderno_rede_summary.json`` with the same values.

Run inside Docker, after the sims:

    ./claw-spice code build experiments/analog-mlp/analyze_moderno_rede.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mpl-"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

C_BLUE = "#2a78d6"
C_AQUA = "#1baf7a"
C_ORANGE = "#eb6834"
C_RED = "#e34948"
GRID = "#d9d9d3"
INK = "#33322e"
INK_2 = "#63615a"

# Timing of the reduced-window LT1810 runs (analog_mlp_moderno_fast.py and
# analog_mlp_moderno_comp.py monkeypatch these into analog_mlp.py).
T_WINDOW_US = 15.0
T_EDGE_US = 0.3
N_VECTORS = 6
# `.tran ... startup` ramps every independent source over the first 20 us,
# so windows 0 and 1 measure the power-up transient, not the network.
STARTUP_US = 20.0
T_SAMPLE_US = 14.7  # sample instant inside each window (before the next edge)
FIRE_LEVEL = 2.4

# Timing of the main experiment (keep in sync with analog_mlp.py).
MAIN_WINDOW_US = 250.0
MAIN_EDGE_US = 10.0

RUNS = [
    ("sem_comp", "analog_mlp_moderno_fast", "sem compensação"),
    ("comp", "analog_mlp_moderno_comp", "com compensação"),
]


def experiment_dir() -> Path:
    return Path(__file__).resolve().parent


def report_dir() -> Path:
    return experiment_dir().parents[1] / "reports" / "analog-mlp"


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


def load_tran_raw(path: Path):
    from spicelib import RawRead

    raw = RawRead(str(path))
    try:
        axis = np.asarray(raw.get_axis(), dtype=float)
    except Exception:
        # Compressed LTspice raws store the time axis with sign markers.
        axis = np.asarray(raw.get_trace("time").get_wave(0), dtype=float)
    time_us = np.abs(axis) * 1e6

    def trace(name: str) -> np.ndarray:
        return np.asarray(raw.get_trace(name).get_wave(0), dtype=float)

    return time_us, trace


def load_dc_raw(path: Path):
    from spicelib import RawRead

    raw = RawRead(str(path))
    try:
        axis = np.asarray(raw.get_axis(), dtype=float)
    except Exception:
        # The sweep variable is the first trace of the DC raw.
        first = raw.get_trace_names()[0]
        axis = np.asarray(raw.get_trace(first).get_wave(0), dtype=float)

    def trace(name: str) -> np.ndarray:
        return np.asarray(raw.get_trace(name).get_wave(0), dtype=float)

    return axis, trace


def sample_at(time_us: np.ndarray, wave: np.ndarray, t_us: float) -> float:
    return float(np.interp(t_us, time_us, wave))


def elapsed_seconds(log_path: Path) -> float | None:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if "\x00" in text:
        text = log_path.read_bytes().decode("utf-16-le", errors="replace")
    match = re.search(r"Total elapsed time:\s*([\d.]+)\s*seconds", text)
    return float(match.group(1)) if match else None


def z_errors_mv(log_path: Path, vectors, valid: list[int]) -> tuple[float, float]:
    """|z_meas - z_model| over the valid windows of a reduced-window run,
    from the .meas lines of its log (measured at T_MEAS_US into the window)."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if "\x00" in text:
        text = log_path.read_bytes().decode("utf-16-le", errors="replace")
    meas = {
        m.group(1).lower(): float(m.group(2))
        for m in re.finditer(r"^(z_v\d+_d\d+):.*?=\s*([-+eE\d.]+)", text, re.M)
    }
    errors = [
        abs(meas[f"z_v{j}_d{k}"] - vectors[j]["logits"][k]) * 1000.0
        for j in valid
        for k in range(10)
    ]
    return float(np.mean(errors)), float(np.max(errors))


# ------------------------------------------------------------- input scheme


def pwl_wave(values: list[float], window_us: float, edge_us: float, t: np.ndarray) -> np.ndarray:
    """Evaluate the exact PWL waveform analog_mlp.py generates: hold the
    previous value, then ramp linearly to the next one over edge_us."""
    points_t = [0.0]
    points_v = [values[0]]
    for j in range(1, len(values)):
        start = j * window_us
        points_t += [start, start + edge_us]
        points_v += [values[j - 1], values[j]]
    return np.interp(t, points_t, points_v)


def fig_entrada_pwl(vectors, out_png: Path) -> list[int]:
    labels = [vec["label"] for vec in vectors]
    pixels = np.array([vec["pixels"] for vec in vectors])  # (20, 64)
    variances = pixels.var(axis=0)
    chosen = [int(i) for i in np.argsort(variances)[::-1][:3]]
    n_vec = len(vectors)
    total_us = n_vec * MAIN_WINDOW_US
    t = np.linspace(0.0, total_us, 8000)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9.6, 5.2), gridspec_kw={"height_ratios": [1.5, 1.0]}
    )
    colors = [C_BLUE, C_AQUA, C_ORANGE]
    for color, i in zip(colors, chosen, strict=False):
        wave = pwl_wave(list(pixels[:, i]), MAIN_WINDOW_US, MAIN_EDGE_US, t)
        ax1.plot(t / 1000.0, wave, color=color, linewidth=1.5)
        ax1.annotate(f"pixel {i}", (total_us / 1000.0 + 0.03, wave[-1]),
                     fontsize=9, color=color, va="center")
    for j in range(n_vec):
        ax1.axvline(j * MAIN_WINDOW_US / 1000.0, color=GRID, linewidth=0.6)
        ax1.annotate(str(labels[j]), ((j + 0.5) * MAIN_WINDOW_US / 1000.0, 1.06),
                     ha="center", fontsize=8, color=INK_2)
    ax1.set_xlim(0, total_us / 1000.0 + 0.45)
    ax1.set_ylim(-0.05, 1.16)
    ax1.set_ylabel("Tensão do pixel (V)", color=INK)
    ax1.set_xlabel("Tempo (ms)", color=INK)
    ax1.set_title(
        "Três fontes de entrada ao longo das vinte janelas "
        "(dígito de cada janela indicado no topo)",
        fontsize=10, color=INK,
    )
    style_axis(ax1)

    # Zoom on one window edge: hold + 10 us linear ramp.
    j_zoom = 3
    t0 = j_zoom * MAIN_WINDOW_US
    tz = np.linspace(t0 - 30.0, t0 + 50.0, 2000)
    for color, i in zip(colors, chosen, strict=False):
        wave = pwl_wave(list(pixels[:, i]), MAIN_WINDOW_US, MAIN_EDGE_US, tz)
        ax2.plot(tz - t0, wave, color=color, linewidth=1.6)
    ax2.axvspan(0.0, MAIN_EDGE_US, color=GRID, alpha=0.45)
    ax2.annotate("rampa de 10 µs", (MAIN_EDGE_US + 2.0, 0.55), fontsize=9, color=INK)
    ax2.annotate("patamar (janela anterior)", (-29.0, 0.55), fontsize=9, color=INK_2)
    ax2.set_xlim(-30.0, 50.0)
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_xlabel(
        f"Tempo em torno da troca da janela {j_zoom} (µs)", color=INK
    )
    ax2.set_ylabel("Tensão do pixel (V)", color=INK)
    style_axis(ax2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)
    return chosen


# ------------------------------------------------------------- activation VTC


def fig_vtc(out_png: Path) -> dict[str, float]:
    sweep, trace = load_dc_raw(experiment_dir() / "bench_vtc.raw")
    # The summer inverts: activation reads as V(out) against -vin.
    x = -sweep
    order = np.argsort(x)
    x = x[order]
    curves = [
        ("Ideal", "V(o1)", C_BLUE, "-"),
        ("LM741", "V(o2)", C_ORANGE, "--"),
        ("LT1810", "V(o3)", C_AQUA, "-"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    clip = {}
    ys = {}
    for name, node, color, style in curves:
        y = trace(node)[order]
        ys[name] = y
        ax.plot(x, y, color=color, linewidth=1.8, linestyle=style, label=name)
        clip[f"{name}_hi"] = float(y.max())
        clip[f"{name}_lo"] = float(y.min())
    # Input-referred shift of the LT1810 curve: bias current over Rf.
    x_mid_ideal = float(np.interp(2.4, ys["Ideal"], x))
    x_mid_mod = float(np.interp(2.4, ys["LT1810"], x))
    offset = x_mid_mod - x_mid_ideal
    clip["LT1810_shift"] = offset
    ax.annotate(
        "", (x_mid_mod, 2.4), (x_mid_ideal, 2.4),
        arrowprops={"arrowstyle": "<->", "color": INK, "linewidth": 1.0},
    )
    ax.annotate(
        f"deslocamento de {offset:.2f} V\n(corrente de polarização)".replace(".", ","),
        (x_mid_mod + 0.25, 2.15), fontsize=9, color=INK,
    )
    ax.axhline(0.0, color=GRID, linewidth=0.8)
    ax.axhline(4.8, color=C_RED, linewidth=1.0, linestyle="--")
    ax.annotate("saturação superior (4,8 V)", (-3.7, 4.95), fontsize=9, color=C_RED)
    ax.annotate("saturação inferior (0 V):\nneurônio cortado (ReLU)",
                (-3.7, 0.6), fontsize=9, color=INK_2)
    ax.set_xlabel("Entrada equivalente do somador $-v_{in}$ (V)", color=INK)
    ax.set_ylabel("Tensão de saída (V)", color=INK)
    ax.set_title(
        "Curva de transferência medida do somador (Rf = Ri = 100 kΩ) "
        "nos trilhos calibrados",
        fontsize=10, color=INK,
    )
    ax.set_xlim(-4, 6.2)
    ax.set_ylim(-0.5, 5.4)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK, loc="lower right")
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)
    return clip


# ------------------------------------------------------------- LT1810 network


def sampled_outputs(time_us, trace) -> np.ndarray:
    matrix = np.zeros((N_VECTORS, 10))
    for j in range(N_VECTORS):
        t = j * T_WINDOW_US + T_SAMPLE_US
        for k in range(10):
            matrix[j, k] = sample_at(time_us, trace(f"V(out{k})"), t)
    return matrix


def fig_rede_saidas(runs, labels, out_png: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 5.6), sharex=True)
    for ax, (key, _stem, name) in zip(axes, RUNS, strict=False):
        matrix = runs[key]["sampled"]
        ax.imshow(matrix.T, cmap="Blues", aspect="auto", vmin=0.0, vmax=4.8)
        for j in range(N_VECTORS):
            ax.add_patch(plt.Rectangle((j - 0.5, labels[j] - 0.5), 1, 1,
                                       fill=False, edgecolor=C_RED, linewidth=1.4))
        n_startup = int(np.ceil(STARTUP_US / T_WINDOW_US))
        ax.axvline(n_startup - 0.5, color=INK_2, linewidth=1.0, linestyle=":")
        ax.annotate("janelas sob rampa de partida", (0.4, 9.1), fontsize=8, color=INK_2)
        ax.set_yticks(range(10))
        ax.set_yticklabels([str(k) for k in range(10)], fontsize=8)
        ax.set_ylabel("Comparador", color=INK)
        ax.set_title(f"Rede completa com LT1810, {name}", fontsize=10, color=INK)
        ax.tick_params(colors=INK_2)
    axes[1].set_xticks(range(N_VECTORS))
    axes[1].set_xticklabels([str(label) for label in labels], fontsize=9)
    axes[1].set_xlabel("Janela de teste (dígito apresentado)", color=INK)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_rede_ondas(runs, labels, out_png: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9.6, 5.9), sharex=True)
    total_us = N_VECTORS * T_WINDOW_US
    for ax, (key, _stem, name) in zip(axes, RUNS, strict=False):
        time_us, trace = runs[key]["raw"]
        for k in range(10):
            ax.plot(time_us, trace(f"V(out{k})"), color=INK_2, linewidth=0.5, alpha=0.25)
        if key == "sem_comp":
            ax.plot(time_us, trace("V(out7)"), color=C_RED, linewidth=0.8, alpha=0.9)
        for j, label in enumerate(labels):
            window = (time_us >= j * T_WINDOW_US) & (time_us <= (j + 1) * T_WINDOW_US)
            ax.plot(time_us[window], trace(f"V(out{label})")[window],
                    color=C_BLUE, linewidth=1.6)
            ax.annotate(str(label), ((j + 0.5) * T_WINDOW_US, 5.25),
                        ha="center", fontsize=9, color=INK)
        ax.axvspan(0.0, STARTUP_US, color=GRID, alpha=0.35)
        ax.annotate("rampa de partida (20 µs)", (1.0, -0.85), fontsize=8, color=INK_2)
        ax.set_ylabel("Comparadores (V)", color=INK)
        ax.set_ylim(-1.1, 5.7)
        ax.set_title(f"Rede completa com LT1810, {name}", fontsize=10, color=INK)
        style_axis(ax)
    axes[1].set_xlim(0, total_us)
    axes[1].set_xlabel("Tempo (µs)", color=INK)
    handles = [
        Line2D([], [], color=C_BLUE, linewidth=1.6,
               label="comparador do dígito da janela"),
        Line2D([], [], color=C_RED, linewidth=1.0, label="out$_7$ (disparo indevido)"),
        Line2D([], [], color=INK_2, linewidth=0.8, alpha=0.5,
               label="demais comparadores"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
               fontsize=9, labelcolor=INK)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def decision_latencies(time_us, trace, labels) -> dict[int, float | None]:
    """Interpolated instant, per window, at which the expected comparator
    crosses FIRE_LEVEL, measured from the start of the input edge."""
    latencies: dict[int, float | None] = {}
    for j, label in enumerate(labels):
        start = j * T_WINDOW_US
        end = (j + 1) * T_WINDOW_US
        window = (time_us >= start) & (time_us <= end)
        t = time_us[window]
        out = trace(f"V(out{label})")[window]
        above = np.flatnonzero(out > FIRE_LEVEL)
        if len(above) == 0 or above[0] == 0:
            latencies[j] = None
            continue
        i = above[0]
        crossing = np.interp(FIRE_LEVEL, [out[i - 1], out[i]], [t[i - 1], t[i]])
        latencies[j] = float(crossing - start)
    return latencies


def fig_rede_decisao(runs, labels, valid, out_png: Path) -> None:
    time_us, trace = runs["comp"]["raw"]
    latencies = runs["comp"]["latencies"]
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    listed = []
    for j in valid:
        label = labels[j]
        start = j * T_WINDOW_US
        window = (time_us >= start) & (time_us <= start + 3.0)
        ax.plot(time_us[window] - start, trace(f"V(out{label})")[window],
                color=C_BLUE, linewidth=1.5, alpha=0.85)
        lat = latencies[j]
        if lat is not None:
            ax.plot([lat], [FIRE_LEVEL], "o", color=C_BLUE, markersize=7,
                    markeredgecolor="white")
            listed.append((label, lat))
    listed.sort(key=lambda item: item[1])
    text = "\n".join(
        f"dígito {label}: {lat:.2f} µs".replace(".", ",") for label, lat in listed
    )
    ax.annotate(text, (2.35, 0.55), fontsize=9, color=INK,
                bbox={"boxstyle": "round,pad=0.4", "facecolor": "white",
                      "edgecolor": GRID})
    ax.axhline(FIRE_LEVEL, color=C_RED, linewidth=1.0, linestyle="--")
    ax.annotate("nível de decisão (2,4 V)", (0.08, FIRE_LEVEL + 0.18),
                fontsize=9, color=C_RED)
    ax.set_xlim(0, 3.0)
    ax.set_ylim(-0.2, 5.2)
    ax.set_xlabel("Tempo desde o início da troca de imagem (µs)", color=INK)
    ax.set_ylabel("Comparador do dígito correto (V)", color=INK)
    ax.set_title(
        "Latência de decisão da rede completa compensada "
        "(janelas fora da rampa de partida)",
        fontsize=10, color=INK,
    )
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------- entry point


def fmt_br(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def build(output_dir: str | Path) -> dict[str, object]:
    output = Path(output_dir)
    exp = experiment_dir()
    payload = json.loads((exp / "spice_test_vectors.json").read_text())
    all_vectors = payload["vectors"]
    labels = [vec["label"] for vec in all_vectors[:N_VECTORS]]

    images = report_dir() / "imagens" / "generated"
    images.mkdir(parents=True, exist_ok=True)
    tables = report_dir() / "gerado"
    tables.mkdir(parents=True, exist_ok=True)

    chosen_pixels = fig_entrada_pwl(all_vectors, images / "entrada_pwl.png")
    clip = fig_vtc(images / "saturacao_vtc.png")

    runs: dict[str, dict] = {}
    for key, stem, _name in RUNS:
        time_us, trace = load_tran_raw(exp / f"{stem}.raw")
        runs[key] = {
            "raw": (time_us, trace),
            "sampled": sampled_outputs(time_us, trace),
            "latencies": decision_latencies(time_us, trace, labels),
            "cpu_s": elapsed_seconds(exp / f"{stem}.log"),
        }

    n_startup = int(np.ceil(STARTUP_US / T_WINDOW_US))
    valid = list(range(n_startup, N_VECTORS))

    fig_rede_saidas(runs, labels, images / "moderno_rede_saidas.png")
    fig_rede_ondas(runs, labels, images / "moderno_rede_ondas.png")
    fig_rede_decisao(runs, labels, valid, images / "moderno_rede_decisao.png")

    summary: dict[str, object] = {
        "windows_valid": valid,
        "clip_vtc": clip,
        "entrada_pixels": chosen_pixels,
    }
    for key, _stem, _name in RUNS:
        sampled = runs[key]["sampled"]
        fires = sampled > FIRE_LEVEL
        clean = [
            bool(fires[j, labels[j]] and fires[j].sum() == 1) for j in range(N_VECTORS)
        ]
        summary[key] = {
            "cpu_s": runs[key]["cpu_s"],
            "clean_fire_valid": int(sum(clean[j] for j in valid)),
            "clean_fire_all": int(sum(clean)),
            "fired_per_window": [
                [k for k in range(10) if fires[j, k]] for j in range(N_VECTORS)
            ],
            "latencies_us": runs[key]["latencies"],
        }

    err_mean, err_max = z_errors_mv(
        exp / "analog_mlp_moderno_comp.log", all_vectors, valid
    )
    summary["comp_z_err_mean_mv"] = err_mean
    summary["comp_z_err_max_mv"] = err_max

    lat_valid = [runs["comp"]["latencies"][j] for j in valid]
    lat_valid = [lat for lat in lat_valid if lat is not None]
    lat_median = float(np.median(lat_valid))
    lat_max = float(max(lat_valid))
    summary["comp_latency_median_us"] = lat_median
    summary["comp_latency_max_us"] = lat_max

    lines = ["% Gerado por analyze_moderno_rede.py - nao editar a mao."]
    lines.append(f"\\newcommand{{\\vModRedeErrMedio}}{{{fmt_br(err_mean, 0)}}}")
    lines.append(f"\\newcommand{{\\vModRedeErrMax}}{{{fmt_br(err_max, 0)}}}")
    lines.append(f"\\newcommand{{\\vModRedeLatMediana}}{{{fmt_br(lat_median, 2)}}}")
    lines.append(f"\\newcommand{{\\vModRedeLatMax}}{{{fmt_br(lat_max, 2)}}}")
    fps = f"{1e6 / lat_max:,.0f}".replace(",", " ")
    lines.append(f"\\newcommand{{\\vFpsModRede}}{{{fps}}}")
    lines.append(
        f"\\newcommand{{\\vModRedeAcertosComp}}{{{summary['comp']['clean_fire_valid']}}}"
    )
    lines.append(
        f"\\newcommand{{\\vModRedeAcertosSemComp}}{{{summary['sem_comp']['clean_fire_valid']}}}"
    )
    lines.append(f"\\newcommand{{\\vModRedeJanelasValidas}}{{{len(valid)}}}")
    cpu_comp = runs["comp"]["cpu_s"]
    cpu_fast = runs["sem_comp"]["cpu_s"]
    if cpu_comp is not None:
        lines.append(f"\\newcommand{{\\vModRedeCpuComp}}{{{fmt_br(cpu_comp, 0)}}}")
    if cpu_fast is not None:
        lines.append(f"\\newcommand{{\\vModRedeCpuSemComp}}{{{fmt_br(cpu_fast, 0)}}}")
    for name, tex in [("Ideal", "Ideal"), ("LM741", "Lm"), ("LT1810", "Mod")]:
        lines.append(
            f"\\newcommand{{\\vVtcHi{tex}}}{{{fmt_br(clip[f'{name}_hi'], 2)}}}"
        )
        lines.append(
            f"\\newcommand{{\\vVtcLo{tex}}}{{{fmt_br(clip[f'{name}_lo'] * 1000, 1)}}}"
        )
    lines.append(
        f"\\newcommand{{\\vVtcOffsetMod}}{{{fmt_br(clip['LT1810_shift'], 2)}}}"
    )
    (tables / "valores_moderno.tex").write_text("\n".join(lines) + "\n")

    out_json = output / "moderno_rede_summary.json"
    out_json.write_text(json.dumps(summary, indent=2, default=float))
    print(f"[analyze-moderno] {json.dumps(summary, indent=2, default=float)}")
    return {"summary": out_json}


if __name__ == "__main__":
    print(build(experiment_dir()))
