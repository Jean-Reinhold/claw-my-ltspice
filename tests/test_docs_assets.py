from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.docs_assets import EXPECTED_PLOT_ASSETS, generate_opencode_reference, generate_plot_assets


class DocsAssetTests(unittest.TestCase):
    def test_generate_plot_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plots = generate_plot_assets(temp)

            self.assertEqual({plot.name for plot in plots}, set(EXPECTED_PLOT_ASSETS))
            for plot in plots:
                self.assertTrue(plot.exists())
                self.assertIn("<svg", plot.read_text())

    def test_generate_opencode_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "ai-instructions.md"
            page = generate_opencode_reference(output)

            text = page.read_text()
            self.assertIn("# Full AI Instructions", text)
            for path in Path(".opencode/agent").glob("*.md"):
                self.assertIn(f"Source: `{path.as_posix()}`", text)
                self.assertIn(path.read_text().strip(), text)
            for path in Path(".opencode/skills").glob("*/SKILL.md"):
                self.assertIn(f"Source: `{path.as_posix()}`", text)
                self.assertIn(path.read_text().strip(), text)

    def test_committed_plot_assets_exist_for_pages(self) -> None:
        expected = set(EXPECTED_PLOT_ASSETS)
        actual = {path.name for path in Path("docs-site/pages/assets/plots").glob("*.svg")}

        self.assertTrue(expected.issubset(actual))

    def test_committed_plot_assets_have_accessible_metadata(self) -> None:
        for asset in EXPECTED_PLOT_ASSETS:
            with self.subTest(asset=asset):
                text = (Path("docs-site/pages/assets/plots") / asset).read_text()
                self.assertIn("<title>", text)
                self.assertIn("<desc>", text)

    def test_signal_plots_page_references_expected_assets(self) -> None:
        page = Path("docs-site/pages/signal-plots.md").read_text()

        for asset in EXPECTED_PLOT_ASSETS:
            with self.subTest(asset=asset):
                self.assertIn(f"assets/plots/{asset}", page)

    def test_schmitt_plots_include_threshold_markers(self) -> None:
        simple = Path("docs-site/pages/assets/plots/schmitt-trigger-simple.svg").read_text()
        practical = Path("docs-site/pages/assets/plots/schmitt-trigger-temperature-switch.svg").read_text()

        self.assertIn("upper trip", simple)
        self.assertIn("lower trip", simple)
        self.assertIn("fan on", practical)
        self.assertIn("fan off", practical)


if __name__ == "__main__":
    unittest.main()
