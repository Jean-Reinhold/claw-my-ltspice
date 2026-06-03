from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


MEAS_VALUE_RE = re.compile(r"^\s*([^:\s]+)\s*[:=]\s*(.*)$", re.IGNORECASE)
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass(frozen=True)
class Measurement:
    name: str
    value: float | None
    raw: str
    status: str


@dataclass(frozen=True)
class LogSummary:
    path: str
    measurements: list[Measurement]
    warnings: list[str]
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors and all(item.status == "pass" for item in self.measurements)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def _extract_value(raw: str) -> float | None:
    if "fail" in raw.lower():
        return None
    at_match = re.search(r"\bAT\s+" + NUMBER_RE.pattern, raw, re.IGNORECASE)
    if at_match:
        number = NUMBER_RE.search(at_match.group(0))
        return float(number.group(0)) if number else None
    equals_match = re.search(r"=\s*(" + NUMBER_RE.pattern + r")", raw)
    if equals_match:
        return float(equals_match.group(1))
    number = NUMBER_RE.search(raw)
    return float(number.group(0)) if number else None


def parse_log(path: str | Path) -> LogSummary:
    log_path = Path(path)
    text = log_path.read_text(errors="replace")
    measurements: list[Measurement] = []
    warnings: list[str] = []
    errors: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            continue
        if "warning" in lower:
            warnings.append(stripped)
        if "error" in lower or "fatal" in lower:
            errors.append(stripped)

        match = MEAS_VALUE_RE.match(stripped)
        if not match:
            continue
        name, raw = match.groups()
        if lower.startswith(("warning", "error", "fatal")):
            continue
        if any(token in lower for token in ("total elapsed", "tnom", "temp")):
            continue
        # LTspice .meas lines commonly contain name: value, name: expr=value, or FAIL.
        if "fail" in lower or "=" in raw or NUMBER_RE.search(raw):
            value = _extract_value(raw)
            measurements.append(
                Measurement(
                    name=name,
                    value=value,
                    raw=stripped,
                    status="fail" if "fail" in lower else "pass",
                )
            )

    return LogSummary(
        path=str(log_path),
        measurements=measurements,
        warnings=warnings,
        errors=errors,
    )


def format_log_summary(summary: LogSummary) -> str:
    lines = [f"Log: {summary.path}", f"Status: {'PASS' if summary.ok else 'FAIL'}"]
    lines.append("")
    lines.append("Measurements:")
    if summary.measurements:
        for measurement in summary.measurements:
            value = "n/a" if measurement.value is None else f"{measurement.value:g}"
            lines.append(f"- {measurement.name}: {value} ({measurement.status})")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Warnings:")
    lines.extend(f"- {warning}" for warning in summary.warnings) if summary.warnings else lines.append(
        "- none"
    )
    lines.append("")
    lines.append("Errors:")
    lines.extend(f"- {error}" for error in summary.errors) if summary.errors else lines.append("- none")
    return "\n".join(lines)
