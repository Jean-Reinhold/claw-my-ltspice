"""Measure real decision latency from the reduced-window LT1810 full-network run.

Ad-hoc analysis for analog_mlp_moderno_fast.raw (see analog_mlp_moderno_fast.py).
For each image window, finds how long after the input edge the dominant
comparator output takes to cross half-rail (~2.4 V) and to fully settle
(~4.5 V), so we can compare against the 1.9us bench_chain_moderno.cir
estimate used in the report.

    ./claw-spice code build experiments/analog-mlp/analyze_fast_latency.py \
        --output-dir experiments/analog-mlp
"""

from __future__ import annotations

from pathlib import Path

from spicelib import RawRead  # type: ignore

T_WINDOW_US = 15
T_EDGE_US = 0.3
N_VECTORS = 6
LABELS = [0, 1, 2, 3, 4, 5]


def experiment_dir() -> Path:
    return Path(__file__).resolve().parent


RAW_NAME = "analog_mlp_moderno_comp.raw"


def build(output_dir: str | Path) -> dict:
    raw_path = experiment_dir() / RAW_NAME
    raw = RawRead(str(raw_path))
    t = raw.get_trace("time").get_wave()
    outs = {k: raw.get_trace(f"V(out{k})").get_wave() for k in range(10)}
    zs = {k: raw.get_trace(f"V(z{k})").get_wave() for k in range(10)}

    report = []
    for j in range(N_VECTORS):
        win_start = j * T_WINDOW_US * 1e-6
        edge_end = win_start + T_EDGE_US * 1e-6
        win_end = win_start + T_WINDOW_US * 1e-6
        mask = (t >= win_start) & (t < win_end)
        idx = [i for i, m in enumerate(mask) if m]
        if not idx:
            continue
        final_vals = {k: outs[k][idx[-1]] for k in range(10)}
        dominant = max(final_vals, key=final_vals.get)

        wave = outs[dominant]
        t_half = None
        t_settled = None
        for i in idx:
            if t[i] < edge_end:
                continue
            if t_half is None and wave[i] >= 2.4:
                t_half = t[i]
            if t_settled is None and wave[i] >= 4.5:
                t_settled = t[i]
            if t_half is not None and t_settled is not None:
                break

        report.append({
            "window": j,
            "label_expected": LABELS[j],
            "dominant_output": dominant,
            "correct": bool(dominant == LABELS[j]),
            "final_out_dominant_V": round(float(final_vals[dominant]), 4),
            "final_z_dominant_V": round(float(zs[dominant][idx[-1]]), 4),
            "final_out_expected_V": round(float(final_vals[LABELS[j]]), 4),
            "t_half_rail_us": None if t_half is None else round(float(t_half - edge_end) * 1e6, 4),
            "t_settled_4v5_us": None if t_settled is None else round(float(t_settled - edge_end) * 1e6, 4),
        })

    out_path = Path(output_dir) / f"{Path(RAW_NAME).stem}_latency_report.json"
    import json
    out_path.write_text(json.dumps(report, indent=2))
    return {"report": out_path, "windows": report}


if __name__ == "__main__":
    print(build(experiment_dir()))
