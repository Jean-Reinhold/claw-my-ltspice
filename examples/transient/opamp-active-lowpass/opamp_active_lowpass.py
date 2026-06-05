from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp buffered active low-pass")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 500u 1m)", at=(96, 224))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 368))
    circuit.resistor("RIN", "in", "filt", "10k", at=(224, 224))
    circuit.capacitor("CF", "filt", "0", "47n", at=(352, 224))
    circuit.opamp("XU1", "filt", "out", "vcc", "vee", "out", at=(416, 192))
    circuit.resistor("RL", "out", "0", "10k", at=(656, 256), rotation="R90")
    circuit.wire(64, 224, 224, 224)
    circuit.wire(320, 224, 416, 224)
    circuit.wire(352, 224, 352, 320)
    circuit.wire(560, 256, 720, 256)
    circuit.wire(560, 256, 592, 256)
    circuit.wire(592, 256, 592, 336)
    circuit.wire(592, 336, 416, 336)
    circuit.wire(416, 336, 416, 288)
    circuit.wire(288, 48, 464, 48)
    circuit.wire(464, 48, 464, 192)
    circuit.wire(288, 368, 464, 368)
    circuit.wire(464, 368, 464, 320)
    circuit.iopin(64, 224, "in", "In")
    circuit.iopin(720, 256, "out", "Out")
    circuit.flag(96, 320, "0")
    circuit.flag(352, 320, "0")
    circuit.flag(656, 352, "0")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 464, "0")
    circuit.tran("0", "4m", "0", "2u")
    circuit.meas("TRAN", "vout_avg", "AVG V(out) FROM=2m TO=4m")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=2m TO=4m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_active_lowpass.cir"),
        "asc": circuit.write_asc(output / "opamp_active_lowpass.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
