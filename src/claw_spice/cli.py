from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from claw_spice import __version__
from claw_spice.ir import Circuit
from claw_spice.logs import format_log_summary, parse_log
from claw_spice.paths import safe_output_path, workspace_paths
from claw_spice.raw import stats as raw_stats
from claw_spice.raw import trace_names
from claw_spice.render import render_asc_to_svg, render_png, terminal_preview
from claw_spice.simulate import create_netlist, run_simulation


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 2
    try:
        return int(args.handler(args) or 0)
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI should present concise failures.
        if getattr(args, "debug", False):
            raise
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claw-spice")
    parser.add_argument("--version", action="version", version=f"claw-spice {__version__}")
    parser.add_argument("--debug", action="store_true", help="raise full tracebacks")
    sub = parser.add_subparsers(dest="command")

    doctor = sub.add_parser("doctor", help="check container/runtime setup")
    doctor.add_argument("--json", action="store_true", dest="as_json")
    doctor.set_defaults(handler=cmd_doctor)

    build = sub.add_parser("build", help="container build placeholder when run inside Docker")
    build.set_defaults(handler=lambda _args: print("Build is handled by the host wrapper/docker compose."))

    shell = sub.add_parser("shell", help="print shell hint")
    shell.set_defaults(handler=lambda _args: print("Use the host wrapper: ./claw-spice shell"))

    test = sub.add_parser("test", help="run unit and integration tests")
    test.add_argument("--pattern", default="test_*.py")
    test.set_defaults(handler=cmd_test)

    sim = sub.add_parser("sim", help="LTspice simulation commands")
    sim_sub = sim.add_subparsers(dest="sim_command", required=True)
    sim_run = sim_sub.add_parser("run", help="run LTspice on .cir/.net/.asc")
    sim_run.add_argument("input")
    sim_run.add_argument("--timeout", type=int, default=300)
    sim_run.add_argument("--json", action="store_true", dest="as_json")
    sim_run.set_defaults(handler=cmd_sim_run)
    sim_netlist = sim_sub.add_parser("netlist", help="export .asc to .net using LTspice")
    sim_netlist.add_argument("input")
    sim_netlist.add_argument("--timeout", type=int, default=120)
    sim_netlist.set_defaults(handler=cmd_sim_netlist)

    render = sub.add_parser("render", help="render LTspice .asc to SVG/PNG/terminal text")
    render.add_argument("input")
    render.add_argument("--output", "-o")
    render.add_argument("--png", action="store_true")
    render.add_argument("--terminal-text")
    render.add_argument("--print-svg-path", action="store_true")
    render.set_defaults(handler=cmd_render)

    show = sub.add_parser("show", help="render a schematic and print/preview the output")
    show.add_argument("input")
    show.add_argument("--terminal", action="store_true")
    show.add_argument("--output", "-o")
    show.add_argument("--print-svg-path", action="store_true")
    show.set_defaults(handler=cmd_show)

    log = sub.add_parser("log", help="LTspice log commands")
    log_sub = log.add_subparsers(dest="log_command", required=True)
    log_summary = log_sub.add_parser("summary", help="summarize LTspice .log measurements")
    log_summary.add_argument("input")
    log_summary.add_argument("--json", action="store_true", dest="as_json")
    log_summary.set_defaults(handler=cmd_log_summary)

    raw = sub.add_parser("raw", help="LTspice raw waveform commands")
    raw_sub = raw.add_subparsers(dest="raw_command", required=True)
    raw_traces = raw_sub.add_parser("traces", help="list trace names")
    raw_traces.add_argument("input")
    raw_traces.add_argument("--json", action="store_true", dest="as_json")
    raw_traces.set_defaults(handler=cmd_raw_traces)
    raw_stats_cmd = raw_sub.add_parser("stats", help="show simple trace statistics")
    raw_stats_cmd.add_argument("input")
    raw_stats_cmd.add_argument("trace")
    raw_stats_cmd.add_argument("--json", action="store_true", dest="as_json")
    raw_stats_cmd.set_defaults(handler=cmd_raw_stats)

    code = sub.add_parser("code", help="code-to-circuit commands")
    code_sub = code.add_subparsers(dest="code_command", required=True)
    code_build = code_sub.add_parser("build", help="run a Python circuit generator")
    code_build.add_argument("input")
    code_build.add_argument("--output-dir", default=None)
    code_build.add_argument("--json", action="store_true", dest="as_json")
    code_build.set_defaults(handler=cmd_code_build)

    examples = sub.add_parser("examples", help="example workflows")
    examples_sub = examples.add_subparsers(dest="examples_command", required=True)
    examples_run = examples_sub.add_parser("run", help="generate/render examples and optionally simulate")
    examples_run.add_argument("--skip-sim", action="store_true")
    examples_run.set_defaults(handler=cmd_examples_run)
    examples_render = examples_sub.add_parser("render", help="render example schematics")
    examples_render.set_defaults(handler=cmd_examples_render)

    docs = sub.add_parser("docs", help="GitHub Pages documentation commands")
    docs_sub = docs.add_subparsers(dest="docs_command", required=True)
    docs_build = docs_sub.add_parser("build", help="build MkDocs site")
    docs_build.set_defaults(handler=lambda _args: cmd_docs(["build"]))
    docs_serve = docs_sub.add_parser("serve", help="serve MkDocs site")
    docs_serve.set_defaults(handler=lambda _args: cmd_docs(["serve", "-a", "0.0.0.0:8000"]))

    ci = sub.add_parser("ci", help="local CI parity commands")
    ci_sub = ci.add_subparsers(dest="ci_command", required=True)
    ci_smoke = ci_sub.add_parser("smoke", help="run tests and render examples without opening viewers")
    ci_smoke.set_defaults(handler=cmd_ci_smoke)
    ci_render = ci_sub.add_parser("render", help="render docs/example assets")
    ci_render.set_defaults(handler=cmd_examples_render)

    return parser


def cmd_doctor(args: argparse.Namespace) -> int:
    checks = {
        "python": sys.version.split()[0],
        "workspace": str(workspace_paths().root),
        "ltspice_wrapper": shutil.which("ltspice"),
        "wine": shutil.which("wine"),
        "xvfb": shutil.which("Xvfb"),
        "ltspice_to_svg": shutil.which("ltspice_to_svg") or shutil.which("ltspice-to-svg"),
        "chafa": shutil.which("chafa"),
        "rsvg_convert": shutil.which("rsvg-convert"),
        "resvg": shutil.which("resvg"),
        "mkdocs": shutil.which("mkdocs"),
    }
    if args.as_json:
        print(json.dumps(checks, indent=2))
        return 0
    print("claw-spice doctor")
    for name, value in checks.items():
        status = "PASS" if value else "MISS"
        print(f"{status:4} {name}: {value or 'not found'}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", args.pattern],
        check=False,
    ).returncode


def cmd_sim_run(args: argparse.Namespace) -> int:
    result = run_simulation(args.input, timeout=args.timeout)
    payload = {
        "input": str(result.input_path),
        "command": result.command,
        "returncode": result.returncode,
        "log": str(result.log_path) if result.log_path else None,
        "raw": str(result.raw_path) if result.raw_path else None,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Command: {' '.join(result.command)}")
        print(f"Return code: {result.returncode}")
        print(f"Log: {result.log_path or 'not produced'}")
        print(f"Raw: {result.raw_path or 'not produced'}")
    return result.returncode


def cmd_sim_netlist(args: argparse.Namespace) -> int:
    output = create_netlist(args.input, timeout=args.timeout)
    print(output)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    source = Path(args.input)
    default = workspace_paths().latest / f"{source.stem}.svg"
    output = safe_output_path(args.output, default)
    svg = render_asc_to_svg(source, output)
    if args.png:
        png = render_png(svg)
        if png:
            print(f"PNG: {png}")
    if args.terminal_text:
        text_path = safe_output_path(args.terminal_text, svg.with_suffix(".terminal.txt"))
        text_path.write_text(terminal_preview(svg))
        print(f"Terminal preview: {text_path}")
    print(svg if args.print_svg_path else f"SVG: {svg}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    source = Path(args.input)
    if source.suffix.lower() == ".svg":
        svg = source
    else:
        default = workspace_paths().latest / f"{source.stem}.svg"
        output = safe_output_path(args.output, default)
        svg = render_asc_to_svg(source, output)
    if args.terminal:
        print(terminal_preview(svg))
    print(svg if args.print_svg_path else f"SVG: {svg}")
    return 0


def cmd_log_summary(args: argparse.Namespace) -> int:
    summary = parse_log(args.input)
    print(summary.to_json() if args.as_json else format_log_summary(summary))
    return 0 if summary.ok else 1


def cmd_raw_traces(args: argparse.Namespace) -> int:
    names = trace_names(args.input)
    if args.as_json:
        print(json.dumps(names, indent=2))
    else:
        for name in names:
            print(name)
    return 0


def cmd_raw_stats(args: argparse.Namespace) -> int:
    result = raw_stats(args.input, args.trace)
    if args.as_json:
        print(result.to_json())
    else:
        print(f"Trace: {result.trace}")
        print(f"Count: {result.count}")
        print(f"Min: {result.minimum:g}")
        print(f"Max: {result.maximum:g}")
        print(f"Mean: {result.mean:g}")
        print(f"Peak-to-peak: {result.peak_to_peak:g}")
    return 0


def cmd_code_build(args: argparse.Namespace) -> int:
    script = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else script.parent / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    module = _load_module(script)
    if hasattr(module, "build"):
        result = module.build(output_dir)
    elif hasattr(module, "create_circuit"):
        circuit = module.create_circuit()
        result = _write_circuit_outputs(circuit, output_dir, script.stem)
    else:
        raise ValueError(f"{script} must define build(output_dir) or create_circuit()")
    payload = {key: str(value) for key, value in dict(result).items()} if isinstance(result, dict) else result
    print(json.dumps(payload, indent=2) if args.as_json else payload)
    return 0


def cmd_examples_run(args: argparse.Namespace) -> int:
    outputs = _build_rc_example()
    render_asc_to_svg(outputs["asc"], workspace_paths().latest / "rc_step.svg")
    skip = args.skip_sim or os.environ.get("CLAW_SPICE_SKIP_SIM") == "1" or not _has_ltspice_runtime()
    if skip:
        print("Examples generated/rendered. Simulation skipped.")
        return 0
    result = run_simulation(outputs["cir"])
    print(f"Simulation return code: {result.returncode}")
    return result.returncode


def cmd_examples_render(_args: argparse.Namespace) -> int:
    outputs = _build_rc_example()
    svg = render_asc_to_svg(outputs["asc"], workspace_paths().latest / "rc_step.svg")
    terminal_path = workspace_paths().latest / "rc_step.terminal.txt"
    terminal_path.parent.mkdir(parents=True, exist_ok=True)
    terminal_path.write_text(terminal_preview(svg))
    print(f"SVG: {svg}")
    print(f"Terminal preview: {terminal_path}")
    return 0


def cmd_docs(args: list[str]) -> int:
    mkdocs = shutil.which("mkdocs")
    if not mkdocs:
        raise RuntimeError("mkdocs is not installed in this environment")
    return subprocess.run([mkdocs, *args, "-f", "docs-site/mkdocs.yml"], check=False).returncode


def cmd_ci_smoke(args: argparse.Namespace) -> int:
    test_code = cmd_test(argparse.Namespace(pattern="test_*.py"))
    if test_code != 0:
        return test_code
    return cmd_examples_render(args)


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if not spec or not spec.loader:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def _write_circuit_outputs(circuit: Circuit, output_dir: Path, stem: str) -> dict[str, Path]:
    cir = circuit.write_netlist(output_dir / f"{stem}.cir")
    asc = circuit.write_asc(output_dir / f"{stem}.asc")
    return {"cir": cir, "asc": asc}


def _build_rc_example() -> dict[str, Path]:
    script = Path("examples/transient/rc-step/rc_step.py")
    module = _load_module(script.resolve())
    output_dir = workspace_paths().latest / "examples" / "rc-step"
    output_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(module, "build"):
        return {key: Path(value) for key, value in module.build(output_dir).items()}
    return _write_circuit_outputs(module.create_circuit(), output_dir, "rc_step")


def _has_ltspice_runtime() -> bool:
    return bool(shutil.which("ltspice") or shutil.which("wine") or os.environ.get("LTSPICE_CMD"))


if __name__ == "__main__":
    raise SystemExit(main())
