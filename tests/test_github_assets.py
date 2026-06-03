from __future__ import annotations

import unittest
from pathlib import Path


class GitHubAssetTests(unittest.TestCase):
    def test_expected_workflows_exist(self) -> None:
        expected = {
            "ci.yml",
            "examples.yml",
            "render.yml",
            "ltspice-smoke.yml",
            "simulate.yml",
            "pages.yml",
        }
        actual = {path.name for path in Path(".github/workflows").glob("*.yml")}

        self.assertTrue(expected.issubset(actual))

    def test_ci_workflow_runs_tests_and_uploads_artifacts(self) -> None:
        ci = Path(".github/workflows/ci.yml").read_text()

        self.assertIn("unittest discover", ci)
        self.assertIn("actions/upload-artifact", ci)
        self.assertIn("docker compose config", ci)

    def test_ltspice_smoke_builds_docker_and_mentions_license_boundary(self) -> None:
        smoke = Path(".github/workflows/ltspice-smoke.yml").read_text()

        self.assertIn("docker compose build claw-spice", smoke)
        self.assertIn("claw-spice examples run", smoke)
        self.assertIn("does not redistribute LTspice", smoke)

    def test_pages_workflow_deploys_mkdocs_site(self) -> None:
        pages = Path(".github/workflows/pages.yml").read_text()

        self.assertIn("actions/configure-pages", pages)
        self.assertIn("actions/upload-pages-artifact", pages)
        self.assertIn("actions/deploy-pages", pages)
        self.assertIn("claw-spice docs build", pages)

    def test_issue_templates_exist(self) -> None:
        expected = {"bug_report.yml", "model_request.yml", "simulation_help.yml"}
        actual = {path.name for path in Path(".github/ISSUE_TEMPLATE").glob("*.yml")}

        self.assertTrue(expected.issubset(actual))

    def test_mkdocs_site_metadata(self) -> None:
        mkdocs = Path("docs-site/mkdocs.yml").read_text()

        self.assertIn("site_name: claw-spice", mkdocs)
        self.assertIn("site_description:", mkdocs)
        self.assertIn("repo_url:", mkdocs)
        self.assertIn("theme:", mkdocs)
        self.assertIn("Home: index.md", mkdocs)

    def test_pages_content_mentions_core_features(self) -> None:
        home = Path("docs-site/pages/index.md").read_text()

        for phrase in (
            "OpenCode-assisted LTspice automation",
            "Docker",
            "code-generated schematics",
            "GitHub Actions",
        ):
            self.assertIn(phrase, home)

    def test_pages_reference_rendered_example_images(self) -> None:
        examples = Path("docs-site/pages/examples.md").read_text()
        gallery = Path("docs-site/pages/gallery.md").read_text()

        for image in (
            "assets/generated/rc-step.svg",
            "assets/generated/opamp-voltage-follower.svg",
            "assets/generated/opamp-noninverting.svg",
            "assets/generated/opamp-inverting.svg",
            "assets/generated/opamp-summing.svg",
            "assets/generated/opamp-difference.svg",
            "assets/generated/opamp-active-lowpass.svg",
        ):
            self.assertIn(image, examples + gallery)

    def test_pages_reference_signal_plot_images(self) -> None:
        signal_plots = Path("docs-site/pages/signal-plots.md").read_text()
        examples = Path("docs-site/pages/examples.md").read_text()
        gallery = Path("docs-site/pages/gallery.md").read_text()

        for image in (
            "assets/plots/rc-step-vout.svg",
            "assets/plots/opamp-voltage-follower.svg",
            "assets/plots/opamp-noninverting.svg",
            "assets/plots/opamp-inverting.svg",
            "assets/plots/opamp-summing.svg",
            "assets/plots/opamp-difference.svg",
            "assets/plots/opamp-active-lowpass.svg",
        ):
            self.assertIn(image, signal_plots + examples + gallery)
            self.assertTrue((Path("docs-site/pages") / image).exists())

    def test_render_workflow_uses_docker_renderer_path(self) -> None:
        render = Path(".github/workflows/render.yml").read_text()
        pages = Path(".github/workflows/pages.yml").read_text()

        self.assertIn("docker compose build claw-spice", render)
        self.assertIn("docker compose run --rm claw-spice claw-spice docs assets", render)
        self.assertIn("docker compose run --rm claw-spice claw-spice docs assets", pages)


if __name__ == "__main__":
    unittest.main()
