from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp buffered active low-pass")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 500u 1m)", at=(96, 160))
    circuit.voltage("VCC", "vcc", "0", "5", at=(320, 32))
    circuit.voltage("VEE", "vee", "0", "-5", at=(320, 352))
    circuit.resistor("RIN", "in", "filt", "10k", at=(256, 192), rotation="R90")
    circuit.capacitor("CF", "filt", "0", "47n", at=(368, 224))
    circuit.opamp("XU1", "filt", "out", "vcc", "vee", "out", at=(480, 176))
    circuit.resistor("RL", "out", "0", "10k", at=(672, 208), rotation="R90")
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
