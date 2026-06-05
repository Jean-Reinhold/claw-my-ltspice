from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Practical inverting op-amp integrator")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(-0.1 0.1 0 10u 10u 1m 2m)", at=(96, 288))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 400))
    circuit.resistor("RIN", "in", "sum", "100k", at=(224, 288))
    circuit.resistor("RLEAK", "out", "sum", "1Meg", at=(496, 80))
    circuit.capacitor("CF", "out", "sum", "10n", at=(496, 128), rotation="R90")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(448, 192))
    circuit.resistor("RL", "out", "0", "10k", at=(704, 256), rotation="R90")
    circuit.wire(64, 288, 224, 288)
    circuit.wire(320, 288, 448, 288)
    circuit.wire(448, 288, 448, 80)
    circuit.wire(448, 80, 496, 80)
    circuit.wire(448, 128, 496, 128)
    circuit.wire(592, 80, 592, 256)
    circuit.wire(592, 256, 768, 256)
    circuit.wire(704, 256, 704, 352)
    circuit.wire(288, 48, 496, 48)
    circuit.wire(496, 48, 496, 192)
    circuit.wire(288, 400, 496, 400)
    circuit.wire(496, 400, 496, 320)
    circuit.iopin(64, 288, "in", "In")
    circuit.iopin(768, 256, "out", "Out")
    circuit.flag(96, 384, "0")
    circuit.flag(448, 224, "0")
    circuit.flag(704, 352, "0")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 496, "0")
    circuit.tran("0", "10m", "0", "2u")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=4m TO=10m")
    circuit.meas("TRAN", "vout_min", "MIN V(out) FROM=4m TO=10m")
    circuit.meas("TRAN", "vout_avg", "AVG V(out) FROM=4m TO=10m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_practical_integrator.cir"),
        "asc": circuit.write_asc(output / "opamp_practical_integrator.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
