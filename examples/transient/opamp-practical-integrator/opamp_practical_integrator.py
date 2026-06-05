from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Practical inverting op-amp integrator")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(-0.1 0.1 0 10u 10u 1m 2m)", at=(96, 336))
    circuit.voltage("VCC", "vcc", "0", "5", at=(528, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(528, 496))
    circuit.resistor("RIN", "in", "sum", "100k", at=(400, 336))
    circuit.resistor("RLEAK", "sum", "out", "1Meg", at=(688, 40))
    circuit.capacitor("CF", "sum", "out", "10n", at=(688, 160), symbol="cap_h")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(640, 240))
    circuit.resistor("RL", "out", "0", "10k", at=(928, 304), symbol="res_v")
    circuit.wire(64, 336, 400, 336)
    circuit.wire(496, 336, 640, 336)
    circuit.wire(640, 336, 640, 40)
    circuit.wire(640, 40, 688, 40)
    circuit.wire(640, 160, 688, 160)
    circuit.wire(784, 40, 784, 304)
    circuit.wire(784, 304, 1008, 304)
    circuit.wire(640, 160, 640, 40)
    circuit.iopin(64, 336, "in", "In")
    circuit.iopin(1008, 304, "out", "Out")
    circuit.flag(96, 432, "0")
    circuit.flag(640, 272, "0")
    circuit.flag(928, 400, "0")
    circuit.flag(528, 48, "vcc")
    circuit.flag(528, 144, "0")
    circuit.flag(528, 496, "vee")
    circuit.flag(528, 592, "0")
    circuit.opamp_supply_flags(640, 240)
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
