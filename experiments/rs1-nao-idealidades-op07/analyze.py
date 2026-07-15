#!/usr/bin/env python3
"""RS1 (Aula S1) - pos-processamento das simulacoes OP07 para o relatorio rs1-nao-idealidades-op07.

Roda DENTRO do container claw-spice (python3 experiments/lab-01/analyze.py):

  --phase vos     le o VOS medido no item 3 e regenera vos_comp.inc
  --phase report  calcula IB+, IB-, Ios, VOS, Avd, Acm, CMRR e slew rate,
                  gera os graficos SVG/PNG em reports/rs1-nao-idealidades-op07/imagens/generated/
                  e grava results.json/results.md

As derivadas numericas (equivalentes a dd(u)/ddt(u) do Micro-Cap) usam
diferencas centrais sobre os dados do .raw.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from claw_spice.logs import parse_log
from claw_spice.plot import plot_waveform_data
from claw_spice.raw import WaveformData, WaveformSeries, trace_names, waveform_data

LAB = Path(__file__).resolve().parent
REPO = LAB.parent.parent
IMG = REPO / "reports" / "rs1-nao-idealidades-op07" / "imagens" / "generated"


def raw_path(stem: str) -> Path:
    for suffix in (".raw", ".op.raw"):
        candidate = LAB / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"nenhum .raw para {stem} em {LAB}")


def resolve_trace(path: Path, wanted: str) -> str:
    names = trace_names(path)
    for name in names:
        if name.lower() == wanted.lower():
            return name
    raise KeyError(f"trace '{wanted}' nao encontrado em {path.name}: {names}")


def single_point(path: Path, wanted: str) -> float:
    data = waveform_data(path, [resolve_trace(path, wanted)])
    return data.series[0].values[0]


def sweep(path: Path, y: str, x: str | None = None) -> tuple[list[float], list[float]]:
    x_name = resolve_trace(path, x) if x else None
    data = waveform_data(path, [resolve_trace(path, y)], x_trace=x_name)
    return data.x_values, data.series[0].values


def central_derivative(xs: list[float], ys: list[float]) -> list[float]:
    out: list[float] = []
    last = len(xs) - 1
    for i in range(len(xs)):
        lo, hi = max(0, i - 1), min(last, i + 1)
        dx = xs[hi] - xs[lo]
        out.append((ys[hi] - ys[lo]) / dx if dx else 0.0)
    return out


def measurement(log_path: Path, name: str) -> float | None:
    if not log_path.exists():
        return None
    for item in parse_log(log_path).measurements:
        if item.name.lower() == name.lower():
            return item.value
    return None


def zero_crossing(xs: list[float], ys: list[float]) -> float | None:
    for i in range(1, len(xs)):
        if ys[i - 1] == 0:
            return xs[i - 1]
        if ys[i - 1] * ys[i] < 0:
            frac = -ys[i - 1] / (ys[i] - ys[i - 1])
            return xs[i - 1] + frac * (xs[i] - xs[i - 1])
    return None


def plot(x_name: str, xs: list[float], series: list[tuple[str, list[float]]], out_name: str, title: str) -> None:
    data = WaveformData(x_name, xs, [WaveformSeries(name, values) for name, values in series])
    svg, png = plot_waveform_data(data, IMG / f"{out_name}.svg", title=title, png=True)
    print(f"  plot: {svg.name} (+{png.name if png else 'sem png'})")


def window(xs: list[float], ys: list[float], lo: float, hi: float) -> tuple[list[float], list[float]]:
    pairs = [(x, y) for x, y in zip(xs, ys) if lo <= x <= hi]
    return [p[0] for p in pairs], [p[1] for p in pairs]


def phase_vos() -> None:
    log_path = LAB / "item3_vos.log"
    vos = measurement(log_path, "vos")
    if vos is None:
        xs, ys = sweep(raw_path("item3_vos"), "V(out)")
        vos = zero_crossing(xs, ys)
    if vos is None:
        raise SystemExit("VOS nao pode ser determinado (item 3 rodou?)")
    (LAB / "vos_comp.inc").write_text(
        "* GERADO por analyze.py --phase vos: compensacao com o VOS medido no item 3.\n"
        f".param VOSC={vos:.9e}\n"
    )
    print(f"VOS medido = {vos * 1e6:.3f} uV -> vos_comp.inc atualizado")


def phase_report() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {}

    # Itens 1-2: correntes de polarizacao e de offset (pontos de operacao)
    ib_plus = -single_point(raw_path("item1_bias"), "I(Ri)")
    vout1 = single_point(raw_path("item1_bias"), "V(out)")
    ib_minus = single_point(raw_path("item2_ios"), "I(Rf)")
    vout2 = single_point(raw_path("item2_ios"), "V(out)")
    ios = ib_plus - ib_minus
    results["item1"] = {"ib_plus_A": ib_plus, "vout_V": vout1}
    results["item2"] = {"ib_minus_A": ib_minus, "vout_V": vout2, "ios_A": ios}

    # Item 3: VOS e curva de transferencia em malha aberta
    xs3, ys3 = sweep(raw_path("item3_vos"), "V(out)")
    vos = measurement(LAB / "item3_vos.log", "vos") or zero_crossing(xs3, ys3)
    results["item3"] = {"vos_V": vos}
    plot("Vin (V)", xs3, [("V(out)", ys3)], "item3_transfer",
         "Item 3 - V(out) x Vin em malha aberta (OP07)")
    zx, zy = window(xs3, ys3, vos - 3e-4, vos + 3e-4)
    plot("Vin (V)", zx, [("V(out)", zy)], "item3_transfer_zoom",
         "Item 3 - regiao linear em torno de VOS")

    # Item 4: ganho diferencial Avd = max |dVout/dVin|
    xs4, ys4 = sweep(raw_path("item4_avd"), "V(out)")
    d4 = central_derivative(xs4, ys4)
    # bordas usam diferenca unilateral; ficam fora da busca do maximo
    idx4 = max(range(1, len(d4) - 1), key=lambda i: abs(d4[i]))
    avd = abs(d4[idx4])
    results["item4"] = {
        "avd": avd,
        "avd_db": 20 * math.log10(avd),
        "avd_vin_at_max_V": xs4[idx4],
        "avd_secante_meas": measurement(LAB / "item4_avd.log", "avd_sec"),
    }
    plot("Vin (V)", xs4, [("V(out)", ys4)], "item4_transfer",
         "Item 4 - V(out) x Vin com offset compensado")
    zx4, zdy4 = window(xs4, d4, -1e-4, 1e-4)
    plot("Vin (V)", zx4, [("dV(out)/dVin", zdy4)], "item4_deriv",
         "Item 4 - derivada dV(out)/dVin (Avd no maximo)")

    # Item 5: ganho de modo comum Acm e CMRR
    xs5, ys5 = sweep(raw_path("item5_acm"), "V(out)")
    d5 = central_derivative(xs5, ys5)
    idx5 = max(range(1, len(d5) - 1), key=lambda i: abs(d5[i]))
    acm = abs(d5[idx5])
    cmrr_db = 20 * math.log10(avd / acm)
    results["item5"] = {
        "acm": acm,
        "acm_vin_at_max_V": xs5[idx5],
        "acm_secante_meas": measurement(LAB / "item5_acm.log", "acm_sec"),
        "cmrr_db": cmrr_db,
    }
    plot("Vin (V)", xs5, [("V(out)", ys5)], "item5_transfer",
         "Item 5 - V(out) x Vin em modo comum")
    plot("Vin (V)", xs5, [("dV(out)/dVin", d5)], "item5_deriv",
         "Item 5 - derivada dV(out)/dVin (Acm)")

    # Item 6: slew rate no degrau -15 V -> +15 V
    ts, vout6 = sweep(raw_path("item6_slew"), "V(out)")
    _, vin6 = sweep(raw_path("item6_slew"), "V(vin)")
    d6 = central_derivative(ts, vout6)
    # O slew rate e o patamar da rampa, nao o pico instantaneo acoplado do
    # degrau de entrada: considera apenas a regiao linear da subida
    # (|V(out)| < 10 V), como na medida de datasheet.
    ramp = [i for i in range(len(d6)) if abs(vout6[i]) < 10.0]
    idx6 = max(ramp, key=lambda i: abs(d6[i])) if ramp else max(
        range(len(d6)), key=lambda i: abs(d6[i]))
    sr_max = abs(d6[idx6]) / 1e6  # V/us
    # patamar da rampa (mediana): representa o slew rate sem o transitorio
    # de saida da saturacao, que inflaciona o maximo pontual
    from statistics import median
    sr_plateau = median(abs(d6[i]) for i in ramp) / 1e6 if ramp else sr_max
    results["item6"] = {
        "sr_max_V_per_us": sr_max,
        "sr_patamar_V_per_us": sr_plateau,
        "sr_t_at_max_s": ts[idx6],
        "sr_media_10V_meas_V_per_us": measurement(LAB / "item6_slew.log", "sr_avg"),
        "t_lo_s": measurement(LAB / "item6_slew.log", "t_lo"),
        "t_hi_s": measurement(LAB / "item6_slew.log", "t_hi"),
    }
    ts_us = [t * 1e6 for t in ts]
    plot("t (us)", ts_us, [("V(vin)", vin6), ("V(out)", vout6)], "item6_step",
         "Item 6 - resposta ao degrau -15 V -> +15 V (seguidor)")
    # Grafico da derivada saturado em +/-1 V/us para o pico instantaneo do
    # degrau nao esconder o patamar da rampa (o slew rate).
    d6_us = [max(min(v / 1e6, 1.0), -1.0) for v in d6]
    plot("t (us)", ts_us, [("dV(out)/dt (V/us)", d6_us)], "item6_deriv",
         "Item 6 - ddt(V(out)): slew rate (recortado em +/-1 V/us)")

    # Teste extra (item 7): slew rate de um AmpOp moderno (ADA4610) no mesmo
    # seguidor do item 6, para comparacao. So roda se a simulacao existir.
    try:
        raw7 = raw_path("item7_slew_ada")
    except FileNotFoundError:
        raw7 = None
    if raw7 is not None:
        ts7, vout7 = sweep(raw7, "V(out)")
        d7 = central_derivative(ts7, vout7)
        ramp7 = [i for i in range(len(d7)) if abs(vout7[i]) < 10.0]
        idx7 = max(ramp7, key=lambda i: abs(d7[i])) if ramp7 else max(
            range(len(d7)), key=lambda i: abs(d7[i]))
        from statistics import median as _median
        sr7_plateau = _median(abs(d7[i]) for i in ramp7) / 1e6 if ramp7 else abs(d7[idx7]) / 1e6
        results["item7"] = {
            "sr_max_V_per_us": abs(d7[idx7]) / 1e6,
            "sr_patamar_V_per_us": sr7_plateau,
            "sr_media_10V_meas_V_per_us": measurement(LAB / "item7_slew_ada.log", "sr_avg"),
            "t_lo_s": measurement(LAB / "item7_slew_ada.log", "t_lo"),
            "t_hi_s": measurement(LAB / "item7_slew_ada.log", "t_hi"),
        }
        # Comparacao das subidas: mesmo degrau, dois amplificadores.
        ts7_us = [t * 1e6 for t in ts7]
        window6 = [i for i in range(len(ts)) if ts[i] <= 60e-6]
        plot(
            "t (us)",
            [ts_us[i] for i in window6],
            [("V(out) OP07", [vout6[i] for i in window6])],
            "item7_op07_janela",
            "Item 7 - OP07 no mesmo degrau (0 a 60 us)",
        )
        plot(
            "t (us)",
            ts7_us,
            [("V(out) ADA4610", vout7)],
            "item7_ada_step",
            "Item 7 - ADA4610: resposta ao degrau -15 V -> +15 V (seguidor)",
        )

    (LAB / "results.json").write_text(json.dumps(results, indent=2))

    lines = [
        "# RS1 - resultados simulados (OP07, LTC.lib do LTspice)",
        "",
        f"- Item 1: IB+ = {ib_plus * 1e9:.4f} nA ; Vout = {vout1 * 1e3:.4f} mV",
        f"- Item 2: IB- = {ib_minus * 1e9:.4f} nA ; Vout = {vout2 * 1e3:.4f} mV ; "
        f"Ios = |IB+ - IB-| = {abs(ios) * 1e9:.4f} nA",
        f"- Item 3: VOS = {vos * 1e6:.3f} uV",
        f"- Item 4: Avd = {avd:.4g} ({20 * math.log10(avd):.2f} dB)",
        f"- Item 5: Acm = {acm:.4g} ; CMRR = {cmrr_db:.2f} dB",
        f"- Item 6: SR(max ddt) = {sr_max:.4g} V/us ; SR(patamar) = {sr_plateau:.4g} V/us ; "
        f"SR(-10V->+10V) = {results['item6']['sr_media_10V_meas_V_per_us']} V/us",
    ]
    if "item7" in results:
        lines.append(
            f"- Item 7 (ADA4610): SR(patamar) = {results['item7']['sr_patamar_V_per_us']:.4g} V/us ; "
            f"SR(-10V->+10V) = {results['item7']['sr_media_10V_meas_V_per_us']} V/us"
        )
    (LAB / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("vos", "report"), required=True)
    args = parser.parse_args()
    if args.phase == "vos":
        phase_vos()
    else:
        phase_report()


if __name__ == "__main__":
    main()
