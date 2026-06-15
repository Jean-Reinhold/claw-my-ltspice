from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from pathlib import Path

from claw_spice.raw import WaveformData, WaveformSeries, waveform_data
from claw_spice.render import render_png


COLORS = ("#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2")


@dataclass(frozen=True)
class ReferenceLine:
    value: float
    label: str
    color: str = "#6b7280"


def plot_raw_traces(
    raw_path: str | Path,
    traces: list[str] | tuple[str, ...],
    output: str | Path,
    *,
    x_trace: str | None = None,
    title: str | None = None,
    png: bool = False,
) -> tuple[Path, Path | None]:
    data = waveform_data(raw_path, traces, x_trace=x_trace)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_plot_svg(data, title or Path(raw_path).stem))
    png_path = render_png(output_path) if png else None
    return output_path, png_path


def plot_raw_fft(
    raw_path: str | Path,
    trace: str,
    output: str | Path,
    *,
    title: str | None = None,
    png: bool = False,
) -> tuple[Path, Path | None]:
    source = waveform_data(raw_path, [trace])
    return plot_fft_waveform_data(source, output, title=title or f"FFT of {trace}", png=png)


def plot_waveform_data(
    data: WaveformData,
    output: str | Path,
    *,
    title: str,
    reference_lines: tuple[ReferenceLine, ...] = (),
    png: bool = False,
) -> tuple[Path, Path | None]:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_plot_svg(data, title, reference_lines=reference_lines))
    png_path = render_png(output_path) if png else None
    return output_path, png_path


def plot_fft_waveform_data(
    data: WaveformData,
    output: str | Path,
    *,
    title: str,
    png: bool = False,
) -> tuple[Path, Path | None]:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_plot_svg(fft_waveform_data(data), title))
    png_path = render_png(output_path) if png else None
    return output_path, png_path


def fft_waveform_data(data: WaveformData) -> WaveformData:
    if len(data.series) != 1:
        raise ValueError("FFT plots require exactly one selected signal trace")
    if len(data.x_values) < 4:
        raise ValueError("FFT plots require at least four samples")
    sample_step = _sample_step(data.x_values)
    values = data.series[0].values
    sample_count = min(len(data.x_values), len(values), 2048)
    sample_count = _largest_power_of_two(sample_count)
    if sample_count < 4:
        raise ValueError("FFT plots require at least four usable samples")
    sampled = values[:sample_count]
    mean = sum(sampled) / sample_count
    centered = [value - mean for value in sampled]
    window = _hann_window(sample_count)
    window_sum = sum(window) or 1.0
    frequencies: list[float] = []
    magnitudes: list[float] = []
    for bin_index in range(sample_count // 2 + 1):
        real = 0.0
        imag = 0.0
        for sample_index, value in enumerate(centered):
            angle = -2.0 * math.pi * bin_index * sample_index / sample_count
            weighted = value * window[sample_index]
            real += weighted * math.cos(angle)
            imag += weighted * math.sin(angle)
        scale = 1.0 / window_sum if bin_index in {0, sample_count // 2} else 2.0 / window_sum
        frequencies.append(bin_index / (sample_count * sample_step))
        magnitudes.append(math.hypot(real, imag) * scale)
    return WaveformData("frequency (Hz)", frequencies, [WaveformSeries(f"FFT {data.series[0].trace}", magnitudes)])


def safe_plot_stem(raw_path: str | Path, traces: list[str] | tuple[str, ...]) -> str:
    trace_suffix = "_".join(_safe_token(trace) for trace in traces) if traces else "signals"
    return f"{Path(raw_path).stem}_{trace_suffix}"


def safe_fft_stem(raw_path: str | Path, trace: str) -> str:
    return f"{Path(raw_path).stem}_fft_{_safe_token(trace)}"


def _plot_svg(
    data: WaveformData,
    title: str,
    *,
    reference_lines: tuple[ReferenceLine, ...] = (),
) -> str:
    width = 960
    height = 560
    left = 86
    right = 28
    top = 72
    bottom = 82
    plot_width = width - left - right
    plot_height = height - top - bottom
    x_min, x_max = _range(data.x_values)
    if data.x_values and min(data.x_values) >= 0:
        x_min = 0.0
    y_values = [value for series in data.series for value in series.values]
    y_values.extend(line.value for line in reference_lines)
    y_min, y_max = _range(y_values)

    def sx(value: float) -> float:
        return left + ((value - x_min) / (x_max - x_min)) * plot_width

    def sy(value: float) -> float:
        return top + plot_height - ((value - y_min) / (y_max - y_min)) * plot_height

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>.title{font:700 20px system-ui,sans-serif;fill:#111827}.axis{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;fill:#374151}.legend{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;fill:#111827}.grid{stroke:#e5e7eb;stroke-width:1}.frame{stroke:#374151;stroke-width:1.5;fill:none}.reference{stroke-dasharray:7 5;stroke-width:1.7}.reference-label{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;fill:#374151}</style>',
        f'<text x="{left}" y="34" class="title">{html.escape(title)}</text>',
    ]

    for tick in _ticks(x_min, x_max, 6):
        x = sx(tick)
        body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_height}" class="grid"/>')
        body.append(f'<text x="{x:.2f}" y="{top + plot_height + 24}" text-anchor="middle" class="axis">{_format_number(tick)}</text>')
    for tick in _ticks(y_min, y_max, 6):
        y = sy(tick)
        body.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" class="grid"/>')
        body.append(f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" class="axis">{_format_number(tick)}</text>')

    body.append(f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" class="frame"/>')

    for line in reference_lines:
        y = sy(line.value)
        body.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" '
            f'class="reference" stroke="{html.escape(line.color)}"/>'
        )
        body.append(
            f'<text x="{left + plot_width - 8}" y="{y - 7:.2f}" text-anchor="end" '
            f'class="reference-label">{html.escape(line.label)}</text>'
        )

    for index, series in enumerate(data.series):
        color = COLORS[index % len(COLORS)]
        points = []
        for x_value, y_value in zip(data.x_values, series.values, strict=False):
            if math.isfinite(x_value) and math.isfinite(y_value):
                points.append(f"{sx(x_value):.2f},{sy(y_value):.2f}")
        body.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.25" stroke-linejoin="round" stroke-linecap="round"/>')

    legend_x = left
    legend_y = height - 34
    for index, series in enumerate(data.series):
        x = legend_x + index * 190
        color = COLORS[index % len(COLORS)]
        body.append(f'<line x1="{x}" y1="{legend_y - 5}" x2="{x + 28}" y2="{legend_y - 5}" stroke="{color}" stroke-width="3"/>')
        body.append(f'<text x="{x + 36}" y="{legend_y}" class="legend">{html.escape(series.trace)}</text>')

    body.append(f'<text x="{left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis">{html.escape(data.x_trace)}</text>')
    body.append(f'<text x="22" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis" transform="rotate(-90 22 {top + plot_height / 2:.2f})">signal</text>')
    body.append("</svg>")
    return "\n".join(body)


def _range(values: list[float]) -> tuple[float, float]:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return 0.0, 1.0
    minimum = min(finite)
    maximum = max(finite)
    if minimum == maximum:
        padding = abs(minimum) * 0.05 or 1.0
        return minimum - padding, maximum + padding
    padding = (maximum - minimum) * 0.05
    return minimum - padding, maximum + padding


def _ticks(minimum: float, maximum: float, count: int) -> list[float]:
    if count <= 1:
        return [minimum]
    step = (maximum - minimum) / (count - 1)
    return [minimum + index * step for index in range(count)]


def _format_number(value: float) -> str:
    if value == 0:
        return "0"
    absolute = abs(value)
    if absolute >= 1000 or absolute < 0.001:
        return f"{value:.3g}"
    return f"{value:.4g}"


def _sample_step(values: list[float]) -> float:
    deltas = [b - a for a, b in zip(values, values[1:], strict=False) if b > a]
    if not deltas:
        raise ValueError("FFT x-axis must be monotonically increasing")
    average = sum(deltas) / len(deltas)
    if average <= 0:
        raise ValueError("FFT sample step must be positive")
    return average


def _largest_power_of_two(value: int) -> int:
    result = 1
    while result * 2 <= value:
        result *= 2
    return result


def _hann_window(count: int) -> list[float]:
    if count == 1:
        return [1.0]
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * index / (count - 1)) for index in range(count)]


def _safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-._")
    return token or "trace"
