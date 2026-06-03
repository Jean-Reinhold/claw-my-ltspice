from __future__ import annotations

import math
from pathlib import Path

from claw_spice.plot import plot_waveform_data
from claw_spice.raw import WaveformData, WaveformSeries


def generate_plot_assets(output_dir: str | Path = "docs-site/pages/assets/plots") -> list[Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plots = [
        _rc_step(output / "rc-step-vout.svg"),
        _voltage_follower(output / "opamp-voltage-follower.svg"),
        _noninverting(output / "opamp-noninverting.svg"),
        _inverting(output / "opamp-inverting.svg"),
        _summing(output / "opamp-summing.svg"),
        _difference(output / "opamp-difference.svg"),
        _active_lowpass(output / "opamp-active-lowpass.svg"),
    ]
    return plots


def _times(stop: float = 0.004, step: float = 0.0001) -> list[float]:
    count = int(stop / step) + 1
    return [index * step for index in range(count)]


def _step(times: list[float], level: float, delay: float = 0.0) -> list[float]:
    return [level if time >= delay else 0.0 for time in times]


def _settled_step(times: list[float], level: float, tau: float, delay: float = 0.0) -> list[float]:
    values: list[float] = []
    for time in times:
        if time < delay:
            values.append(0.0)
        else:
            values.append(level * (1.0 - math.exp(-(time - delay) / tau)))
    return values


def _plot(path: Path, title: str, x_values: list[float], series: list[WaveformSeries]) -> Path:
    svg, _png = plot_waveform_data(WaveformData("time", x_values, series), path, title=title)
    return svg


def _rc_step(path: Path) -> Path:
    times = _times(stop=0.006, step=0.00015)
    vin = _step(times, 5.0)
    vout = _settled_step(times, 5.0, tau=0.001)
    return _plot(path, "RC step response", times, [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)])


def _voltage_follower(path: Path) -> Path:
    times = _times()
    vin = _step(times, 1.0)
    vout = _settled_step(times, 0.998, tau=0.00008)
    return _plot(path, "Op-amp voltage follower", times, [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)])


def _noninverting(path: Path) -> Path:
    times = _times()
    vin = _step(times, 1.0)
    vout = _settled_step(times, 3.0, tau=0.00012)
    return _plot(path, "Op-amp non-inverting gain", times, [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)])


def _inverting(path: Path) -> Path:
    times = _times()
    vin = _step(times, 1.0)
    vout = _settled_step(times, -2.0, tau=0.00012)
    return _plot(path, "Op-amp inverting gain", times, [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)])


def _summing(path: Path) -> Path:
    times = _times()
    vin1 = _step(times, 0.5)
    vin2 = _step(times, 0.25, delay=0.001)
    vout = [-(2.0 * a + b) for a, b in zip(vin1, vin2, strict=False)]
    return _plot(
        path,
        "Op-amp inverting summing amplifier",
        times,
        [WaveformSeries("V(in1)", vin1), WaveformSeries("V(in2)", vin2), WaveformSeries("V(out)", vout)],
    )


def _difference(path: Path) -> Path:
    times = _times()
    vp = _step(times, 0.8)
    vm = _step(times, 0.3, delay=0.001)
    vout = [2.0 * (p - m) for p, m in zip(vp, vm, strict=False)]
    return _plot(
        path,
        "Op-amp difference amplifier",
        times,
        [WaveformSeries("V(plus)", vp), WaveformSeries("V(minus)", vm), WaveformSeries("V(out)", vout)],
    )


def _active_lowpass(path: Path) -> Path:
    times = _times(stop=0.008, step=0.00016)
    vin = [1.0 if int(time / 0.001) % 2 == 0 else 0.0 for time in times]
    vout: list[float] = []
    value = 0.0
    tau = 0.00045
    step = times[1] - times[0]
    alpha = 1.0 - math.exp(-step / tau)
    for sample in vin:
        value += (sample - value) * alpha
        vout.append(value)
    return _plot(path, "Buffered active low-pass response", times, [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)])
