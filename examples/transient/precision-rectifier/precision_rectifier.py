from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Precision half-wave rectifier")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "SINE(0 0.75 1k)", at=(96, 272))
    circuit.voltage("VCC", "vcc", "0", "5", at=(464, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(464, 464))
    circuit.opamp("XU1", "in", "rect", "vcc", "vee", "drive", at=(560, 240))
    circuit.diode("D1", "drive", "rect", "DCLAW", at=(768, 304))
    circuit.resistor("RLOAD", "rect", "0", "10k", at=(944, 304), symbol="res_v")
    circuit.wire(64, 272, 560, 272)
    circuit.wire(704, 304, 768, 304)
    circuit.wire(864, 304, 1024, 304)
    circuit.wire(864, 304, 864, 424)
    circuit.wire(864, 424, 560, 424)
    circuit.wire(560, 424, 560, 336)
    circuit.iopin(64, 272, "in", "In")
    circuit.iopin(1024, 304, "rect", "Out")
    circuit.flag(96, 368, "0")
    circuit.flag(944, 400, "0")
    circuit.flag(464, 48, "vcc")
    circuit.flag(464, 144, "0")
    circuit.flag(464, 464, "vee")
    circuit.flag(464, 560, "0")
    circuit.opamp_supply_flags(560, 240)
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
