from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean


@dataclass(frozen=True)
class TraceStats:
    trace: str
    count: int
    minimum: float
    maximum: float
    mean: float
    peak_to_peak: float

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)


@dataclass(frozen=True)
class WaveformSeries:
    trace: str
    values: list[float]


@dataclass(frozen=True)
class WaveformData:
    x_trace: str
    x_values: list[float]
    series: list[WaveformSeries]


def trace_names(path: str | Path) -> list[str]:
    raw_path = Path(path)
    try:
        from spicelib import RawRead  # type: ignore

        raw = RawRead(str(raw_path))
        return list(raw.get_trace_names())
    except Exception:
        return _ascii_raw_trace_names(raw_path)


def stats(path: str | Path, trace: str) -> TraceStats:
    raw_path = Path(path)
    try:
        from spicelib import RawRead  # type: ignore

        raw = RawRead(str(raw_path))
        values = [float(value) for value in raw.get_trace(trace).get_wave()]
    except Exception:
        values = _ascii_raw_values(raw_path, trace)

    if not values:
        raise ValueError(f"trace '{trace}' has no values in {raw_path}")
    minimum = min(values)
    maximum = max(values)
    return TraceStats(
        trace=trace,
        count=len(values),
        minimum=minimum,
        maximum=maximum,
        mean=fmean(values),
        peak_to_peak=maximum - minimum,
    )


def waveform_data(path: str | Path, traces: list[str] | tuple[str, ...], x_trace: str | None = None) -> WaveformData:
    raw_path = Path(path)
    try:
        names, values_by_trace = _spicelib_raw_table(raw_path)
    except Exception:
        names, values_by_trace = _ascii_raw_table(raw_path)

    if not names:
        raise ValueError(f"no traces found in {raw_path}")
    selected_x = x_trace or ("time" if "time" in names else names[0])
    if selected_x not in values_by_trace:
        raise ValueError(f"x trace '{selected_x}' not found in {raw_path}")
    selected_traces = list(traces) or [name for name in names if name != selected_x]
    if not selected_traces:
        raise ValueError(f"no signal traces selected in {raw_path}")

    series: list[WaveformSeries] = []
    for trace in selected_traces:
        if trace not in values_by_trace:
            raise ValueError(f"trace '{trace}' not found in {raw_path}")
        series.append(WaveformSeries(trace, values_by_trace[trace]))
    return WaveformData(selected_x, values_by_trace[selected_x], series)


def _spicelib_raw_table(path: Path) -> tuple[list[str], dict[str, list[float]]]:
    from spicelib import RawRead  # type: ignore

    raw = RawRead(str(path))
    names = list(raw.get_trace_names())
    return names, {name: [_as_float(value) for value in raw.get_trace(name).get_wave()] for name in names}


def _ascii_raw_trace_names(path: Path) -> list[str]:
    text = path.read_text(errors="replace")
    names: list[str] = []
    in_variables = False
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower == "variables:":
            in_variables = True
            continue
        if lower == "values:":
            break
        if in_variables and stripped:
            parts = stripped.split()
            if len(parts) >= 2 and parts[0].isdigit():
                names.append(parts[1])
    return names


def _ascii_raw_table(path: Path) -> tuple[list[str], dict[str, list[float]]]:
    text = path.read_text(errors="replace")
    names = _ascii_raw_trace_names(path)
    values_by_trace: dict[str, list[float]] = {name: [] for name in names}
    values_section = text.split("Values:", 1)
    if len(values_section) != 2:
        return names, values_by_trace

    pending: list[float] = []
    for line in values_section[1].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) == 2 and parts[0].isdigit():
            pending = [float(parts[1])]
        else:
            pending.append(float(parts[-1]))
        if len(pending) == len(names):
            for name, value in zip(names, pending, strict=False):
                values_by_trace[name].append(value)
            pending = []
    return names, values_by_trace


def _ascii_raw_values(path: Path, trace: str) -> list[float]:
    _names, values_by_trace = _ascii_raw_table(path)
    if trace not in values_by_trace:
        raise ValueError(f"trace '{trace}' not found in {path}")
    return values_by_trace[trace]


def _as_float(value: object) -> float:
    if isinstance(value, complex):
        return abs(value)
    return float(value)  # type: ignore[arg-type]
