from __future__ import annotations

import os
import signal
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SimulationResult:
    input_path: Path
    command: list[str]
    returncode: int
    log_path: Path | None
    raw_path: Path | None
    stdout: str
    stderr: str

    @property
    def missing_artifacts(self) -> tuple[str, ...]:
        missing = []
        if self.log_path is None:
            missing.append("log")
        if self.raw_path is None:
            missing.append("raw")
        return tuple(missing)

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.missing_artifacts


def ltspice_command() -> list[str]:
    configured = os.environ.get("LTSPICE_CMD")
    if configured:
        return configured.split()
    wrapper = shutil.which("ltspice")
    if wrapper:
        return [wrapper]
    exe = os.environ.get("LTSPICE_EXE")
    if exe:
        return ["wine", exe]
    default_exe = Path(os.environ.get("WINEPREFIX", "/tmp/wine-prefix")) / "drive_c/Program Files/ADI/LTspice/LTspice.exe"
    return ["wine", str(default_exe)]


def wine_path(path: Path) -> str:
    resolved = path.resolve()
    return "Z:" + resolved.as_posix()


def simulation_command(input_path: str | Path) -> list[str]:
    source = Path(input_path).resolve()
    base_command = ltspice_command()
    if source.suffix.lower() == ".asc":
        return [*base_command, "-Run", "-b", wine_path(source)]
    return [*base_command, "-b", wine_path(source)]


def run_simulation(input_path: str | Path, timeout: int = 300) -> SimulationResult:
    source = Path(input_path).resolve()
    command = simulation_command(source)
    result = _run_ltspice_command(command, source.parent, timeout)
    log_path = source.with_suffix(".log") if source.with_suffix(".log").exists() else None
    raw_path = source.with_suffix(".raw") if source.with_suffix(".raw").exists() else None
    return SimulationResult(source, command, result.returncode, log_path, raw_path, result.stdout, result.stderr)


def create_netlist(asc_path: str | Path, timeout: int = 120) -> Path:
    source = Path(asc_path).resolve()
    command = [*ltspice_command(), "-netlist", wine_path(source)]
    result = _run_ltspice_command(command, source.parent, timeout)
    output = source.with_suffix(".net")
    if result.returncode != 0 or not output.exists():
        raise RuntimeError(
            "LTspice netlist export failed\n"
            f"command: {' '.join(command)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return output


def _run_ltspice_command(command: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _kill_process_group(process.pid)
        stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _kill_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
