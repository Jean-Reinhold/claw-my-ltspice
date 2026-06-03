from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.plot import plot_raw_traces, safe_plot_stem


FIXTURES = Path(__file__).parent / "fixtures"


class PlotTests(unittest.TestCase):
    def test_safe_plot_stem_sanitizes_trace_names(self) -> None:
        self.assertEqual(safe_plot_stem("runs/latest/rc.raw", ["V(out)"]), "rc_V-out")

    def test_plot_raw_trace_writes_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "plot.svg"
            svg, png = plot_raw_traces(FIXTURES / "ascii.raw", ["V(out)"], output, title="RC output")

            text = svg.read_text()
            self.assertEqual(svg, output)
            self.assertIsNone(png)
            self.assertIn("<svg", text)
            self.assertIn("RC output", text)
            self.assertIn("V(out)", text)


if __name__ == "__main__":
    unittest.main()
