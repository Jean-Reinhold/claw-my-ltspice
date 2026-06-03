from __future__ import annotations

import html
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
    if command:
        result = subprocess.run(
            [command, str(source)],
            cwd=str(source.parent),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        produced = source.with_suffix(".svg")
        if result.returncode == 0 and produced.exists():
            if produced != output_path:
                output_path.write_bytes(produced.read_bytes())
            return output_path

    output_path.write_text(_fallback_svg(source))
    return output_path


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


def _fallback_svg(path: Path) -> str:
    wires: list[tuple[int, int, int, int]] = []
    symbols: list[tuple[str, int, int, str]] = []
    flags: list[tuple[int, int, str]] = []
    texts: list[tuple[int, int, str]] = []
    current_symbol: tuple[str, int, int, str] | None = None

    for line in path.read_text(errors="replace").splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "WIRE" and len(parts) >= 5:
            wires.append(tuple(map(int, parts[1:5])))
        elif parts[0] == "SYMBOL" and len(parts) >= 5:
            current_symbol = (parts[1], int(parts[2]), int(parts[3]), parts[4])
            symbols.append(current_symbol)
        elif parts[0] == "FLAG" and len(parts) >= 4:
            flags.append((int(parts[1]), int(parts[2]), " ".join(parts[3:])))
        elif parts[0] == "TEXT" and len(parts) >= 6:
            texts.append((int(parts[1]), int(parts[2]), " ".join(parts[5:])))
        elif parts[0] == "SYMATTR" and len(parts) >= 3 and current_symbol:
            label = " ".join(parts[2:])
            texts.append((current_symbol[1], current_symbol[2] - 12, label))

    max_x = max([400, *[max(w[0], w[2]) for w in wires], *[s[1] + 120 for s in symbols]], default=400)
    max_y = max([240, *[max(w[1], w[3]) for w in wires], *[s[2] + 120 for s in symbols]], default=240)
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {max_x + 80} {max_y + 80}" width="{max_x + 80}" height="{max_y + 80}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        '<g stroke="#222" stroke-width="2" fill="none" stroke-linecap="round">',
    ]
    body.extend(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>' for x1, y1, x2, y2 in wires)
    for symbol, x, y, rotation in symbols:
        body.append(f'<rect x="{x}" y="{y}" width="72" height="48" rx="6" fill="#fff"/>')
        body.append("</g>")
        body.append(
            f'<text x="{x + 6}" y="{y + 28}" font-family="monospace" font-size="14" fill="#222">{html.escape(symbol)} {html.escape(rotation)}</text>'
        )
        body.append('<g stroke="#222" stroke-width="2" fill="none" stroke-linecap="round">')
    body.append("</g>")
    for x, y, label in flags:
        body.append(
            f'<text x="{x + 4}" y="{y - 4}" font-family="monospace" font-size="12" fill="#0b5394">{html.escape(label)}</text>'
        )
    for x, y, text in texts:
        body.append(
            f'<text x="{x}" y="{y}" font-family="monospace" font-size="12" fill="#444">{html.escape(text)}</text>'
        )
    body.append("</svg>")
    return "\n".join(body)
