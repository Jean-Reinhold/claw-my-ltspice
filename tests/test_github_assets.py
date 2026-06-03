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


if __name__ == "__main__":
    unittest.main()
