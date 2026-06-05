from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


def render_asc_to_svg(asc_path: str | Path, output: str | Path | None = None) -> Path:
    source = Path(asc_path).resolve()
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

    errors: list[str] = []
    for ltspice_lib in _ltspice_library_paths():
        try:
            return _run_renderer_command(command, source, output_path, ltspice_lib)
        except RuntimeError as exc:
            detail = str(exc)
            errors.append(detail)
            if not _is_symbol_resolution_error(detail):
                raise
    raise RuntimeError(errors[-1] if errors else f"ltspice_to_svg did not run for {source}")


def _run_renderer_command(
    command: str, source: Path, output_path: Path, ltspice_lib: str | None
) -> Path:
    renderer_command = [command]
    if ltspice_lib:
        renderer_command.extend(["--ltspice-lib", ltspice_lib])
    renderer_command.append(str(source))

    env = os.environ.copy()
    if ltspice_lib:
        env["LTSPICE_LIB_PATH"] = ltspice_lib

    produced = source.with_suffix(".svg")
    previous_mtime = produced.stat().st_mtime_ns if produced.exists() else None
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

    if result.stdout.lstrip().startswith("<svg"):
        output_path.write_text(result.stdout)
        return _finalize_svg(output_path, output_path, source)
    if produced.exists():
        if previous_mtime == produced.stat().st_mtime_ns:
            raise RuntimeError(f"ltspice_to_svg did not produce a fresh SVG for {source}")
        return _finalize_svg(produced, output_path, source)
    raise RuntimeError(f"ltspice_to_svg did not produce an SVG for {source}")


def _ltspice_library_paths() -> list[str | None]:
    paths: list[str | None] = []

    def append(path: str | None) -> None:
        if path and path not in paths:
            paths.append(path)

    ltspice_lib = os.environ.get("LTSPICE_LIB_PATH")
    append(ltspice_lib)

    bundled_symbols = Path(__file__).resolve().parent / "symbols"
    if bundled_symbols.exists():
        append(str(bundled_symbols))

    docker_ltspice_lib = Path("/opt/ltspice/lib/sym")
    if docker_ltspice_lib.exists():
        append(str(docker_ltspice_lib))
    paths.append(None)
    return paths


def _is_symbol_resolution_error(detail: str) -> bool:
    return "could not resolve symbol definitions" in detail or "Symbol definition not found" in detail


def _render_with_ltspice_to_svg_package(source: Path, output_path: Path, ltspice_lib: str | None) -> Path:
    # ltspice-to-svg 0.2.0's CLI rejects Linux, but its parser/renderer works
    # when a symbol library path is provided explicitly.
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
        parser = SchematicParser(str(source), lib_path=ltspice_lib)
        data = parser.parse()
        missing_symbols = sorted(
            {
                symbol["symbol_name"]
                for symbol in data["schematic"].get("symbols", [])
                if symbol["symbol_name"] not in data["symbols"]
            }
        )
        if missing_symbols:
            raise RuntimeError(
                f"ltspice-to-svg could not resolve symbol definitions: {', '.join(missing_symbols)}"
            )
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
        return _finalize_svg(produced, output_path, source)
    raise RuntimeError(f"ltspice-to-svg package did not produce an SVG for {source}")


def _finalize_svg(produced: Path, output_path: Path, source: Path) -> Path:
    if produced != output_path:
        output_path.write_bytes(produced.read_bytes())
    _normalize_power_flag_text(output_path)
    _pad_svg_viewbox(output_path)
    _validate_rendered_svg(source, output_path)
    return output_path


def _normalize_power_flag_text(svg_path: Path) -> None:
    text = svg_path.read_text()

    def replace(match: re.Match[str]) -> str:
        label = match.group(3).upper()
        return f'{match.group(1)}12.0px{match.group(2)}{label}{match.group(4)}'

    text = re.sub(
        r'(<text\b(?=[^>]*font-size="24\.0px")[^>]*font-size=")24\.0px("[^>]*>)(vcc|vee)(</text>)',
        replace,
        text,
        flags=re.IGNORECASE,
    )
    svg_path.write_text(text)


def _validate_rendered_svg(source: Path, svg_path: Path) -> None:
    asc = source.read_text()
    svg = svg_path.read_text()
    symbol_count = sum(1 for line in asc.splitlines() if line.startswith("SYMBOL "))
    wire_count = sum(1 for line in asc.splitlines() if line.startswith("WIRE "))
    rendered_symbols = svg.count("s:type=")
    rendered_wires = svg.count("<line ")

    if symbol_count and rendered_symbols == 0:
        raise RuntimeError(
            f"ltspice_to_svg rendered no component symbols for {source}; "
            "check symbol library resolution instead of publishing a flag-only schematic."
        )
    if wire_count and rendered_wires < wire_count:
        raise RuntimeError(
            f"ltspice_to_svg rendered too few schematic wires for {source}: "
            f"expected at least {wire_count}, saw {rendered_wires}."
        )


def _pad_svg_viewbox(svg_path: Path, padding: float = 192.0) -> None:
    text = svg_path.read_text()
    match = re.search(r'viewBox="([-0-9.]+) ([-0-9.]+) ([-0-9.]+) ([-0-9.]+)"', text)
    if not match:
        return

    x, y, width, height = (float(value) for value in match.groups())
    padded = (x - padding, y - padding, width + padding * 2, height + padding * 2)
    viewbox = f'viewBox="{padded[0]:.1f} {padded[1]:.1f} {padded[2]:.1f} {padded[3]:.1f}"'
    text = text[: match.start()] + viewbox + text[match.end() :]

    if "data-claw-background" not in text:
        background = (
            f'  <rect data-claw-background="true" fill="white" height="{padded[3]:.1f}" '
            f'width="{padded[2]:.1f}" x="{padded[0]:.1f}" y="{padded[1]:.1f}"/>\n'
        )
        text = text.replace("  <defs/>\n", "  <defs/>\n" + background, 1)
    svg_path.write_text(text)


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
