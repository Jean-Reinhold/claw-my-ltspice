from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.docs_assets import generate_plot_assets


class DocsAssetTests(unittest.TestCase):
    def test_generate_plot_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plots = generate_plot_assets(temp)

            self.assertEqual(len(plots), 7)
            for plot in plots:
                self.assertTrue(plot.exists())
                self.assertIn("<svg", plot.read_text())

    def test_committed_plot_assets_exist_for_pages(self) -> None:
        expected = {
            "rc-step-vout.svg",
            "opamp-voltage-follower.svg",
            "opamp-noninverting.svg",
            "opamp-inverting.svg",
            "opamp-summing.svg",
            "opamp-difference.svg",
            "opamp-active-lowpass.svg",
        }
        actual = {path.name for path in Path("docs-site/pages/assets/plots").glob("*.svg")}

        self.assertTrue(expected.issubset(actual))


if __name__ == "__main__":
    unittest.main()
