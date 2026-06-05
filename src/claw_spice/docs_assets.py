from __future__ import annotations

import math
from pathlib import Path

from claw_spice.plot import plot_fft_waveform_data, plot_waveform_data
from claw_spice.raw import WaveformData, WaveformSeries


EXPECTED_PLOT_ASSETS = (
    "rc-step-vout.svg",
    "opamp-voltage-follower.svg",
    "opamp-noninverting.svg",
    "opamp-inverting.svg",
    "opamp-summing.svg",
    "opamp-difference.svg",
    "opamp-active-lowpass.svg",
    "precision-rectifier.svg",
    "sallen-key-lowpass.svg",
    "sallen-key-lowpass-fft.svg",
    "diode-clipper-spectrum.svg",
    "diode-clipper-spectrum-fft.svg",
    "rlc-step-ringing.svg",
    "passive-rc-spectrum-split.svg",
    "passive-rc-spectrum-low-fft.svg",
    "passive-rc-spectrum-high-fft.svg",
    "opamp-practical-integrator.svg",
    "opamp-practical-differentiator.svg",
    "sallen-key-highpass.svg",
    "sallen-key-highpass-fft.svg",
)


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
        _precision_rectifier(output / "precision-rectifier.svg"),
        _sallen_key(output / "sallen-key-lowpass.svg"),
        _sallen_key_fft(output / "sallen-key-lowpass-fft.svg"),
        _diode_clipper(output / "diode-clipper-spectrum.svg"),
        _diode_clipper_fft(output / "diode-clipper-spectrum-fft.svg"),
        _rlc_step_ringing(output / "rlc-step-ringing.svg"),
        _passive_rc_spectrum_split(output / "passive-rc-spectrum-split.svg"),
        _passive_rc_spectrum_low_fft(output / "passive-rc-spectrum-low-fft.svg"),
        _passive_rc_spectrum_high_fft(output / "passive-rc-spectrum-high-fft.svg"),
        _practical_integrator(output / "opamp-practical-integrator.svg"),
        _practical_differentiator(output / "opamp-practical-differentiator.svg"),
        _sallen_key_highpass(output / "sallen-key-highpass.svg"),
        _sallen_key_highpass_fft(output / "sallen-key-highpass-fft.svg"),
    ]
    return plots


def generate_opencode_reference(output_path: str | Path = "docs-site/pages/ai-instructions.md") -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    agent_paths = sorted(Path(".opencode/agent").glob("*.md"))
    skill_paths = sorted(Path(".opencode/skills").glob("*/SKILL.md"))
    lines = [
        "# Full AI Instructions",
        "",
        "This page is generated from the project-local OpenCode instruction files.",
        "It intentionally includes the complete text of every agent and skill so",
        "reviewers can see exactly how AI collaborators are instructed to design,",
        "simulate, render, verify, and report LTspice work in this repository.",
        "",
        "Regenerate this page with:",
        "",
        "```bash",
        "./claw-spice docs assets",
        "```",
        "",
        "## Agents",
        "",
    ]
    for path in agent_paths:
        lines.extend(_instruction_block(path, path.stem))
    lines.extend(["## Skills", ""])
    for path in skill_paths:
        lines.extend(_instruction_block(path, path.parent.name))
    output.write_text("\n".join(lines).rstrip() + "\n")
    return output


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


def _fft_plot(path: Path, title: str, x_values: list[float], series: WaveformSeries) -> Path:
    svg, _png = plot_fft_waveform_data(WaveformData("time", x_values, [series]), path, title=title)
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


def _precision_rectifier(path: Path) -> Path:
    times = _times(stop=0.004, step=0.00004)
    vin = [0.75 * math.sin(2.0 * math.pi * 1000.0 * time) for time in times]
    vrect = [max(value, 0.0) for value in vin]
    return _plot(
        path,
        "Precision rectifier response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(rect)", vrect)],
    )


def _sallen_key(path: Path) -> Path:
    times = _times(stop=0.006, step=0.00004)
    vin = [_mixed_signal(time) for time in times]
    vout = _lowpass_response(times, vin, cutoff_hz=1600.0)
    return _plot(
        path,
        "Sallen-Key low-pass response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)],
    )


def _sallen_key_fft(path: Path) -> Path:
    sample_rate = 50000.0
    sample_count = 512
    times = [index / sample_rate for index in range(sample_count)]
    output = _lowpass_response(times, [_mixed_signal(time) for time in times], cutoff_hz=1600.0)
    return _fft_plot(path, "FFT of Sallen-Key filtered output", times, WaveformSeries("V(out)", output))


def _diode_clipper(path: Path) -> Path:
    times = _times(stop=0.008, step=0.00004)
    vin = [3.0 * math.sin(2.0 * math.pi * 1000.0 * time) for time in times]
    clip = [_clip_positive(value) for value in vin]
    return _plot(
        path,
        "Diode clipper response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(clip)", clip)],
    )


def _diode_clipper_fft(path: Path) -> Path:
    sample_rate = 50000.0
    sample_count = 512
    times = [index / sample_rate for index in range(sample_count)]
    clip = [_clip_positive(3.0 * math.sin(2.0 * math.pi * 1000.0 * time)) for time in times]
    return _fft_plot(path, "FFT of diode-clipped output", times, WaveformSeries("V(clip)", clip))


def _rlc_step_ringing(path: Path) -> Path:
    times = _times(stop=0.004, step=0.00002)
    vin = _step(times, 5.0)
    frequency = 5200.0
    damping = 1800.0
    vout = [5.0 * (1.0 - math.exp(-damping * time) * math.cos(2.0 * math.pi * frequency * time)) for time in times]
    return _plot(
        path,
        "RLC step ringing response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)],
    )


def _passive_rc_spectrum_split(path: Path) -> Path:
    times, vin, low, high = _passive_rc_spectrum_data()
    return _plot(
        path,
        "Passive RC spectrum split",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(low)", low), WaveformSeries("V(high)", high)],
    )


def _passive_rc_spectrum_low_fft(path: Path) -> Path:
    times, _vin, low, _high = _passive_rc_spectrum_data(sample_count=512, sample_rate=50000.0)
    return _fft_plot(path, "FFT of RC low-pass output", times, WaveformSeries("V(low)", low))


def _passive_rc_spectrum_high_fft(path: Path) -> Path:
    times, _vin, _low, high = _passive_rc_spectrum_data(sample_count=512, sample_rate=50000.0)
    return _fft_plot(path, "FFT of RC high-pass output", times, WaveformSeries("V(high)", high))


def _practical_integrator(path: Path) -> Path:
    times = _times(stop=0.01, step=0.0001)
    vin = [0.1 if int(time / 0.001) % 2 == 0 else -0.1 for time in times]
    vout: list[float] = []
    value = 0.0
    step = times[1] - times[0]
    for sample in vin:
        value += -sample * step / 0.001
        value *= 0.995
        vout.append(value)
    return _plot(
        path,
        "Practical inverting integrator response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)],
    )


def _practical_differentiator(path: Path) -> Path:
    times = _times(stop=0.015, step=0.0001)
    vin = [0.05 * math.sin(2.0 * math.pi * 200.0 * time) for time in times]
    vout = [0.0]
    for previous, current in zip(vin, vin[1:], strict=False):
        vout.append(-0.00025 * (current - previous) / (times[1] - times[0]))
    return _plot(
        path,
        "Practical inverting differentiator response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", vout)],
    )


def _sallen_key_highpass(path: Path) -> Path:
    times = _times(stop=0.006, step=0.00004)
    vin = [_mixed_signal(time) for time in times]
    low = _lowpass_response(times, vin, cutoff_hz=1600.0)
    high = [sample - low_sample for sample, low_sample in zip(vin, low, strict=False)]
    return _plot(
        path,
        "Sallen-Key high-pass response",
        times,
        [WaveformSeries("V(in)", vin), WaveformSeries("V(out)", high)],
    )


def _sallen_key_highpass_fft(path: Path) -> Path:
    sample_rate = 50000.0
    sample_count = 512
    times = [index / sample_rate for index in range(sample_count)]
    vin = [_mixed_signal(time) for time in times]
    low = _lowpass_response(times, vin, cutoff_hz=1600.0)
    high = [sample - low_sample for sample, low_sample in zip(vin, low, strict=False)]
    return _fft_plot(path, "FFT of Sallen-Key high-pass output", times, WaveformSeries("V(out)", high))


def _mixed_signal(time: float) -> float:
    return math.sin(2.0 * math.pi * 500.0 * time) + 0.35 * math.sin(2.0 * math.pi * 8000.0 * time)


def _clip_positive(value: float) -> float:
    return min(value, 0.72 + max(value - 0.72, 0.0) * 0.06)


def _passive_rc_spectrum_data(
    *,
    sample_count: int | None = None,
    sample_rate: float | None = None,
) -> tuple[list[float], list[float], list[float], list[float]]:
    if sample_count and sample_rate:
        times = [index / sample_rate for index in range(sample_count)]
    else:
        times = _times(stop=0.02, step=0.00005)
    vin = [math.sin(2.0 * math.pi * 250.0 * time) + 0.6 * math.sin(2.0 * math.pi * 4000.0 * time) for time in times]
    low = _lowpass_response(times, vin, cutoff_hz=1000.0)
    high = [sample - low_sample for sample, low_sample in zip(vin, low, strict=False)]
    return times, vin, low, high


def _lowpass_response(times: list[float], samples: list[float], *, cutoff_hz: float) -> list[float]:
    if not times:
        return []
    tau = 1.0 / (2.0 * math.pi * cutoff_hz)
    previous_time = times[0]
    value = 0.0
    result: list[float] = []
    for time, sample in zip(times, samples, strict=False):
        step = max(time - previous_time, 0.0)
        alpha = 1.0 - math.exp(-step / tau) if step else 0.0
        value += (sample - value) * alpha
        result.append(value)
        previous_time = time
    return result


def _instruction_block(path: Path, title: str) -> list[str]:
    text = path.read_text()
    fence = _fence_for(text)
    return [
        f"### {title}",
        "",
        f"Source: `{path.as_posix()}`",
        "",
        f"{fence}markdown",
        text.rstrip(),
        fence,
        "",
    ]


def _fence_for(text: str) -> str:
    longest = 0
    current = 0
    for char in text:
        if char == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return "`" * max(3, longest + 1)
