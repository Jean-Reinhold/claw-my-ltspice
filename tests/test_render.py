from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from claw_spice.render import render_asc_to_svg, terminal_preview


EXAMPLE_ASC = Path("examples/transient/rc-step/rc_step.asc")
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
            completed = type("Completed", (), {"returncode": 0, "stdout": "<svg>ok</svg>", "stderr": ""})()

            with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                with mock.patch("claw_spice.render.subprocess.run", return_value=completed):
                    result = render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertEqual(result, output)
            self.assertEqual(output.read_text(), "<svg>ok</svg>")

    def test_render_passes_explicit_ltspice_library(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            completed = type("Completed", (), {"returncode": 0, "stdout": "<svg>ok</svg>", "stderr": ""})()

            with mock.patch.dict(os.environ, {"LTSPICE_LIB_PATH": "/opt/ltspice/lib/sym"}):
                with mock.patch("claw_spice.render.shutil.which", return_value="ltspice_to_svg"):
                    with mock.patch("claw_spice.render.subprocess.run", return_value=completed) as run:
                        render_asc_to_svg(EXAMPLE_ASC, output)

            command = run.call_args.args[0]
            self.assertIn("--ltspice-lib", command)
            self.assertIn("/opt/ltspice/lib/sym", command)

    def test_terminal_preview_degrades_without_chafa(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            svg = Path(temp) / "schematic.svg"
            svg.write_text("<svg></svg>")
            text = terminal_preview(svg)

            self.assertIsInstance(text, str)
            self.assertTrue(text)


if __name__ == "__main__":
    unittest.main()
