from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.render import render_asc_to_svg, terminal_preview


EXAMPLE_ASC = Path("examples/transient/rc-step/rc_step.asc")


class RenderTests(unittest.TestCase):
    def test_fallback_svg_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schematic.svg"
            result = render_asc_to_svg(EXAMPLE_ASC, output)

            self.assertEqual(result, output)
            self.assertIn("<svg", output.read_text())
            self.assertIn("voltage", output.read_text())

    def test_terminal_preview_degrades_without_chafa(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            svg = Path(temp) / "schematic.svg"
            svg.write_text("<svg></svg>")
            text = terminal_preview(svg)

            self.assertIsInstance(text, str)
            self.assertTrue(text)


if __name__ == "__main__":
    unittest.main()
