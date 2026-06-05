from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp inverting summing amplifier")
    circuit.include(include_path)
    circuit.voltage("VIN1", "in1", "0", "PULSE(0 0.5 0 1u 1u 5m 10m)", at=(96, 144))
    circuit.voltage("VIN2", "in2", "0", "PULSE(0 0.25 1m 1u 1u 5m 10m)", at=(96, 400))
    circuit.voltage("VCC", "vcc", "0", "5", at=(720, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(720, 448))
    circuit.resistor("R1", "in1", "sum", "10k", at=(248, 240))
    circuit.resistor("R2", "in2", "sum", "20k", at=(248, 400))
    circuit.resistor("RF", "out", "sum", "20k", at=(464, 128))
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(416, 208))
    circuit.resistor("RL", "out", "0", "10k", at=(640, 272), symbol="res_v")
    circuit.wire(64, 144, 176, 144)
    circuit.wire(176, 144, 176, 240)
    circuit.wire(176, 240, 248, 240)
    circuit.wire(64, 400, 248, 400)
    circuit.wire(344, 240, 352, 240)
    circuit.wire(344, 400, 352, 400)
    circuit.wire(352, 240, 352, 304)
    circuit.wire(352, 400, 352, 304)
    circuit.wire(352, 304, 416, 304)
    circuit.wire(416, 304, 416, 128)
    circuit.wire(416, 128, 464, 128)
    circuit.wire(560, 128, 560, 272)
    circuit.wire(560, 272, 704, 272)
    circuit.iopin(64, 144, "in1", "In")
    circuit.iopin(64, 400, "in2", "In")
    circuit.iopin(704, 272, "out", "Out")
    circuit.flag(96, 240, "0")
    circuit.flag(96, 496, "0")
    circuit.flag(416, 240, "0")
    circuit.flag(640, 368, "0")
    circuit.flag(720, 48, "vcc")
    circuit.flag(720, 144, "0")
    circuit.flag(720, 448, "vee")
    circuit.flag(720, 544, "0")
    circuit.opamp_supply_flags(416, 208)
    circuit.tran("0", "4m", "0", "5u")
    circuit.meas("TRAN", "vout_2ms", "FIND V(out) AT=2m")
    circuit.meas("TRAN", "vout_3ms", "FIND V(out) AT=3m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_summing.cir"),
        "asc": circuit.write_asc(output / "opamp_summing.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
