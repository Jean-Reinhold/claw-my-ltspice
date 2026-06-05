from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Practical inverting op-amp differentiator")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(-0.05 0.05 0 500u 500u 2m 5m)", at=(96, 336))
    circuit.voltage("VCC", "vcc", "0", "5", at=(528, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(528, 496))
    circuit.capacitor("CIN", "in", "ncin", "100n", at=(360, 336), symbol="cap_h")
    circuit.resistor("RIN", "ncin", "sum", "1k", at=(520, 336))
    circuit.resistor("RF", "sum", "out", "100k", at=(720, 40))
    circuit.capacitor("CF", "sum", "out", "1n", at=(720, 160), symbol="cap_h")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(672, 240))
    circuit.resistor("RL", "out", "0", "10k", at=(960, 304), symbol="res_v")
    circuit.wire(64, 336, 360, 336)
    circuit.wire(456, 336, 520, 336)
    circuit.wire(616, 336, 672, 336)
    circuit.wire(672, 336, 672, 40)
    circuit.wire(672, 40, 720, 40)
    circuit.wire(672, 160, 720, 160)
    circuit.wire(816, 40, 816, 304)
    circuit.wire(816, 304, 1040, 304)
    circuit.wire(672, 160, 672, 40)
    circuit.iopin(64, 336, "in", "In")
    circuit.iopin(1040, 304, "out", "Out")
    circuit.flag(96, 432, "0")
    circuit.flag(672, 272, "0")
    circuit.flag(960, 400, "0")
    circuit.flag(528, 48, "vcc")
    circuit.flag(528, 144, "0")
    circuit.flag(528, 496, "vee")
    circuit.flag(528, 592, "0")
    circuit.opamp_supply_flags(672, 240)
    circuit.tran("0", "15m", "0", "5u")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=5m TO=15m")
    circuit.meas("TRAN", "vout_min", "MIN V(out) FROM=5m TO=15m")
    circuit.meas("TRAN", "vout_rms", "RMS V(out) FROM=5m TO=15m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_practical_differentiator.cir"),
        "asc": circuit.write_asc(output / "opamp_practical_differentiator.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
