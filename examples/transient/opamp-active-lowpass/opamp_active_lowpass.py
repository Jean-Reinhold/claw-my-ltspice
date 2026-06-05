from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp buffered active low-pass")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 500u 1m)", at=(96, 224))
    circuit.voltage("VCC", "vcc", "0", "5", at=(512, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(512, 400))
    circuit.resistor("RIN", "in", "filt", "10k", at=(360, 224))
    circuit.capacitor("CF", "filt", "0", "47n", at=(560, 224))
    circuit.opamp("XU1", "filt", "out", "vcc", "vee", "out", at=(672, 192))
    circuit.resistor("RL", "out", "0", "10k", at=(912, 256), symbol="res_v")
    circuit.wire(64, 224, 360, 224)
    circuit.wire(456, 224, 672, 224)
    circuit.wire(560, 224, 560, 320)
    circuit.wire(816, 256, 976, 256)
    circuit.wire(816, 256, 848, 256)
    circuit.wire(848, 256, 848, 336)
    circuit.wire(848, 336, 672, 336)
    circuit.wire(672, 336, 672, 288)
    circuit.iopin(64, 224, "in", "In")
    circuit.iopin(976, 256, "out", "Out")
    circuit.flag(96, 320, "0")
    circuit.flag(560, 320, "0")
    circuit.flag(912, 352, "0")
    circuit.flag(512, 48, "vcc")
    circuit.flag(512, 144, "0")
    circuit.flag(512, 400, "vee")
    circuit.flag(512, 496, "0")
    circuit.opamp_supply_flags(672, 192)
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
