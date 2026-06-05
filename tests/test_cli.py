from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_examples import EXPECTED_SAMPLE_IDS


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        src_path = str(Path.cwd() / "src")
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "claw_spice.cli", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_doctor_json(self) -> None:
        result = self.run_cli("doctor", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("python", json.loads(result.stdout))

    def test_log_summary_cli(self) -> None:
        result = self.run_cli("log", "summary", "tests/fixtures/sample.log")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Status: PASS", result.stdout)

    def test_raw_traces_cli(self) -> None:
        result = self.run_cli("raw", "traces", "tests/fixtures/ascii.raw")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("V(out)", result.stdout)

    def test_code_build_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli(
                "code",
                "build",
                "examples/transient/rc-step/rc_step.py",
                "--output-dir",
                temp,
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(Path(payload["cir"]).exists())
            self.assertTrue(Path(payload["asc"]).exists())

    def test_render_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "out.svg"
            result = self.run_cli(
                "render",
                "examples/transient/rc-step/rc_step.asc",
                "--output",
                str(output),
                "--print-svg-path",
            )

            if shutil.which("ltspice_to_svg") or shutil.which("ltspice-to-svg"):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(output.exists())
                self.assertEqual(result.stdout.strip(), str(output))
            else:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ltspice_to_svg is required", result.stderr)

    def test_examples_run_skip_sim(self) -> None:
        result = self.run_cli("examples", "run", "--skip-sim", "--skip-render")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Simulation skipped", result.stdout)

    def test_raw_plot_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "plot.svg"
            result = self.run_cli("raw", "plot", "tests/fixtures/ascii.raw", "V(out)", "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SVG plot:", result.stdout)
            self.assertIn("<svg", output.read_text())

    def test_examples_list_json(self) -> None:
        result = self.run_cli("examples", "list", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        ids = {item["id"] for item in payload}
        self.assertEqual(ids, EXPECTED_SAMPLE_IDS)

    def test_raw_fft_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp) / "wave.raw"
            raw.write_text(
                "\n".join(
                    [
                        "Title: FFT fixture",
                        "Plotname: Transient Analysis",
                        "Flags: real forward",
                        "No. Variables: 2",
                        "No. Points: 8",
                        "Variables:",
                        "        0       time    time",
                        "        1       V(out)  voltage",
                        "Values:",
                        "0       0",
                        "        0",
                        "1       0.001",
                        "        1",
                        "2       0.002",
                        "        0",
                        "3       0.003",
                        "        -1",
                        "4       0.004",
                        "        0",
                        "5       0.005",
                        "        1",
                        "6       0.006",
                        "        0",
                        "7       0.007",
                        "        -1",
                    ]
                )
            )
            output = Path(temp) / "fft.svg"
            result = self.run_cli("raw", "fft", str(raw), "V(out)", "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SVG FFT plot:", result.stdout)
            self.assertIn("<svg", output.read_text())


if __name__ == "__main__":
    unittest.main()
