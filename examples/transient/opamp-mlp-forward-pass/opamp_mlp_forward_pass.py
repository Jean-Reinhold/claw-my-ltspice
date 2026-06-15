from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


RF = 100_000.0


def _resistance_for_gain(gain: float) -> str:
    value = RF / gain
    if value >= 1_000_000.0:
        return f"{value / 1_000_000.0:g}Meg"
    return f"{value / 1_000.0:g}k"


def _input_vectors() -> list[tuple[float, float, float]]:
    return [
        (1e-3, 0.0, 0.0),
        (3e-3, 0.8, 0.1),
        (5e-3, 0.1, 0.9),
        (7e-3, 0.6, 0.5),
    ]


def _forward(x1: float, x2: float) -> tuple[float, float, float, float, float]:
    z1a = 0.7 * x1 + 0.3 * x2 + 0.1
    z1b = 0.2 * x1 + 0.8 * x2 - 0.2
    a1a = max(z1a, 0.0)
    a1b = max(z1b, 0.0)
    a2a = max(0.6 * a1a + 0.4 * a1b + 0.05, 0.0)
    a2b = max(0.3 * a1a + 0.7 * a1b, 0.0)
    y = 0.5 * a2a + 0.5 * a2b + 0.1
    return z1b, a1b, a2a, a2b, y


def _add_bsource(circuit: Circuit, ref: str, node: str, expression: str, at: tuple[int, int]) -> None:
    circuit.behavioral_voltage(ref, node, "0", expression, at=at, symbol="voltage")
    x, y = at
    circuit.flag(x, y, node)
    circuit.flag(x, y + 96, "0")


def _add_weighted_sum(
    circuit: Circuit,
    name: str,
    output: str,
    summing_node: str,
    sources: list[tuple[str, str, float]],
    *,
    at: tuple[int, int],
) -> None:
    x, y = at
    opamp_x = x + 480
    opamp_y = y + 88
    sum_bus_x = x + 400
    out_bus_x = opamp_x + 220
    circuit.opamp(f"X{name}", "0", summing_node, "vcc", "vee", output, at=(opamp_x, opamp_y))
    circuit.flag(opamp_x, opamp_y + 32, "0")
    circuit.flag(opamp_x, opamp_y + 96, summing_node)
    circuit.flag(opamp_x + 144, opamp_y + 64, output)
    circuit.opamp_supply_flags(opamp_x, opamp_y)
    circuit.resistor(f"RF{name}", output, summing_node, "100k", at=(x + 260, y))
    circuit.flag(x + 260, y, output)
    circuit.flag(x + 356, y, summing_node)
    circuit.wire(x + 356, y, sum_bus_x, y)
    circuit.wire(sum_bus_x, y, sum_bus_x, opamp_y + 96)
    circuit.wire(sum_bus_x, opamp_y + 96, opamp_x, opamp_y + 96)
    circuit.wire(opamp_x + 144, opamp_y + 64, out_bus_x, opamp_y + 64)
    circuit.wire(out_bus_x, opamp_y + 64, out_bus_x, y)
    circuit.wire(out_bus_x, y, x + 260, y)
    for index, (suffix, source_node, gain) in enumerate(sources):
        ry = y + 128 + index * 144
        circuit.resistor(f"R{name}{suffix}", source_node, summing_node, _resistance_for_gain(gain), at=(x, ry))
        circuit.flag(x, ry, source_node)
        circuit.flag(x + 96, ry, summing_node)
        circuit.wire(x + 96, ry, sum_bus_x, ry)


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Three-layer op-amp MLP forward pass")
    circuit.include(include_path)
    circuit.directive(".options plotwinsize=0")
    circuit.text(64, 32, "Input vector sources", size=2)
    circuit.text(960, 32, "Layer 1 op-amp weighted sums", size=2)
    circuit.text(1740, 32, "Layer 1 ReLU and inversion", size=2)
    circuit.text(2200, 32, "Layer 2 op-amp weighted sums", size=2)
    circuit.text(2980, 32, "Layer 2 ReLU and inversion", size=2)
    circuit.text(3440, 320, "Layer 3 output neuron", size=2)
    circuit.voltage(
        "VX1",
        "x1",
        "0",
        "PWL(0 0 2m 0 2.01m 0.8 4m 0.8 4.01m 0.1 6m 0.1 6.01m 0.6 8m 0.6)",
        at=(96, 96),
    )
    circuit.voltage(
        "VX2",
        "x2",
        "0",
        "PWL(0 0 2m 0 2.01m 0.1 4m 0.1 4.01m 0.9 6m 0.9 6.01m 0.5 8m 0.5)",
        at=(96, 288),
    )
    circuit.voltage("VBP", "bp", "0", "1", at=(96, 560))
    circuit.voltage("VBN", "bn", "0", "-1", at=(96, 760))
    circuit.voltage("VCC", "vcc", "0", "5", at=(336, 920))
    circuit.voltage("VEE", "vee", "0", "-5", at=(480, 920))
    circuit.flag(96, 96, "x1")
    circuit.flag(96, 192, "0")
    circuit.flag(96, 288, "x2")
    circuit.flag(96, 384, "0")
    circuit.flag(96, 560, "bp")
    circuit.flag(96, 656, "0")
    circuit.flag(96, 760, "bn")
    circuit.flag(96, 856, "0")
    circuit.flag(336, 920, "vcc")
    circuit.flag(336, 1016, "0")
    circuit.flag(480, 920, "vee")
    circuit.flag(480, 1016, "0")
    _add_bsource(circuit, "BNX1", "nx1", "-V(x1)", (640, 96))
    _add_bsource(circuit, "BNX2", "nx2", "-V(x2)", (640, 288))

    _add_weighted_sum(
        circuit,
        "L1A",
        "z1a",
        "sum1a",
        [("X1", "nx1", 0.7), ("X2", "nx2", 0.3), ("B", "bn", 0.1)],
        at=(960, 64),
    )
    _add_weighted_sum(
        circuit,
        "L1B",
        "z1b",
        "sum1b",
        [("X1", "nx1", 0.2), ("X2", "nx2", 0.8), ("B", "bp", 0.2)],
        at=(960, 640),
    )
    _add_bsource(circuit, "BA1A", "a1a", "limit(V(z1a),0,4.8)", (1740, 160))
    _add_bsource(circuit, "BA1B", "a1b", "limit(V(z1b),0,4.8)", (1740, 736))
    _add_bsource(circuit, "BNA1A", "na1a", "-V(a1a)", (1940, 160))
    _add_bsource(circuit, "BNA1B", "na1b", "-V(a1b)", (1940, 736))

    _add_weighted_sum(
        circuit,
        "L2A",
        "z2a",
        "sum2a",
        [("A", "na1a", 0.6), ("B", "na1b", 0.4), ("BI", "bn", 0.05)],
        at=(2200, 64),
    )
    _add_weighted_sum(
        circuit,
        "L2B",
        "z2b",
        "sum2b",
        [("A", "na1a", 0.3), ("B", "na1b", 0.7)],
        at=(2200, 640),
    )
    _add_bsource(circuit, "BA2A", "a2a", "limit(V(z2a),0,4.8)", (2980, 160))
    _add_bsource(circuit, "BA2B", "a2b", "limit(V(z2b),0,4.8)", (2980, 736))
    _add_bsource(circuit, "BNA2A", "na2a", "-V(a2a)", (3180, 160))
    _add_bsource(circuit, "BNA2B", "na2b", "-V(a2b)", (3180, 736))

    _add_weighted_sum(
        circuit,
        "L3Y",
        "yout",
        "sum3y",
        [("A", "na2a", 0.5), ("B", "na2b", 0.5), ("BI", "bn", 0.1)],
        at=(3440, 352),
    )
    circuit.resistor("RLOAD", "yout", "0", "10k", at=(4140, 504), symbol="res_v")
    circuit.flag(4140, 504, "yout")
    circuit.flag(4140, 600, "0")
    circuit.iopin(64, 96, "x1", "In")
    circuit.iopin(64, 288, "x2", "In")
    circuit.iopin(4300, 504, "yout", "Out")
    circuit.wire(4140, 504, 4300, 504)
    circuit.tran("0", "8m", "0", "10u")
    for index, (time, x1, x2) in enumerate(_input_vectors(), start=1):
        z1b, a1b, _a2a, _a2b, y = _forward(x1, x2)
        circuit.meas("TRAN", f"y_vec{index}", f"FIND V(yout) AT={time:g}")
        circuit.meas("TRAN", f"expected_y_vec{index}", f"PARAM {y:.6g}")
        circuit.meas("TRAN", f"err_vec{index}", f"PARAM y_vec{index}-expected_y_vec{index}")
        if index == 1:
            circuit.meas("TRAN", "z1b_vec1", f"FIND V(z1b) AT={time:g}")
            circuit.meas("TRAN", "a1b_vec1", f"FIND V(a1b) AT={time:g}")
            circuit.meas("TRAN", "expected_z1b_vec1", f"PARAM {z1b:.6g}")
            circuit.meas("TRAN", "expected_a1b_vec1", f"PARAM {a1b:.6g}")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_mlp_forward_pass.cir"),
        "asc": circuit.write_asc(output / "opamp_mlp_forward_pass.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
