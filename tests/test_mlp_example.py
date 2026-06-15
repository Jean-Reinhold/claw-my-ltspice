from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType


SOURCE = Path("examples/transient/opamp-mlp-forward-pass/opamp_mlp_forward_pass.py")


def _load_example() -> ModuleType:
    spec = importlib.util.spec_from_file_location(SOURCE.stem, SOURCE)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OpampMlpExampleTests(unittest.TestCase):
    def test_committed_mlp_outputs_match_generator(self) -> None:
        circuit = _load_example().create_circuit()

        self.assertEqual(SOURCE.with_suffix(".cir").read_text(), circuit.to_netlist())
        self.assertEqual(SOURCE.with_suffix(".asc").read_text(), circuit.to_asc())

    def test_mlp_netlist_has_three_forward_pass_layers(self) -> None:
        netlist = _load_example().create_circuit().to_netlist()

        for ref in ("XL1A", "XL1B", "XL2A", "XL2B", "XL3Y"):
            with self.subTest(ref=ref):
                self.assertIn(ref, netlist)
        self.assertIn("BA1A a1a 0 V=limit(V(z1a),0,4.8)", netlist)
        self.assertIn("BA2A a2a 0 V=limit(V(z2a),0,4.8)", netlist)
        self.assertIn(".options plotwinsize=0", netlist)

    def test_mlp_measures_forward_pass_vectors(self) -> None:
        netlist = _load_example().create_circuit().to_netlist()

        for index in range(1, 5):
            with self.subTest(vector=index):
                self.assertIn(f".meas TRAN y_vec{index}", netlist)
                self.assertIn(f".meas TRAN expected_y_vec{index}", netlist)
                self.assertIn(f".meas TRAN err_vec{index}", netlist)
        self.assertIn(".meas TRAN z1b_vec1", netlist)
        self.assertIn(".meas TRAN a1b_vec1", netlist)

    def test_mlp_schematic_has_stage_annotations(self) -> None:
        asc = SOURCE.with_suffix(".asc").read_text()

        self.assertIn("Input vector sources", asc)
        self.assertIn("Layer 1 op-amp weighted sums", asc)
        self.assertIn("Layer 2 op-amp weighted sums", asc)
        self.assertIn("Layer 3 output neuron", asc)


if __name__ == "__main__":
    unittest.main()
