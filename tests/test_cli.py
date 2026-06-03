from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            self.assertEqual(result.stdout.strip(), str(output))

    def test_examples_run_skip_sim(self) -> None:
        result = self.run_cli("examples", "run", "--skip-sim")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Simulation skipped", result.stdout)


if __name__ == "__main__":
    unittest.main()
