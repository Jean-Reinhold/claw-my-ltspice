from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp non-inverting amplifier")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 5m 10m)", at=(96, 192))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 336))
    circuit.opamp("XU1", "in", "fb", "vcc", "vee", "out", at=(384, 160))
    circuit.resistor("RG", "fb", "0", "10k", at=(384, 256), rotation="R90")
    circuit.resistor("RF", "out", "fb", "20k", at=(432, 112))
    circuit.resistor("RL", "out", "0", "10k", at=(640, 224), rotation="R90")
    circuit.wire(64, 192, 384, 192)
    circuit.wire(528, 224, 704, 224)
    circuit.wire(384, 256, 384, 112)
    circuit.wire(384, 112, 432, 112)
    circuit.wire(528, 112, 528, 224)
    circuit.iopin(64, 192, "in", "In")
    circuit.iopin(704, 224, "out", "Out")
    circuit.flag(96, 288, "0")
    circuit.flag(384, 352, "0")
    circuit.flag(640, 320, "0")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 432, "0")
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
        "cir": circuit.write_netlist(output / "opamp_noninverting.cir"),
        "asc": circuit.write_asc(output / "opamp_noninverting.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
