from __future__ import annotations

import unittest
from pathlib import Path

from claw_spice.logs import format_log_summary, parse_log


FIXTURES = Path(__file__).parent / "fixtures"


class LogParsingTests(unittest.TestCase):
    def test_parse_measurements_warnings_and_status(self) -> None:
        summary = parse_log(FIXTURES / "sample.log")

        self.assertTrue(summary.ok)
        self.assertEqual([item.name for item in summary.measurements], ["vout_max", "vout_ss", "tau_rise"])
        self.assertAlmostEqual(summary.measurements[0].value or 0, 4.987)
        self.assertEqual(len(summary.warnings), 1)

    def test_parse_failure(self) -> None:
        summary = parse_log(FIXTURES / "failing.log")

        self.assertFalse(summary.ok)
        self.assertEqual(summary.measurements[0].status, "fail")
        self.assertEqual(len(summary.errors), 1)

    def test_format_summary(self) -> None:
        text = format_log_summary(parse_log(FIXTURES / "sample.log"))

        self.assertIn("Status: PASS", text)
        self.assertIn("tau_rise", text)


if __name__ == "__main__":
    unittest.main()
