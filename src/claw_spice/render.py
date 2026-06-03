from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def render_asc_to_svg(asc_path: str | Path, output: str | Path | None = None) -> Path:
    source = Path(asc_path)
    if output is None:
        output_path = source.with_suffix(".svg")
    else:
        output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = shutil.which("ltspice_to_svg") or shutil.which("ltspice-to-svg")
    if not command:
        raise RuntimeError(
            "ltspice_to_svg is required for schematic rendering. "
            "Run through ./claw-spice after building the Docker image, or use "
            "an environment with the ltspice-to-svg package installed."
        )

    renderer_command = [command]
    ltspice_lib = os.environ.get("LTSPICE_LIB_PATH")
    if not ltspice_lib:
        docker_ltspice_lib = Path("/opt/ltspice/lib/sym")
        if docker_ltspice_lib.exists():
            ltspice_lib = str(docker_ltspice_lib)
    if ltspice_lib:
        renderer_command.extend(["--ltspice-lib", ltspice_lib])
    renderer_command.append(str(source))

    result = subprocess.run(
        renderer_command,
        cwd=str(source.parent),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no renderer output"
        raise RuntimeError(f"ltspice_to_svg failed for {source}: {detail}")

    produced = source.with_suffix(".svg")
    if produced.exists():
        if produced != output_path:
            output_path.write_bytes(produced.read_bytes())
        return output_path
    if result.stdout.lstrip().startswith("<svg"):
        output_path.write_text(result.stdout)
        return output_path
    raise RuntimeError(f"ltspice_to_svg did not produce an SVG for {source}")


def terminal_preview(svg_path: str | Path) -> str:
    source = Path(svg_path)
    chafa = shutil.which("chafa")
    if chafa:
        result = subprocess.run(
            [chafa, "--symbols", "block", str(source)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    return f"Terminal preview unavailable. SVG generated at: {source}\n"


def render_png(svg_path: str | Path, output: str | Path | None = None) -> Path | None:
    source = Path(svg_path)
    output_path = Path(output) if output else source.with_suffix(".png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for command, args in (
        ("rsvg-convert", ["-o", str(output_path), str(source)]),
        ("resvg", [str(source), str(output_path)]),
    ):
        executable = shutil.which(command)
        if not executable:
            continue
        result = subprocess.run([executable, *args], check=False)
        if result.returncode == 0 and output_path.exists():
            return output_path
    return None
