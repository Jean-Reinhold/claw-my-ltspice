from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Practical inverting op-amp differentiator")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(-0.05 0.05 0 500u 500u 2m 5m)", at=(96, 288))
    circuit.voltage("VCC", "vcc", "0", "5", at=(352, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(352, 400))
    circuit.capacitor("CIN", "in", "ncin", "100n", at=(224, 288), rotation="R90")
    circuit.resistor("RIN", "ncin", "sum", "1k", at=(352, 288))
    circuit.resistor("RF", "out", "sum", "100k", at=(592, 128))
    circuit.capacitor("CF", "out", "sum", "1n", at=(592, 80), rotation="R90")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(544, 192))
    circuit.resistor("RL", "out", "0", "10k", at=(784, 256), rotation="R90")
    circuit.wire(64, 288, 224, 288)
    circuit.wire(320, 288, 352, 288)
    circuit.wire(448, 288, 544, 288)
    circuit.wire(544, 288, 544, 80)
    circuit.wire(544, 80, 592, 80)
    circuit.wire(544, 128, 592, 128)
    circuit.wire(688, 80, 688, 256)
    circuit.wire(688, 256, 848, 256)
    circuit.wire(784, 256, 784, 352)
    circuit.wire(352, 48, 592, 48)
    circuit.wire(592, 48, 592, 192)
    circuit.wire(352, 400, 592, 400)
    circuit.wire(592, 400, 592, 320)
    circuit.iopin(64, 288, "in", "In")
    circuit.iopin(848, 256, "out", "Out")
    circuit.flag(96, 384, "0")
    circuit.flag(544, 224, "0")
    circuit.flag(784, 352, "0")
    circuit.flag(352, 144, "0")
    circuit.flag(352, 496, "0")
    circuit.tran("0", "15m", "0", "5u")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=5m TO=15m")
    circuit.meas("TRAN", "vout_min", "MIN V(out) FROM=5m TO=15m")
    circuit.meas("TRAN", "vout_rms", "RMS V(out) FROM=5m TO=15m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_practical_differentiator.cir"),
        "asc": circuit.write_asc(output / "opamp_practical_differentiator.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
