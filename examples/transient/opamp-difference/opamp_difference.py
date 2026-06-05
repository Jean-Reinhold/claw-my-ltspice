from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp difference amplifier")
    circuit.include(include_path)
    circuit.voltage("VPLUS", "plus", "0", "PULSE(0 0.8 0 1u 1u 5m 10m)", at=(96, 192))
    circuit.voltage("VMINUS", "minus", "0", "PULSE(0 0.3 1m 1u 1u 5m 10m)", at=(96, 352))
    circuit.voltage("VCC", "vcc", "0", "5", at=(832, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(832, 448))
    circuit.resistor("RINM", "minus", "inv", "10k", at=(224, 400))
    circuit.resistor("RFM", "out", "inv", "20k", at=(624, 144))
    circuit.resistor("RINP", "plus", "noninv", "10k", at=(224, 224))
    circuit.resistor("RGP", "noninv", "0", "20k", at=(384, 256), symbol="res_v")
    circuit.opamp("XU1", "noninv", "inv", "vcc", "vee", "out", at=(576, 224))
    circuit.resistor("RL", "out", "0", "10k", at=(832, 288), symbol="res_v")
    circuit.wire(64, 192, 160, 192)
    circuit.wire(160, 192, 160, 224)
    circuit.wire(160, 224, 224, 224)
    circuit.wire(320, 224, 384, 224)
    circuit.wire(384, 224, 384, 256)
    circuit.wire(384, 256, 576, 256)
    circuit.wire(64, 352, 160, 352)
    circuit.wire(160, 352, 160, 400)
    circuit.wire(160, 400, 224, 400)
    circuit.wire(320, 400, 448, 400)
    circuit.wire(448, 400, 448, 320)
    circuit.wire(448, 320, 576, 320)
    circuit.wire(576, 320, 576, 144)
    circuit.wire(576, 144, 624, 144)
    circuit.wire(720, 144, 720, 288)
    circuit.wire(720, 288, 896, 288)
    circuit.iopin(64, 192, "plus", "In")
    circuit.iopin(64, 352, "minus", "In")
    circuit.iopin(896, 288, "out", "Out")
    circuit.flag(96, 288, "0")
    circuit.flag(96, 448, "0")
    circuit.flag(384, 352, "0")
    circuit.flag(832, 384, "0")
    circuit.flag(832, 48, "vcc")
    circuit.flag(832, 144, "0")
    circuit.flag(832, 448, "vee")
    circuit.flag(832, 544, "0")
    circuit.opamp_supply_flags(576, 224)
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
