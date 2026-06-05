from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp difference amplifier")
    circuit.include(include_path)
    circuit.voltage("VPLUS", "plus", "0", "PULSE(0 0.8 0 1u 1u 5m 10m)", at=(96, 192))
    circuit.voltage("VMINUS", "minus", "0", "PULSE(0 0.3 1m 1u 1u 5m 10m)", at=(96, 352))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 416))
    circuit.resistor("RINM", "minus", "inv", "10k", at=(224, 320))
    circuit.resistor("RFM", "out", "inv", "20k", at=(496, 144))
    circuit.resistor("RINP", "plus", "noninv", "10k", at=(224, 256))
    circuit.resistor("RGP", "noninv", "0", "20k", at=(384, 256), rotation="R90")
    circuit.opamp("XU1", "noninv", "inv", "vcc", "vee", "out", at=(448, 224))
    circuit.resistor("RL", "out", "0", "10k", at=(704, 288), rotation="R90")
    circuit.wire(64, 192, 160, 192)
    circuit.wire(160, 192, 160, 256)
    circuit.wire(160, 256, 224, 256)
    circuit.wire(320, 256, 448, 256)
    circuit.wire(384, 256, 384, 352)
    circuit.wire(64, 352, 160, 352)
    circuit.wire(160, 352, 160, 320)
    circuit.wire(160, 320, 224, 320)
    circuit.wire(320, 320, 448, 320)
    circuit.wire(448, 320, 448, 144)
    circuit.wire(448, 144, 496, 144)
    circuit.wire(592, 144, 592, 288)
    circuit.wire(592, 288, 768, 288)
    circuit.iopin(64, 192, "plus", "In")
    circuit.iopin(64, 352, "minus", "In")
    circuit.iopin(768, 288, "out", "Out")
    circuit.flag(96, 288, "0")
    circuit.flag(96, 448, "0")
    circuit.flag(384, 352, "0")
    circuit.flag(704, 384, "0")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 512, "0")
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
        "cir": circuit.write_netlist(output / "opamp_difference.cir"),
        "asc": circuit.write_asc(output / "opamp_difference.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
