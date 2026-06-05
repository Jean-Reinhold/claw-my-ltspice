from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Unity-gain Sallen-Key high-pass filter")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 0.5 0 20u 20u 500u 1m)", at=(96, 256))
    circuit.voltage("VCC", "vcc", "0", "5", at=(752, 64))
    circuit.voltage("VEE", "vee", "0", "-5", at=(752, 432))
    circuit.capacitor("C1", "in", "n1", "10n", at=(224, 256), rotation="R90")
    circuit.capacitor("C2", "n1", "filt", "10n", at=(384, 256), rotation="R90")
    circuit.resistor("R1", "n1", "out", "10k", at=(352, 128))
    circuit.resistor("R2", "filt", "0", "10k", at=(496, 256), rotation="R90")
    circuit.opamp("XU1", "filt", "out", "vcc", "vee", "out", at=(560, 224))
    circuit.resistor("RL", "out", "0", "10k", at=(800, 288), rotation="R90")
    circuit.wire(64, 256, 224, 256)
    circuit.wire(320, 256, 384, 256)
    circuit.wire(480, 256, 560, 256)
    circuit.wire(496, 256, 496, 352)
    circuit.wire(320, 256, 320, 128)
    circuit.wire(320, 128, 352, 128)
    circuit.wire(448, 128, 768, 128)
    circuit.wire(768, 128, 768, 288)
    circuit.wire(704, 288, 864, 288)
    circuit.wire(704, 288, 736, 288)
    circuit.wire(736, 288, 736, 384)
    circuit.wire(736, 384, 560, 384)
    circuit.wire(560, 384, 560, 320)
    circuit.wire(800, 288, 800, 384)
    circuit.wire(752, 64, 608, 64)
    circuit.wire(608, 64, 608, 224)
    circuit.wire(752, 432, 608, 432)
    circuit.wire(608, 432, 608, 352)
    circuit.iopin(64, 256, "in", "In")
    circuit.iopin(864, 288, "out", "Out")
    circuit.flag(96, 352, "0")
    circuit.flag(496, 352, "0")
    circuit.flag(800, 384, "0")
    circuit.flag(752, 160, "0")
    circuit.flag(752, 528, "0")
    circuit.tran("0", "5m", "0", "1u")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=1m TO=5m")
    circuit.meas("TRAN", "vout_min", "MIN V(out) FROM=1m TO=5m")
    circuit.meas("TRAN", "vout_avg", "AVG V(out) FROM=1m TO=5m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "sallen_key_highpass.cir"),
        "asc": circuit.write_asc(output / "sallen_key_highpass.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
