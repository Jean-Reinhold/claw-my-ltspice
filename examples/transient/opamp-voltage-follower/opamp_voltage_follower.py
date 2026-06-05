from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Generic op-amp voltage follower")
    circuit.include(include_path)
    circuit.voltage("VIN", "in", "0", "PULSE(0 1 0 1u 1u 5m 10m)", at=(96, 192))
    circuit.voltage("VCC", "vcc", "0", "5", at=(288, 48))
    circuit.voltage("VEE", "vee", "0", "-5", at=(288, 336))
    circuit.opamp("XU1", "in", "out", "vcc", "vee", "out", at=(384, 160))
    circuit.resistor("RL", "out", "0", "10k", at=(640, 224), symbol="res_v")
    circuit.wire(64, 192, 384, 192)
    circuit.wire(528, 224, 704, 224)
    circuit.wire(528, 224, 560, 224)
    circuit.wire(560, 224, 560, 336)
    circuit.wire(560, 336, 384, 336)
    circuit.wire(384, 336, 384, 256)
    circuit.iopin(64, 192, "in", "In")
    circuit.iopin(704, 224, "out", "Out")
    circuit.flag(96, 288, "0")
    circuit.flag(640, 320, "0")
    circuit.flag(288, 48, "vcc")
    circuit.flag(288, 144, "0")
    circuit.flag(288, 336, "vee")
    circuit.flag(288, 432, "0")
    circuit.opamp_supply_flags(384, 160)
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
