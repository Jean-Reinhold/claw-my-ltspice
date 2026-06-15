from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from claw_spice.schematic_model import component_collisions


EXPECTED_SAMPLE_IDS = {
    "rc-step",
    "opamp-voltage-follower",
    "opamp-noninverting",
    "opamp-inverting",
    "opamp-summing",
    "opamp-difference",
    "opamp-active-lowpass",
    "precision-rectifier",
    "sallen-key-lowpass",
    "diode-clipper-spectrum",
    "rlc-step-ringing",
    "passive-rc-spectrum-split",
    "opamp-practical-integrator",
    "opamp-practical-differentiator",
    "schmitt-trigger-simple",
    "schmitt-trigger-temperature-switch",
    "sallen-key-highpass",
}


class ExampleAssetTests(unittest.TestCase):
    def test_sample_runs_have_existing_assets_and_previews(self) -> None:
        runs = tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]
        ids = {item["id"] for item in runs}

        self.assertEqual(ids, EXPECTED_SAMPLE_IDS)

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
        self.assertIn("DCLAW", models)
        self.assertEqual(models["DCLAW"]["source"], "repo-owned")
        self.assertTrue(models["DCLAW"]["redistributable"])

    def test_example_docs_cover_all_sample_runs(self) -> None:
        examples = Path("docs-site/pages/examples.md").read_text()
        gallery = Path("docs-site/pages/gallery.md").read_text()

        for sample_id in EXPECTED_SAMPLE_IDS:
            with self.subTest(sample=sample_id):
                self.assertIn(sample_id, examples + gallery)

    def test_example_readmes_embed_preview_images(self) -> None:
        for readme in Path("examples").glob("transient/*/README.md"):
            with self.subTest(readme=readme):
                text = readme.read_text()
                self.assertIn("preview.svg", text)
                self.assertIn("ltspice_to_svg", text)

    def test_committed_schematics_have_explicit_wires(self) -> None:
        for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]:
            schematic = Path(item["schematic"])

            with self.subTest(schematic=schematic):
                wire_count = sum(1 for line in schematic.read_text().splitlines() if line.startswith("WIRE "))
                self.assertGreaterEqual(wire_count, 3)

    def test_bundled_renderer_symbols_cover_examples(self) -> None:
        symbol_dir = Path("src/claw_spice/symbols")
        emitted_symbols: set[str] = set()
        for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]:
            for line in Path(item["schematic"]).read_text().splitlines():
                if line.startswith("SYMBOL "):
                    emitted_symbols.add(line.split()[1])

        missing = {symbol for symbol in emitted_symbols if not (symbol_dir / f"{symbol}.asy").exists()}
        self.assertFalse(missing)

    def test_committed_schematics_have_orthogonal_wires(self) -> None:
        for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]:
            schematic = Path(item["schematic"])

            with self.subTest(schematic=schematic):
                diagonals = []
                for line in schematic.read_text().splitlines():
                    if line.startswith("WIRE "):
                        _wire, x1, y1, x2, y2 = line.split()
                        if x1 != x2 and y1 != y2:
                            diagonals.append(line)
                self.assertEqual(diagonals, [])

    def test_committed_schematics_have_no_modeled_component_collisions(self) -> None:
        for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]:
            schematic = Path(item["schematic"])

            with self.subTest(schematic=schematic):
                collisions = component_collisions(schematic.read_text(), clearance=8)
                formatted = [
                    f"{collision.first.reference}/{collision.second.reference}"
                    for collision in collisions
                ]
                self.assertEqual(formatted, [])

    def test_committed_schematics_use_orientation_specific_symbols(self) -> None:
        rotated_component_symbols = []
        for item in tomllib.loads(Path("examples/sample-runs.toml").read_text())["runs"]:
            schematic = Path(item["schematic"])
            for line in schematic.read_text().splitlines():
                if line.startswith(("SYMBOL res ", "SYMBOL cap ", "SYMBOL diode ", "SYMBOL ind ")):
                    if line.endswith(" R90"):
                        rotated_component_symbols.append(f"{schematic}: {line}")

        self.assertEqual(rotated_component_symbols, [])


if __name__ == "__main__":
    unittest.main()
