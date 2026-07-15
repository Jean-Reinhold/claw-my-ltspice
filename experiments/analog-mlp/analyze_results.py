"""Compare the LTspice runs of the analog MLP against the numpy model.

Reads the ``.meas`` results and ``.raw`` waveforms of the two variants
(``analog_mlp`` = ideal macromodel, ``analog_mlp_741`` = vendor LM741) and
produces the report figures:

- one-sample figure: all 10 output-layer voltages for a single test digit;
- inner-state figures: hidden activations per layer for that sample, the
  layer-4 activation pattern across all windows, and the virtual ground of
  a summing node;
- agreement figures: SPICE vs numpy logit scatter, comparator heatmap and
  waveforms;
- circuit inference time (comparator decision latency per window);
- ``gerado/tabela_medidas.tex`` and ``gerado/valores_sim.tex`` (number
  macros) for the report.

Run inside Docker, after the sims:

    ./claw-spice code build experiments/analog-mlp/analyze_results.py \
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

C_BLUE = "#2a78d6"
C_AQUA = "#1baf7a"
C_ORANGE = "#eb6834"
C_RED = "#e34948"
GRID = "#d9d9d3"
INK = "#33322e"
INK_2 = "#63615a"

WINDOW_MS = 0.25  # keep in sync with T_WINDOW_US in analog_mlp.py
FIRE_LEVEL = 2.4  # comparator output above this counts as "fired"
SAMPLE_WINDOW = 3  # the window whose digit gets the detailed figures
HIDDEN_SIZES = [48, 32, 24, 16]

MEAS_RE = re.compile(
    r"^(?P<name>(?:z|out)_v\d+_d\d+):.*?=\s*(?P<value>[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)",
    re.IGNORECASE,
)


def experiment_dir() -> Path:
    return Path(__file__).resolve().parent


def report_dir() -> Path:
    return experiment_dir().parents[1] / "reports" / "analog-mlp"


def parse_measurements(log_path: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if "\x00" in text:
        text = log_path.read_bytes().decode("utf-16-le", errors="replace")
    for line in text.splitlines():
        match = MEAS_RE.match(line.strip())
        if match:
            values[match.group("name").lower()] = float(match.group("value"))
    return values


def meas_matrix(meas: dict[str, float], prefix: str, n_vec: int) -> np.ndarray:
    return np.array([[meas[f"{prefix}_v{j}_d{k}"] for k in range(10)] for j in range(n_vec)])


def load_raw(path: Path):
    from spicelib import RawRead

    raw = RawRead(str(path))
    try:
        axis = np.asarray(raw.get_axis(), dtype=float)
    except Exception:
        # Compressed LTspice raws store the time axis with sign markers and
        # spicelib refuses get_axis(); read the trace and drop the signs.
        axis = np.asarray(raw.get_trace("time").get_wave(0), dtype=float)
    time_ms = np.abs(axis) * 1000.0

    def trace(name: str) -> np.ndarray:
        return np.asarray(raw.get_trace(name).get_wave(0), dtype=float)

    return time_ms, trace


def sample_at(time_ms: np.ndarray, wave: np.ndarray, t_ms: float) -> float:
    return float(np.interp(t_ms, time_ms, wave))


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)


# ------------------------------------------------------------- figures


def fig_one_sample(vectors, meas, theta, out_png: Path, window=SAMPLE_WINDOW) -> None:
    vec = vectors[window]
    label = vec["label"]
    z = [meas[f"z_v{window}_d{k}"] for k in range(10)]
    out = [meas[f"out_v{window}_d{k}"] for k in range(10)]

    fig = plt.figure(figsize=(9.2, 3.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 2.6], wspace=0.25)
    ax_img = fig.add_subplot(gs[0])
    ax_img.imshow(np.asarray(vec["pixels"]).reshape(8, 8), cmap="gray_r")
    ax_img.set_xticks([])
    ax_img.set_yticks([])
    for spine in ax_img.spines.values():
        spine.set_color(GRID)
    ax_img.set_title(f"Entrada: dígito {label}\n(64 tensões, 0 a 1 V)", fontsize=10, color=INK)

    ax = fig.add_subplot(gs[1])
    x = np.arange(10)
    width = 0.4
    ax.bar(x - width / 2, z, width, color=C_BLUE, label="Saída do somador $V(z_k)$")
    ax.bar(x + width / 2, out, width, color=C_AQUA, label="Comparador $V(out_k)$")
    ax.axhline(theta, color=C_RED, linewidth=1.2, linestyle="--")
    ax.annotate(f"$V_{{TH}}$ = {theta:.2f} V", (9.4, theta + 0.12), ha="right",
                fontsize=9, color=C_RED)
    ax.set_xticks(x)
    ax.set_xlabel("Neurônio de saída (dígito)", color=INK)
    ax.set_ylabel("Tensão medida no LTspice (V)", color=INK)
    ax.set_title("Camada de saída completa para essa amostra", fontsize=10, color=INK)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK, loc="upper left")
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_inner_sample(time_ms, trace, vectors, out_png: Path, window=SAMPLE_WINDOW) -> None:
    t_meas = window * WINDOW_MS + 0.8 * WINDOW_MS
    label = vectors[window]["label"]
    fig, axes = plt.subplots(1, 4, figsize=(10.4, 3.2), sharey=True)
    for panel, (layer, size) in enumerate(zip([1, 2, 3, 4], HIDDEN_SIZES, strict=False)):
        values = [
            sample_at(time_ms, trace(f"V(a{layer}_{n})"), t_meas) for n in range(size)
        ]
        ax = axes[panel]
        ax.bar(np.arange(size), values, color=C_BLUE, width=0.8)
        ax.axhline(4.8, color=C_RED, linewidth=0.9, linestyle="--", alpha=0.8)
        ax.set_title(f"Oculta {layer} ({size} neurônios)", fontsize=9, color=INK)
        ax.set_xlabel("neurônio", fontsize=8, color=INK_2)
        style_axis(ax)
    axes[0].set_ylabel("Ativação (V)", color=INK)
    axes[0].annotate("saturação 4,8 V", (0, 4.55), fontsize=8, color=C_RED)
    fig.suptitle(
        f"Estados internos com o dígito {label} na entrada: "
        "tensões de saída dos 120 neurônios ocultos",
        fontsize=10,
        color=INK,
    )
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_hidden_heatmap(time_ms, trace, vectors, out_png: Path) -> None:
    n_vec = len(vectors)
    labels = [vec["label"] for vec in vectors]
    matrix = np.zeros((16, n_vec))
    for j in range(n_vec):
        t_meas = j * WINDOW_MS + 0.8 * WINDOW_MS
        for n in range(16):
            matrix[n, j] = sample_at(time_ms, trace(f"V(a4_{n})"), t_meas)
    fig, ax = plt.subplots(figsize=(9.6, 3.2))
    ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0.0, vmax=4.8)
    ax.set_xticks(range(n_vec))
    ax.set_xticklabels([str(label) for label in labels], fontsize=8)
    ax.set_yticks(range(0, 16, 2))
    ax.set_xlabel("Janela de teste (dígito apresentado)", color=INK)
    ax.set_ylabel("Neurônio da camada oculta 4", color=INK)
    ax.set_title(
        "Padrão interno da última camada oculta: cada dígito acende uma combinação própria",
        fontsize=10,
        color=INK,
    )
    ax.tick_params(colors=INK_2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_virtual_ground(time_ms, trace, out_png: Path) -> None:
    t_max = 10 * WINDOW_MS
    mask = time_ms <= t_max
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 4.2), sharex=True)
    ax1.plot(time_ms[mask], trace("V(a4_7)")[mask], color=C_BLUE, linewidth=1.6)
    ax1.axhline(0, color=GRID, linewidth=0.8)
    ax1.set_ylabel("$V(a^{(4)}_7)$ (V)", color=INK)
    ax1.set_title(
        "Neurônio $a^{(4)}_7$: a saída satura em 0 V (ReLU) enquanto o nó de soma "
        "fica em terra virtual",
        fontsize=10,
        color=INK,
    )
    ax2.plot(time_ms[mask], 1000 * trace("V(s4_7)")[mask], color=C_ORANGE, linewidth=1.2)
    ax2.set_ylabel("$V(s^{(4)}_7)$ (mV)", color=INK)
    ax2.set_xlabel("Tempo (ms)", color=INK)
    for ax in (ax1, ax2):
        style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_scatter(numpy_z, runs, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.8))
    lo = min(numpy_z.min(), *[run["z"].min() for run in runs.values()]) - 0.3
    hi = max(numpy_z.max(), *[run["z"].max() for run in runs.values()]) + 0.3
    ax.plot([lo, hi], [lo, hi], color=GRID, linewidth=1.2, zorder=1)
    colors = {"ideal": C_BLUE, "741": C_ORANGE}
    names = {"ideal": "AmpOp ideal", "741": "LM741"}
    for variant, run in runs.items():
        err = np.abs(run["z"] - numpy_z)
        ax.scatter(
            numpy_z.ravel(),
            run["z"].ravel(),
            s=20,
            color=colors[variant],
            alpha=0.65,
            edgecolor="white",
            linewidth=0.3,
            zorder=2,
            label=f"{names[variant]} (erro máx. {err.max() * 1000:.0f} mV)",
        )
    ax.set_xlabel("Saída prevista pelo modelo (V)", color=INK)
    ax.set_ylabel("Saída medida no LTspice (V)", color=INK)
    ax.set_title("Circuito contra modelo (200 medidas por variante)",
                 fontsize=10, color=INK)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK, loc="upper left")
    style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_heatmap(out_matrix, labels, out_png: Path) -> None:
    n_vec = out_matrix.shape[0]
    fig, ax = plt.subplots(figsize=(9.6, 3.4))
    ax.imshow(out_matrix.T, cmap="Blues", aspect="auto", vmin=0.0, vmax=4.8)
    for j in range(n_vec):
        ax.add_patch(
            plt.Rectangle(
                (j - 0.5, labels[j] - 0.5), 1, 1, fill=False, edgecolor=C_RED, linewidth=1.4
            )
        )
    ax.set_xticks(range(n_vec))
    ax.set_xticklabels([str(label) for label in labels], fontsize=8)
    ax.set_yticks(range(10))
    ax.set_yticklabels([str(k) for k in range(10)], fontsize=8)
    ax.set_xlabel("Janela de teste (dígito apresentado)", color=INK)
    ax.set_ylabel("Neurônio de saída", color=INK)
    ax.set_title(
        "Saída dos dez comparadores em cada janela (contorno vermelho: dígito correto)",
        fontsize=10,
        color=INK,
    )
    ax.tick_params(colors=INK_2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_waveforms(time_ms, trace, vectors, theta, out_png: Path) -> None:
    labels = [vec["label"] for vec in vectors]
    n_show = min(10, len(labels))
    t_max = n_show * WINDOW_MS

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.6, 5.4), sharex=True)
    for k in range(10):
        z = trace(f"V(z{k})")
        ax1.plot(time_ms, z, color=INK_2, linewidth=0.7, alpha=0.35)
    for j in range(n_show):
        k = labels[j]
        window = (time_ms >= j * WINDOW_MS) & (time_ms <= (j + 1) * WINDOW_MS)
        ax1.plot(time_ms[window], trace(f"V(z{k})")[window], color=C_BLUE, linewidth=1.8)
        ax2.plot(time_ms[window], trace(f"V(out{k})")[window], color=C_BLUE, linewidth=1.8)
        ax2.annotate(str(k), ((j + 0.5) * WINDOW_MS, 4.4), ha="center", fontsize=9, color=INK)
    ax1.axhline(theta, color=C_RED, linewidth=1, linestyle="--")
    ax1.annotate(f"$V_{{TH}}$ = {theta:.2f} V", (t_max - 0.01, theta + 0.15), ha="right",
                 fontsize=9, color=C_RED)
    ax1.set_ylabel("Saídas $V(z_0..z_9)$ (V)", color=INK)
    ax1.set_title(
        "Dez janelas de 250 µs: a saída do dígito correto (azul) cruza $V_{TH}$ "
        "e dispara o comparador",
        fontsize=10,
        color=INK,
    )
    ax2.set_ylabel("Comparador do dígito correto (V)", color=INK)
    ax2.set_xlabel("Tempo (ms)", color=INK)
    ax2.set_xlim(0, t_max)
    for ax in (ax1, ax2):
        style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


def fig_transition(raws, vectors, theta, out_png: Path, window=SAMPLE_WINDOW) -> None:
    """Zoom on one window edge: the ideal op-amp steps almost instantly,
    the LM741 ramps at its slew rate and crosses the comparator later."""
    label = vectors[window]["label"]
    t0 = window * WINDOW_MS
    t1 = t0 + 0.09
    names = {"ideal": "AmpOp ideal", "741": "LM741"}
    colors = {"ideal": C_BLUE, "741": C_ORANGE}
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 4.6), sharex=True)
    for variant, (time_ms, trace) in raws.items():
        mask = (time_ms >= t0 - 0.005) & (time_ms <= t1)
        t_us = (time_ms[mask] - t0) * 1000.0
        ax1.plot(t_us, trace(f"V(z{label})")[mask], color=colors[variant],
                 linewidth=1.8, label=names[variant])
        ax2.plot(t_us, trace(f"V(out{label})")[mask], color=colors[variant],
                 linewidth=1.8, label=names[variant])
    ax1.axhline(theta, color=C_RED, linewidth=1, linestyle="--")
    ax1.annotate(f"$V_{{TH}}$", (2, theta + 0.15), fontsize=9, color=C_RED)
    ax1.set_ylabel(f"$V(z_{label})$ (V)", color=INK)
    ax1.set_title(
        f"Troca de imagem na entrada (janela do dígito {label}), ampliada: "
        "o 741 sobe no seu slew rate",
        fontsize=10, color=INK,
    )
    ax1.legend(frameon=False, fontsize=9, labelcolor=INK, loc="lower right")
    ax2.axhline(FIRE_LEVEL, color=C_RED, linewidth=1, linestyle="--")
    ax2.set_ylabel(f"$V(out_{label})$ (V)", color=INK)
    ax2.set_xlabel("Tempo desde a troca da imagem (us)", color=INK)
    for ax in (ax1, ax2):
        style_axis(ax)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------- timing


def fire_latencies_us(time_ms, trace, vectors) -> list[float]:
    """Comparator decision latency per window: time from the input step to
    the correct comparator output crossing FIRE_LEVEL."""
    latencies = []
    for j, vec in enumerate(vectors):
        k = vec["label"]
        start = j * WINDOW_MS
        end = (j + 1) * WINDOW_MS
        window = (time_ms >= start) & (time_ms <= end)
        t = time_ms[window]
        out = trace(f"V(out{k})")[window]
        above = np.flatnonzero(out > FIRE_LEVEL)
        if len(above) == 0 or above[0] == 0:
            continue  # never fired, or was already high at the window start
        crossing = np.interp(
            FIRE_LEVEL, [out[above[0] - 1], out[above[0]]], [t[above[0] - 1], t[above[0]]]
        )
        latencies.append((crossing - start) * 1000.0)
    return latencies


# ------------------------------------------------------------- report files


def latex_table(vectors, runs, out_tex: Path) -> None:
    has_741 = "741" in runs
    ref = runs["741"] if has_741 else runs["ideal"]
    cols = "c S[table-format=1.3] S[table-format=1.3]"
    header = "{Dígito} & {$z$ modelo (\\si{\\volt})} & {$z$ ideal (\\si{\\volt})}"
    if has_741:
        cols += " S[table-format=1.3]"
        header += " & {$z$ LM741 (\\si{\\volt})}"
    cols += " S[table-format=-1.3] c"
    header += " & {maior errada (\\si{\\volt})} & {Disparo} \\\\"
    lines = [
        "% Gerado por analyze_results.py - nao editar a mao.",
        f"\\begin{{tabular}}{{{cols}}}",
        "\\toprule",
        header,
        "\\midrule",
    ]
    for j, vec in enumerate(vectors[:10]):
        k = vec["label"]
        fires = ref["out"][j] > FIRE_LEVEL
        clean = bool(fires[k] and fires.sum() == 1)
        status = "Sim" if clean else "N\\~ao"
        runner_up = max(v for d, v in enumerate(ref["z"][j]) if d != k)
        row = f"{k} & {vec['logits'][k]:.3f} & {runs['ideal']['z'][j][k]:.3f}"
        if has_741:
            row += f" & {runs['741']['z'][j][k]:.3f}"
        row += f" & {runner_up:.3f} & {status} \\\\"
        lines.append(row)
    lines += ["\\bottomrule", "\\end{tabular}"]
    out_tex.write_text("\n".join(lines) + "\n")


def latex_values(numpy_z, runs, timing, out_tex: Path) -> None:
    def err(variant):
        return np.abs(runs[variant]["z"] - numpy_z) * 1000.0

    lines = ["% Gerado por analyze_results.py - nao editar a mao."]
    if "ideal" in runs:
        lines.append(f"\\newcommand{{\\vErrIdealMedio}}{{{err('ideal').mean():.1f}}}".replace(".", ","))
        lines.append(f"\\newcommand{{\\vErrIdealMax}}{{{err('ideal').max():.1f}}}".replace(".", ","))
    if "741" in runs:
        lines.append(f"\\newcommand{{\\vErrLmMedio}}{{{err('741').mean():.0f}}}")
        lines.append(f"\\newcommand{{\\vErrLmMax}}{{{err('741').max():.0f}}}")
    for variant, values in timing.items():
        if values:
            name = "Ideal" if variant == "ideal" else "Lm"
            lines.append(
                f"\\newcommand{{\\vLatencia{name}Mediana}}{{{np.median(values):.1f}}}".replace(".", ",")
            )
            lines.append(f"\\newcommand{{\\vLatencia{name}Max}}{{{max(values):.1f}}}".replace(".", ","))
    for variant, run in runs.items():
        fires = run["out"] > FIRE_LEVEL
        labels = run["labels"]
        clean = sum(
            bool(fires[j, labels[j]] and fires[j].sum() == 1) for j in range(len(labels))
        )
        name = "Ideal" if variant == "ideal" else "Lm"
        lines.append(f"\\newcommand{{\\vDisparos{name}}}{{{clean}}}")
    out_tex.write_text("\n".join(lines) + "\n")


# ------------------------------------------------------------- entry point


def build(output_dir: str | Path) -> dict[str, object]:
    output = Path(output_dir)
    exp = experiment_dir()
    payload = json.loads((exp / "spice_test_vectors.json").read_text())
    vectors = payload["vectors"]
    theta = payload["threshold"]
    n_vec = len(vectors)
    numpy_z = np.array([vec["logits"] for vec in vectors])
    labels = [vec["label"] for vec in vectors]

    runs = {}
    for variant, stem in [("ideal", "analog_mlp"), ("741", "analog_mlp_741")]:
        log_path = exp / f"{stem}.log"
        if not log_path.exists():
            continue
        meas = parse_measurements(log_path)
        if not meas:
            continue
        runs[variant] = {
            "meas": meas,
            "z": meas_matrix(meas, "z", n_vec),
            "out": meas_matrix(meas, "out", n_vec),
            "labels": labels,
            "raw": exp / f"{stem}.raw",
        }
    if not runs:
        raise RuntimeError("no measurements found - did the sims run?")

    detail = runs.get("741", runs["ideal"])
    images = report_dir() / "imagens" / "generated"
    images.mkdir(parents=True, exist_ok=True)
    tables = report_dir() / "gerado"
    tables.mkdir(parents=True, exist_ok=True)

    latex_table(vectors, runs, tables / "tabela_medidas.tex")
    fig_one_sample(vectors, detail["meas"], theta, images / "amostra_saidas.png")
    fig_scatter(numpy_z, runs, images / "logits_spice_vs_numpy.png")
    fig_heatmap(detail["out"], labels, images / "comparadores_heatmap.png")

    timing = {}
    raws = {}
    for variant, run in runs.items():
        if not run["raw"].exists():
            timing[variant] = []
            continue
        time_ms, trace = load_raw(run["raw"])
        raws[variant] = (time_ms, trace)
        timing[variant] = fire_latencies_us(time_ms, trace, vectors)
        if run is detail:
            fig_waveforms(time_ms, trace, vectors, theta, images / "formas_de_onda.png")
        if variant == "ideal":
            fig_inner_sample(time_ms, trace, vectors, images / "estados_internos.png")
            fig_hidden_heatmap(time_ms, trace, vectors, images / "atividade_oculta.png")
            fig_virtual_ground(time_ms, trace, images / "terra_virtual.png")
    if raws:
        fig_transition(raws, vectors, theta, images / "transicao_janela.png")

    latex_values(numpy_z, runs, timing, tables / "valores_sim.tex")

    summary = {
        "variants": {
            variant: {
                "logit_err_mean_mv": float(np.abs(run["z"] - numpy_z).mean() * 1000),
                "logit_err_max_mv": float(np.abs(run["z"] - numpy_z).max() * 1000),
                "fire_latency_us_median": float(np.median(timing[variant]))
                if timing[variant]
                else None,
                "fire_latency_us_max": float(max(timing[variant])) if timing[variant] else None,
            }
            for variant, run in runs.items()
        }
    }
    print(f"[analyze] {json.dumps(summary, indent=2)}")
    (output / "agreement.json").write_text(json.dumps(summary, indent=2))
    return {"agreement": output / "agreement.json"}


if __name__ == "__main__":
    print(build(experiment_dir()))
