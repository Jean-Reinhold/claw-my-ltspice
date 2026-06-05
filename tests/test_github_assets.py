from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from claw_spice.docs_assets import EXPECTED_PLOT_ASSETS


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
        expected_nav = {
            "Overview: index.md",
            "Quick Start: quick-start.md",
            "Engineering Workflow: engineering-workflow.md",
            "Runtime Architecture: docker.md",
            "CLI Reference: command-reference.md",
            "Code-Generated Schematics: code-to-schematic.md",
            "Schematic Rendering: schematic-rendering.md",
            "Simulation And Analysis: simulation-analysis.md",
            "Circuit Examples: examples.md",
            "Theory To Examples: theory-to-examples.md",
            "RC Step Walkthrough: example-rc-step.md",
            "Op-Amp Walkthroughs: example-opamps.md",
            "Precision Rectifier Walkthrough: example-precision-rectifier.md",
            "Sallen-Key Walkthrough: example-sallen-key-lowpass.md",
            "Gallery: gallery.md",
            "Plots And FFT Gallery: signal-plots.md",
            "AI Workflow: opencode.md",
            "Full AI Instructions: ai-instructions.md",
            "GitHub Actions: github-actions.md",
            "Models And Licensing: model-policy.md",
            "Troubleshooting: troubleshooting.md",
        }

        self.assertIn("site_name: claw-spice", mkdocs)
        self.assertIn("site_description:", mkdocs)
        self.assertIn("repo_url:", mkdocs)
        self.assertIn("theme:", mkdocs)
        for nav_entry in expected_nav:
            with self.subTest(nav_entry=nav_entry):
                self.assertIn(nav_entry, mkdocs)
                self.assertTrue((Path("docs-site/pages") / nav_entry.rsplit(": ", 1)[1]).exists())

    def test_pages_content_mentions_core_features(self) -> None:
        home = Path("docs-site/pages/index.md").read_text()

        for phrase in (
            "Docker-first LTspice automation",
            "Docker",
            "code-generated schematics",
            "OpenCode",
        ):
            self.assertIn(phrase, home)

    def test_pages_reference_rendered_example_images(self) -> None:
        examples = Path("docs-site/pages/examples.md").read_text()
        gallery = Path("docs-site/pages/gallery.md").read_text()
        run_ids = {item["id"] for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]}

        for image in (f"assets/generated/{run_id}.svg" for run_id in run_ids):
            self.assertIn(image, examples + gallery)

    def test_pages_reference_signal_plot_images(self) -> None:
        signal_plots = Path("docs-site/pages/signal-plots.md").read_text()
        examples = Path("docs-site/pages/examples.md").read_text()
        gallery = Path("docs-site/pages/gallery.md").read_text()

        for name in EXPECTED_PLOT_ASSETS:
            image = f"assets/plots/{name}"
            self.assertIn(image, signal_plots + examples + gallery)
            self.assertTrue((Path("docs-site/pages") / image).exists())

    def test_theory_and_opencode_pages_are_linked(self) -> None:
        home = Path("docs-site/pages/index.md").read_text()
        theory = Path("docs-site/pages/theory-to-examples.md").read_text()
        opencode = Path("docs-site/pages/opencode.md").read_text()

        self.assertIn("theory-to-examples.md", home)
        self.assertIn("engineering-workflow.md", home)
        self.assertIn("schematic-rendering.md", home)
        self.assertIn("simulation-analysis.md", home)
        self.assertIn("material_teorico", theory)
        self.assertIn("ai-instructions.md", opencode)
        self.assertIn("./claw-spice docs assets", opencode)

    def test_operational_reference_pages_cover_quality_gates(self) -> None:
        workflow = Path("docs-site/pages/engineering-workflow.md").read_text()
        rendering = Path("docs-site/pages/schematic-rendering.md").read_text()
        simulation = Path("docs-site/pages/simulation-analysis.md").read_text()
        command_reference = Path("docs-site/pages/command-reference.md").read_text()

        self.assertIn("Definition Of Done", workflow)
        self.assertIn("./claw-spice raw fft", workflow)
        self.assertIn("fake fallback", rendering)
        self.assertIn("component groups", rendering)
        self.assertIn("Hann window", simulation)
        self.assertIn("raw fft", command_reference)

    def test_render_workflow_uses_docker_renderer_path(self) -> None:
        render = Path(".github/workflows/render.yml").read_text()
        pages = Path(".github/workflows/pages.yml").read_text()

        self.assertIn("docker compose build claw-spice", render)
        self.assertIn("docker compose run --rm claw-spice claw-spice docs assets", render)
        self.assertIn("docker compose run --rm claw-spice claw-spice docs assets", pages)


if __name__ == "__main__":
    unittest.main()
