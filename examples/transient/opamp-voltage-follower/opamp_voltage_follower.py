from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp voltage follower")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 5m 10m)", at=(96, 160))
    circuit.voltage("VCC", "vcc", "0", "5", at=(320, 32))
    circuit.voltage("VEE", "vee", "0", "-5", at=(320, 288))
    circuit.opamp("XU1", "in", "out", "vcc", "vee", "out", at=(384, 144))
    circuit.resistor("RL", "out", "0", "10k", at=(560, 176))
    circuit.tran("0", "4m", "0", "5u")
    circuit.meas("TRAN", "vout_2ms", "FIND V(out) AT=2m")
    circuit.meas("TRAN", "tracking_error_max", "MAX abs(V(out)-V(in)) FROM=1m TO=4m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_voltage_follower.cir"),
        "asc": circuit.write_asc(output / "opamp_voltage_follower.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
