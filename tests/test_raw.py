from __future__ import annotations

import unittest
from pathlib import Path

from claw_spice.raw import stats, trace_names


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


if __name__ == "__main__":
    unittest.main()
