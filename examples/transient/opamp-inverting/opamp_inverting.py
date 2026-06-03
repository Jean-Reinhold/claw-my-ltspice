from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp inverting amplifier")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 5m 10m)", at=(96, 160))
    circuit.voltage("VCC", "vcc", "0", "5", at=(320, 32))
    circuit.voltage("VEE", "vee", "0", "-5", at=(320, 320))
    circuit.resistor("RIN", "in", "sum", "10k", at=(256, 192), rotation="R90")
    circuit.resistor("RF", "out", "sum", "20k", at=(544, 128), rotation="R90")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(416, 176))
    circuit.resistor("RL", "out", "0", "10k", at=(672, 208))
    circuit.tran("0", "4m", "0", "5u")
    circuit.meas("TRAN", "vout_2ms", "FIND V(out) AT=2m")
    circuit.meas("TRAN", "gain_2ms", "PARAM vout_2ms/1")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_inverting.cir"),
        "asc": circuit.write_asc(output / "opamp_inverting.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
