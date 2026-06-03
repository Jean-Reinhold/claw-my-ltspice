from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from claw_spice.ir import Circuit


class CircuitIrTests(unittest.TestCase):
    def test_netlist_generation(self) -> None:
        circuit = Circuit("test")
        circuit.voltage("V1", "in", "0", "DC 5")
        circuit.resistor("R1", "in", "out", "1k")
        circuit.capacitor("C1", "out", "0", "1u")
        circuit.tran("0", "1m", maxstep="1u")
        circuit.meas("TRAN", "vmax", "MAX V(out)")

        netlist = circuit.to_netlist()

        self.assertIn("V1 in 0 DC 5", netlist)
        self.assertIn(".tran 0 1m 0 1u", netlist)
        self.assertTrue(netlist.endswith(".end\n"))

    def test_asc_generation_contains_symbols_and_directives(self) -> None:
        circuit = Circuit("test")
        circuit.voltage("V1", "in", "0", "DC 5", at=(96, 96))
        circuit.resistor("R1", "in", "out", "1k", at=(224, 96))
        circuit.directive(".tran 0 1m")

        asc = circuit.to_asc()

        self.assertIn("Version 4", asc)
        self.assertIn("SYMBOL voltage", asc)
        self.assertIn("SYMBOL res", asc)
        self.assertIn("!.tran 0 1m", asc)

    def test_write_outputs(self) -> None:
        circuit = Circuit("test")
        circuit.resistor("R1", "a", "b", "10k")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cir = circuit.write_netlist(root / "test.cir")
            asc = circuit.write_asc(root / "test.asc")

            self.assertTrue(cir.exists())
            self.assertTrue(asc.exists())

    def test_opamp_subcircuit_generation(self) -> None:
        circuit = Circuit("opamp")
        circuit.include("claw_opamps.lib")
        circuit.opamp("XU1", "inp", "inn", "vcc", "vee", "out")

        netlist = circuit.to_netlist()
        asc = circuit.to_asc()

        self.assertIn(".include claw_opamps.lib", netlist)
        self.assertIn("XU1 inp inn vcc vee out CLAW_IDEAL_OPAMP", netlist)
        self.assertIn("SYMBOL opamp2", asc)


if __name__ == "__main__":
    unittest.main()
