from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def find_workspace(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
            return candidate
    return current


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path
    runs: Path
    latest: Path


def workspace_paths(root: Path | None = None) -> WorkspacePaths:
    resolved = (root or find_workspace()).resolve()
    runs = resolved / "runs"
    latest = runs / "latest"
    return WorkspacePaths(root=resolved, runs=runs, latest=latest)


def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def safe_output_path(path: str | Path | None, default: Path) -> Path:
    output = Path(path) if path else default
    if not output.is_absolute():
        output = Path.cwd() / output
    ensure_parent(output)
    return output
