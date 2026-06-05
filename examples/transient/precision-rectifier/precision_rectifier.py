from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Precision half-wave rectifier")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "SINE(0 0.75 1k)", at=(96, 224))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 368))
    circuit.opamp("XU1", "in", "rect", "vcc", "vee", "drive", at=(416, 192))
    circuit.diode("D1", "drive", "rect", "DCLAW", at=(592, 256))
    circuit.resistor("RLOAD", "rect", "0", "10k", at=(720, 256), rotation="R90")
    circuit.wire(64, 224, 416, 224)
    circuit.wire(560, 256, 592, 256)
    circuit.wire(656, 256, 784, 256)
    circuit.wire(720, 256, 720, 352)
    circuit.wire(656, 256, 688, 256)
    circuit.wire(688, 256, 688, 336)
    circuit.wire(688, 336, 416, 336)
    circuit.wire(416, 336, 416, 288)
    circuit.wire(288, 48, 464, 48)
    circuit.wire(464, 48, 464, 192)
    circuit.wire(288, 368, 464, 368)
    circuit.wire(464, 368, 464, 320)
    circuit.iopin(64, 224, "in", "In")
    circuit.iopin(784, 256, "rect", "Out")
    circuit.flag(96, 320, "0")
    circuit.flag(720, 352, "0")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 464, "0")
    circuit.directive(".model DCLAW D(Is=2n Rs=0.2 N=1.8 Cjo=2p)")
    circuit.tran("0", "5m", "0", "1u")
    circuit.meas("TRAN", "vrect_max", "MAX V(rect) FROM=1m TO=5m")
    circuit.meas("TRAN", "vrect_min", "MIN V(rect) FROM=1m TO=5m")
    circuit.meas("TRAN", "vrect_avg", "AVG V(rect) FROM=1m TO=5m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "precision_rectifier.cir"),
        "asc": circuit.write_asc(output / "precision_rectifier.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
