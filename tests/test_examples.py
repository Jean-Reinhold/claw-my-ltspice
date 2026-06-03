from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


class ExampleAssetTests(unittest.TestCase):
    def test_sample_runs_have_existing_assets_and_previews(self) -> None:
        runs = tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]
        ids = {item["id"] for item in runs}

        self.assertTrue(
            {
                "rc-step",
                "opamp-voltage-follower",
                "opamp-noninverting",
                "opamp-inverting",
                "opamp-summing",
                "opamp-difference",
                "opamp-active-lowpass",
            }.issubset(ids)
        )

        for item in runs:
            with self.subTest(sample=item["id"]):
                generator = Path(item["generator"])
                circuit = Path(item["circuit"])
                schematic = Path(item["schematic"])

                self.assertTrue(generator.exists())
                self.assertTrue(circuit.exists())
                self.assertTrue(schematic.exists())
                self.assertGreaterEqual(len(item.get("expected_measurements", [])), 1)

    def test_opamp_model_is_repo_owned_and_manifested(self) -> None:
        manifest = tomllib.loads(Path("models/manifest.toml").read_text())["models"]
        models = {item["name"]: item for item in manifest}

        self.assertTrue(Path("examples/lib/claw_opamps.lib").exists())
        self.assertIn("CLAW_IDEAL_OPAMP", models)
        self.assertEqual(models["CLAW_IDEAL_OPAMP"]["source"], "repo-owned")
        self.assertTrue(models["CLAW_IDEAL_OPAMP"]["redistributable"])

    def test_example_readmes_embed_preview_images(self) -> None:
        for readme in Path("examples").glob("transient/*/README.md"):
            with self.subTest(readme=readme):
                text = readme.read_text()
                self.assertIn("preview.svg", text)
                self.assertIn("ltspice_to_svg", text)


if __name__ == "__main__":
    unittest.main()
