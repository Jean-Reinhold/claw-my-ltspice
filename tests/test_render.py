from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from claw_spice.render import _normalize_power_flag_text, _render_with_ltspice_to_svg_package, render_asc_to_svg, terminal_preview


EXAMPLE_ASC = Path("examples/transient/rc-step/rc_step.asc")
RENDERED_SVG = '<svg><g s:type="res"></g><line /><line /><line /></svg>'
class RenderTests(unittest.TestCase):
    def test_render_requires_real_renderer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"

            with mock.patch("claw_spice.render.shutil.which", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "ltspice_to_svg is required"):
                    render_asc_to_svg(EXAMPLE_ASC, output)

    def test_render_uses_renderer_stdout_when_no_file_is_produced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type("Completed", (), {"returncode": 0, "stdout": RENDERED_SVG, "stderr": ""})()

            with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                with mock.patch("claw_spice.render.subprocess.run", return_value=completed):
                    result = render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertEqual(result, output)
            self.assertEqual(output.read_text(), RENDERED_SVG)

    def test_render_rejects_flag_only_svg_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type(
                "Completed",
                (),
                {"returncode": 0, "stdout": "<svg><text>in</text><text>out</text></svg>", "stderr": ""},
            )()

            with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                with mock.patch("claw_spice.render.subprocess.run", return_value=completed):
                    with self.assertRaisesRegex(RuntimeError, "rendered no component symbols"):
                        render_asc_to_svg(EXAMPLE_ASC, output)

    def test_render_passes_absolute_source_path_to_renderer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type("Completed", (), {"returncode": 0, "stdout": RENDERED_SVG, "stderr": ""})()

            with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                with mock.patch("claw_spice.render.subprocess.run", return_value=completed) as run:
                    render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertTrue(Path(run.call_args.args[0][-1]).is_absolute())

    def test_render_passes_explicit_ltspice_library(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type("Completed", (), {"returncode": 0, "stdout": RENDERED_SVG, "stderr": ""})()

            with mock.patch.dict(os.environ, {"LTSPICE_LIB_PATH": "/opt/ltspice/lib/sym"}):
                with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                    with mock.patch("claw_spice.render.subprocess.run", return_value=completed) as run:
                        render_asc_to_svg(EXAMPLE_ASC, output)

            command = run.call_args.args[0]
            self.assertIn("--ltspice-lib", command)
            self.assertIn("/opt/ltspice/lib/sym", command)

    def test_render_retries_next_library_on_symbol_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            failed = type(
                "Completed",
                (),
                {"returncode": 1, "stdout": "", "stderr": "Symbol definition not found: vendor"},
            )()
            succeeded = type("Completed", (), {"returncode": 0, "stdout": RENDERED_SVG, "stderr": ""})()

            with mock.patch("claw_spice.render._ltspice_library_paths", return_value=["/bundled", "/official"]):
                with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                    with mock.patch(
                        "claw_spice.render.subprocess.run", side_effect=[failed, succeeded]
                    ) as run:
                        result = render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertEqual(result, output)
            self.assertEqual(output.read_text(), RENDERED_SVG)
            self.assertEqual(run.call_count, 2)
            self.assertIn("/official", run.call_args.args[0])

    def test_render_uses_package_adapter_for_linux_cli_bug(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type(
                "Completed",
                (),
                {"returncode": 1, "stdout": "", "stderr": "OSError: Unsupported operating system: Linux"},
            )()

            with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                with mock.patch("claw_spice.render.subprocess.run", return_value=completed):
                    with mock.patch(
                        "claw_spice.render._render_with_ltspice_to_svg_package", return_value=output
                    ) as render_package:
                        result = render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertEqual(result, output)
            render_package.assert_called_once()

    def test_package_adapter_rejects_missing_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asc = root / "missing.asc"
            asc.write_text("Version 4\nSHEET 1 200 200\nSYMBOL not-a-symbol 0 0 R0\n")

            class FakeParser:
                def __init__(self, _source: str, lib_path: str | None = None) -> None:
                    self.lib_path = lib_path

                def parse(self) -> dict[str, object]:
                    return {
                        "schematic": {"symbols": [{"symbol_name": "not-a-symbol"}]},
                        "symbols": {},
                    }

            parser_module = types.ModuleType("src.parsers.schematic_parser")
            parser_module.SchematicParser = FakeParser
            config_module = types.ModuleType("src.renderers.rendering_config")
            config_module.RenderingConfig = object
            renderer_module = types.ModuleType("src.renderers.svg_renderer")
            renderer_module.SVGRenderer = object
            modules = {
                "src": types.ModuleType("src"),
                "src.parsers": types.ModuleType("src.parsers"),
                "src.parsers.schematic_parser": parser_module,
                "src.renderers": types.ModuleType("src.renderers"),
                "src.renderers.rendering_config": config_module,
                "src.renderers.svg_renderer": renderer_module,
            }
            modules["src"].__path__ = []
            modules["src.parsers"].__path__ = []
            modules["src.renderers"].__path__ = []

            with mock.patch.dict(sys.modules, modules):
                with self.assertRaisesRegex(RuntimeError, "could not resolve symbol definitions"):
                    _render_with_ltspice_to_svg_package(asc, root / "missing.svg", None)

    def test_terminal_preview_degrades_without_chafa(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            svg = Path(temp) / "schematic.svg"
            svg.write_text("<svg></svg>")
            text = terminal_preview(svg)

            self.assertIsInstance(text, str)
            self.assertTrue(text)

    def test_power_flag_text_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            svg = Path(temp) / "schematic.svg"
            svg.write_text(
                '<svg><text font-family="Arial" font-size="24.0px">vcc</text>'
                '<text font-family="Arial" font-size="24.0px">out</text></svg>'
            )

            _normalize_power_flag_text(svg)

            text = svg.read_text()
            self.assertIn('font-size="12.0px">VCC</text>', text)
            self.assertIn('font-size="24.0px">out</text>', text)


if __name__ == "__main__":
    unittest.main()
