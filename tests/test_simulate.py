from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from claw_spice.simulate import SimulationResult, _run_ltspice_command, ltspice_command, simulation_command, wine_path


class SimulateTests(unittest.TestCase):
    def test_wine_path_maps_absolute_path_to_z_drive(self) -> None:
        path = wine_path(Path("/tmp/example.cir"))

        self.assertTrue(path.startswith("Z:"))
        self.assertIn("/tmp/example.cir", path)

    def test_ltspice_command_prefers_environment(self) -> None:
        with mock.patch.dict(os.environ, {"LTSPICE_CMD": "ltspice-custom -flag"}, clear=False):
            self.assertEqual(ltspice_command(), ["ltspice-custom", "-flag"])

    def test_run_simulation_uses_batch_form_for_netlists(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "example.cir"
            source.write_text(".end\n")

            with mock.patch("claw_spice.simulate.ltspice_command", return_value=["ltspice"]):
                command = simulation_command(source)

            self.assertEqual(command, ["ltspice", "-b", wine_path(source)])

    def test_run_simulation_keeps_run_flag_for_schematics(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "example.asc"
            source.write_text("Version 4\n")

            with mock.patch("claw_spice.simulate.ltspice_command", return_value=["ltspice"]):
                command = simulation_command(source)

            self.assertEqual(command, ["ltspice", "-Run", "-b", wine_path(source)])

    def test_successful_return_code_requires_log_and_raw_artifacts(self) -> None:
        result = SimulationResult(Path("example.cir"), ["ltspice"], 0, None, None, "", "")

        self.assertFalse(result.ok)
        self.assertEqual(result.missing_artifacts, ("log", "raw"))

    def test_simulation_result_ok_when_artifacts_exist(self) -> None:
        result = SimulationResult(
            Path("example.cir"),
            ["ltspice"],
            0,
            Path("example.log"),
            Path("example.raw"),
            "",
            "",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.missing_artifacts, ())

    def test_ltspice_timeout_kills_process_group(self) -> None:
        process = mock.Mock()
        process.pid = 1234
        process.communicate.side_effect = [subprocess.TimeoutExpired(["ltspice"], 5), ("", "")]

        with mock.patch("claw_spice.simulate.subprocess.Popen", return_value=process) as popen, mock.patch(
            "claw_spice.simulate.os.killpg"
        ) as killpg:
            with self.assertRaises(subprocess.TimeoutExpired):
                _run_ltspice_command(["ltspice"], Path("."), 5)

        self.assertTrue(popen.call_args.kwargs["start_new_session"])
        killpg.assert_called_once_with(1234, signal.SIGKILL)


if __name__ == "__main__":
    unittest.main()
