from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp inverting summing amplifier")
    circuit.include(include_path)
    circuit.voltage("VIN1", "in1", "0", "PULSE(0 0.5 0 1u 1u 5m 10m)", at=(96, 144))
    circuit.voltage("VIN2", "in2", "0", "PULSE(0 0.25 1m 1u 1u 5m 10m)", at=(96, 288))
    circuit.voltage("VCC", "vcc", "0", "5", at=(320, 32))
    circuit.voltage("VEE", "vee", "0", "-5", at=(320, 384))
    circuit.resistor("R1", "in1", "sum", "10k", at=(256, 176), rotation="R90")
    circuit.resistor("R2", "in2", "sum", "20k", at=(256, 320), rotation="R90")
    circuit.resistor("RF", "out", "sum", "20k", at=(544, 128), rotation="R90")
    circuit.opamp("XU1", "0", "sum", "vcc", "vee", "out", at=(416, 208))
    circuit.resistor("RL", "out", "0", "10k", at=(672, 240), rotation="R90")
    circuit.tran("0", "4m", "0", "5u")
    circuit.meas("TRAN", "vout_2ms", "FIND V(out) AT=2m")
    circuit.meas("TRAN", "vout_3ms", "FIND V(out) AT=3m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "opamp_summing.cir"),
        "asc": circuit.write_asc(output / "opamp_summing.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
