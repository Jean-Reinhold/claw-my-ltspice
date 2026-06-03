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
    ltspice_lib = _ltspice_library_path()
    if ltspice_lib:
        renderer_command.extend(["--ltspice-lib", ltspice_lib])
    renderer_command.append(str(source))

    env = os.environ.copy()
    if ltspice_lib:
        env["LTSPICE_LIB_PATH"] = ltspice_lib

    result = subprocess.run(
        renderer_command,
        cwd=str(source.parent),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no renderer output"
        if "Unsupported operating system: Linux" in detail:
            return _render_with_ltspice_to_svg_package(source, output_path, ltspice_lib)
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


def _ltspice_library_path() -> str | None:
    ltspice_lib = os.environ.get("LTSPICE_LIB_PATH")
    if ltspice_lib:
        return ltspice_lib

    docker_ltspice_lib = Path("/opt/ltspice/lib/sym")
    if docker_ltspice_lib.exists():
        return str(docker_ltspice_lib)
    return None


def _render_with_ltspice_to_svg_package(source: Path, output_path: Path, ltspice_lib: str | None) -> Path:
    # ltspice-to-svg 0.2.0's CLI rejects Linux, but its parser/renderer works
    # when the Docker LTspice symbol path is provided explicitly.
    try:
        from src.parsers.schematic_parser import SchematicParser
        from src.renderers.rendering_config import RenderingConfig
        from src.renderers.svg_renderer import SVGRenderer
    except ImportError as exc:
        raise RuntimeError("ltspice-to-svg package internals are required for Linux schematic rendering") from exc

    previous_ltspice_lib = os.environ.get("LTSPICE_LIB_PATH")
    if ltspice_lib:
        os.environ["LTSPICE_LIB_PATH"] = ltspice_lib
    try:
        parser = SchematicParser(str(source))
        data = parser.parse()
        renderer = SVGRenderer(RenderingConfig())
        produced = source.with_suffix(".svg")

        renderer.load_schematic(data["schematic"], data["symbols"])
        renderer.create_drawing(str(produced))
        renderer.render_wires(1.5)
        renderer.render_symbols()
        renderer.render_texts()
        renderer.render_shapes()
        renderer.render_flags()
        renderer.save()
    finally:
        if previous_ltspice_lib is None:
            os.environ.pop("LTSPICE_LIB_PATH", None)
        else:
            os.environ["LTSPICE_LIB_PATH"] = previous_ltspice_lib

    if produced.exists():
        if produced != output_path:
            output_path.write_bytes(produced.read_bytes())
        return output_path
    raise RuntimeError(f"ltspice-to-svg package did not produce an SVG for {source}")


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
