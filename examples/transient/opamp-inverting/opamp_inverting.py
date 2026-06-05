from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp inverting amplifier")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 5m 10m)", at=(96, 224))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 352))
    circuit.resistor("RIN", "in", "sum", "10k", at=(224, 272))
    circuit.resistor("RF", "out", "sum", "20k", at=(464, 72))
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(416, 176))
    circuit.resistor("RL", "out", "0", "10k", at=(640, 240), symbol="res_v")
    circuit.wire(64, 224, 160, 224)
    circuit.wire(160, 224, 160, 272)
    circuit.wire(160, 272, 224, 272)
    circuit.wire(320, 272, 416, 272)
    circuit.wire(416, 272, 416, 72)
    circuit.wire(416, 72, 464, 72)
    circuit.wire(560, 72, 560, 240)
    circuit.wire(560, 240, 704, 240)
    circuit.iopin(64, 224, "in", "In")
    circuit.iopin(704, 240, "out", "Out")
    circuit.flag(96, 320, "0")
    circuit.flag(416, 208, "0")
    circuit.flag(640, 336, "0")
    circuit.flag(288, 48, "vcc")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 352, "vee")
    circuit.flag(288, 448, "0")
    circuit.opamp_supply_flags(416, 176)
    circuit.tran("0", "4m", "0", "5u")
    circuit.meas("TRAN", "vout_2ms", "FIND V(out) AT=2m")
    circuit.meas("TRAN", "gain_2ms", "PARAM vout_2ms/1")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_inverting.cir"),
        "asc": circuit.write_asc(output / "opamp_inverting.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
