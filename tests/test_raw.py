from __future__ import annotations

import unittest
from pathlib import Path

from claw_spice.raw import stats, trace_names, waveform_data


FIXTURES = Path(__file__).parent / "fixtures"


class RawParsingTests(unittest.TestCase):
    def test_ascii_raw_trace_names(self) -> None:
        self.assertEqual(trace_names(FIXTURES / "ascii.raw"), ["time", "V(out)"])

    def test_ascii_raw_stats(self) -> None:
        result = stats(FIXTURES / "ascii.raw", "V(out)")

        self.assertEqual(result.count, 3)
        self.assertAlmostEqual(result.minimum, 0.0)
        self.assertAlmostEqual(result.maximum, 4.32)
        self.assertAlmostEqual(result.peak_to_peak, 4.32)

    def test_ascii_waveform_data(self) -> None:
        result = waveform_data(FIXTURES / "ascii.raw", ["V(out)"])

        self.assertEqual(result.x_trace, "time")
        self.assertEqual(result.x_values, [0.0, 0.001, 0.002])
        self.assertEqual(result.series[0].trace, "V(out)")
        self.assertEqual(result.series[0].values, [0.0, 3.16, 4.32])


if __name__ == "__main__":
    unittest.main()
