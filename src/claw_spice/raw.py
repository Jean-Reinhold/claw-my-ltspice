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


def _ascii_raw_values(path: Path, trace: str) -> list[float]:
    text = path.read_text(errors="replace")
    names = _ascii_raw_trace_names(path)
    if trace not in names:
        raise ValueError(f"trace '{trace}' not found in {path}")
    index = names.index(trace)

    values_section = text.split("Values:", 1)
    if len(values_section) != 2:
        return []
    values: list[float] = []
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
            values.append(pending[index])
            pending = []
    return values
