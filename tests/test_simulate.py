from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from claw_spice.simulate import ltspice_command, wine_path


class SimulateTests(unittest.TestCase):
    def test_wine_path_maps_absolute_path_to_z_drive(self) -> None:
        path = wine_path(Path("/tmp/example.cir"))

        self.assertTrue(path.startswith("Z:"))
        self.assertIn("\\tmp\\example.cir", path)

    def test_ltspice_command_prefers_environment(self) -> None:
        with mock.patch.dict(os.environ, {"LTSPICE_CMD": "ltspice-custom -flag"}, clear=False):
            self.assertEqual(ltspice_command(), ["ltspice-custom", "-flag"])


if __name__ == "__main__":
    unittest.main()
