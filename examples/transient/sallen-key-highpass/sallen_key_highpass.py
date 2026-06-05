from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Unity-gain Sallen-Key high-pass filter")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 0.5 0 20u 20u 500u 1m)", at=(96, 304))
    circuit.voltage("VCC", "vcc", "0", "5", at=(704, 64))
    circuit.voltage("VEE", "vee", "0", "-5", at=(704, 512))
    circuit.capacitor("C1", "in", "n1", "10n", at=(360, 304), symbol="cap_h")
    circuit.capacitor("C2", "n1", "filt", "10n", at=(560, 304), symbol="cap_h")
    circuit.resistor("R1", "n1", "out", "10k", at=(488, 136))
    circuit.resistor("R2", "filt", "0", "10k", at=(704, 304), symbol="res_v")
    circuit.opamp("XU1", "filt", "out", "vcc", "vee", "out", at=(816, 272))
    circuit.resistor("RL", "out", "0", "10k", at=(1056, 336), symbol="res_v")
    circuit.wire(64, 304, 360, 304)
    circuit.wire(456, 304, 560, 304)
    circuit.wire(656, 304, 816, 304)
    circuit.wire(456, 304, 456, 136)
    circuit.wire(456, 136, 488, 136)
    circuit.wire(584, 136, 960, 136)
    circuit.wire(960, 136, 960, 336)
    circuit.wire(960, 336, 1136, 336)
    circuit.wire(960, 336, 960, 440)
    circuit.wire(960, 440, 816, 440)
    circuit.wire(816, 440, 816, 368)
    circuit.iopin(64, 304, "in", "In")
    circuit.iopin(1136, 336, "out", "Out")
    circuit.flag(96, 400, "0")
    circuit.flag(704, 400, "0")
    circuit.flag(1056, 432, "0")
    circuit.flag(704, 64, "vcc")
    circuit.flag(704, 160, "0")
    circuit.flag(704, 512, "vee")
    circuit.flag(704, 608, "0")
    circuit.opamp_supply_flags(816, 272)
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
