from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType


def _load_example(path: str) -> ModuleType:
    source = Path(path)
    spec = importlib.util.spec_from_file_location(source.stem, source)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SchmittExampleTests(unittest.TestCase):
    def test_committed_schmitt_outputs_match_generators(self) -> None:
        examples = [
            Path("examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.py"),
            Path(
                "examples/transient/schmitt-trigger-temperature-switch/"
                "schmitt_trigger_temperature_switch.py"
            ),
        ]

        for source in examples:
            with self.subTest(source=source):
                circuit = _load_example(source.as_posix()).create_circuit()
                self.assertEqual(source.with_suffix(".cir").read_text(), circuit.to_netlist())
                self.assertEqual(source.with_suffix(".asc").read_text(), circuit.to_asc())

    def test_simple_schmitt_exposes_configurable_hysteresis(self) -> None:
        module = _load_example("examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.py")
        netlist = module.create_circuit().to_netlist()

        self.assertIn(".param RHYS=100k", netlist)
        self.assertIn(".param RREF=20k", netlist)
        self.assertIn(".param VTRIP=4.8*RREF/(RHYS+RREF)", netlist)
        self.assertIn(".meas TRAN upper_trip FIND V(in) WHEN V(out)=0 FALL=1", netlist)
        self.assertIn(".meas TRAN lower_trip FIND V(in) WHEN V(out)=0 RISE=1", netlist)
        self.assertIn(".meas TRAN hysteresis_width PARAM upper_trip-lower_trip", netlist)
        self.assertIn(".meas TRAN expected_hysteresis PARAM 2*VTRIP", netlist)

    def test_temperature_switch_uses_real_fan_enable_node(self) -> None:
        module = _load_example(
            "examples/transient/schmitt-trigger-temperature-switch/"
            "schmitt_trigger_temperature_switch.py"
        )
        netlist = module.create_circuit().to_netlist()

        self.assertIn("RHYS fan_en cmp {RHYS}", netlist)
        self.assertIn("XU1 cmp ref vcc 0 fan_en CLAW_IDEAL_OPAMP", netlist)
        self.assertIn("RLOAD fan_en 0 10k", netlist)
        self.assertIn(".param UPPER_TRIP=VREF*(1+RIN/RHYS)-VOUT_L*(RIN/RHYS)", netlist)
        self.assertIn(".param LOWER_TRIP=VREF*(1+RIN/RHYS)-VOUT_H*(RIN/RHYS)", netlist)
        self.assertIn("WHEN V(fan_en)=2.5 RISE=1", netlist)
        self.assertIn("WHEN V(fan_en)=2.5 FALL=1", netlist)
        self.assertIn("TRIG V(fan_en) VAL=2.5 RISE=1", netlist)
        self.assertIn(".meas TRAN ripple_reduction PARAM raw_ripple_pp/filtered_ripple_pp", netlist)

    def test_schmitt_readmes_document_expected_measurements(self) -> None:
        simple = Path("examples/transient/schmitt-trigger-simple/README.md").read_text()
        practical = Path("examples/transient/schmitt-trigger-temperature-switch/README.md").read_text()

        for measurement in (
            "upper_trip",
            "lower_trip",
            "hysteresis_width",
            "expected_trip",
            "expected_hysteresis",
        ):
            with self.subTest(readme="simple", measurement=measurement):
                self.assertIn(f"`{measurement}`", simple)
        for measurement in (
            "turn_on_sensor",
            "turn_off_sensor",
            "hysteresis_width",
            "expected_upper",
            "expected_lower",
            "fan_on_time",
            "raw_ripple_pp",
            "filtered_ripple_pp",
            "ripple_reduction",
        ):
            with self.subTest(readme="temperature-switch", measurement=measurement):
                self.assertIn(f"`{measurement}`", practical)
        self.assertIn("Expected measurement ranges", simple)
        self.assertIn("Expected measurement ranges", practical)


if __name__ == "__main__":
    unittest.main()
