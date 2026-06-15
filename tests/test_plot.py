from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.plot import (
    ReferenceLine,
    plot_raw_fft,
    plot_raw_traces,
    plot_waveform_data,
    safe_fft_stem,
    safe_plot_stem,
)
from claw_spice.raw import WaveformData, WaveformSeries


FIXTURES = Path(__file__).parent / "fixtures"


class PlotTests(unittest.TestCase):
    def test_safe_plot_stem_sanitizes_trace_names(self) -> None:
        self.assertEqual(safe_plot_stem("runs/latest/rc.raw", ["V(out)"]), "rc_V-out")
        self.assertEqual(safe_fft_stem("runs/latest/rc.raw", "V(out)"), "rc_fft_V-out")

    def test_plot_raw_trace_writes_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "plot.svg"
            svg, png = plot_raw_traces(FIXTURES / "ascii.raw", ["V(out)"], output, title="RC output")

            text = svg.read_text()
            self.assertEqual(svg, output)
            self.assertIsNone(png)
            self.assertIn("<svg", text)
            self.assertIn("<title>RC output</title>", text)
            self.assertIn("<desc>Waveform plot", text)
            self.assertIn("RC output", text)
            self.assertIn("V(out)", text)

    def test_plot_raw_fft_writes_svg(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp) / "wave.raw"
            raw.write_text(
                "\n".join(
                    [
                        "Title: FFT fixture",
                        "Plotname: Transient Analysis",
                        "Flags: real forward",
                        "No. Variables: 2",
                        "No. Points: 8",
                        "Variables:",
                        "        0       time    time",
                        "        1       V(out)  voltage",
                        "Values:",
                        "0       0",
                        "        0",
                        "1       0.001",
                        "        1",
                        "2       0.002",
                        "        0",
                        "3       0.003",
                        "        -1",
                        "4       0.004",
                        "        0",
                        "5       0.005",
                        "        1",
                        "6       0.006",
                        "        0",
                        "7       0.007",
                        "        -1",
                    ]
                )
            )
            output = Path(temp) / "fft.svg"
            svg, png = plot_raw_fft(raw, "V(out)", output, title="FFT output")

            text = svg.read_text()
            self.assertEqual(svg, output)
            self.assertIsNone(png)
            self.assertIn("<svg", text)
            self.assertIn("FFT output", text)
            self.assertIn("frequency (Hz)", text)

    def test_plot_waveform_data_writes_reference_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "plot.svg"
            svg, _png = plot_waveform_data(
                WaveformData("time", [0.0, 1.0], [WaveformSeries("V(out)", [0.0, 1.0])]),
                output,
                title="Threshold plot",
                reference_lines=(ReferenceLine(0.5, "trip"),),
            )

            text = svg.read_text()
            self.assertIn("reference", text)
            self.assertIn("trip", text)


if __name__ == "__main__":
    unittest.main()
