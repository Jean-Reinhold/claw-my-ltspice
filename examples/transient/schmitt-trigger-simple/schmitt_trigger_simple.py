from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Configurable inverting Schmitt trigger")
    circuit.include(include_path)
    circuit.directive(".param RHYS=100k")
    circuit.directive(".param RREF=20k")
    circuit.directive(".param VTRIP=4.8*RREF/(RHYS+RREF)")
    circuit.voltage("VIN", "in", "0", "PWL(0 -2 2m 2 4m -2 6m 2 8m -2)", at=(96, 336))
    circuit.voltage("VCC", "vcc", "0", "5", at=(528, 64))
    circuit.voltage("VEE", "vee", "0", "-5", at=(528, 560))
    circuit.opamp("XU1", "trip", "in", "vcc", "vee", "out", at=(640, 304))
    circuit.resistor("RHYS", "out", "trip", "{RHYS}", at=(704, 160))
    circuit.resistor("RREF", "trip", "0", "{RREF}", at=(496, 336), symbol="res_v")
    circuit.resistor("RL", "out", "0", "10k", at=(944, 368), symbol="res_v")
    circuit.wire(64, 336, 320, 336)
    circuit.wire(320, 336, 320, 400)
    circuit.wire(320, 400, 640, 400)
    circuit.wire(496, 336, 640, 336)
    circuit.wire(640, 336, 640, 160)
    circuit.wire(640, 160, 704, 160)
    circuit.wire(800, 160, 944, 160)
    circuit.wire(944, 160, 944, 368)
    circuit.wire(784, 368, 1024, 368)
    circuit.wire(944, 368, 944, 464)
    circuit.wire(496, 432, 496, 464)
    circuit.iopin(64, 336, "in", "In")
    circuit.iopin(1024, 368, "out", "Out")
    circuit.flag(96, 432, "0")
    circuit.flag(496, 464, "0")
    circuit.flag(944, 464, "0")
    circuit.flag(528, 64, "vcc")
    circuit.flag(528, 160, "0")
    circuit.flag(528, 560, "vee")
    circuit.flag(528, 656, "0")
    circuit.opamp_supply_flags(640, 304)
    circuit.tran("0", "8m", "0", "2u")
    circuit.meas("TRAN", "upper_trip", "FIND V(in) WHEN V(out)=0 FALL=1")
    circuit.meas("TRAN", "lower_trip", "FIND V(in) WHEN V(out)=0 RISE=1")
    circuit.meas("TRAN", "hysteresis_width", "PARAM upper_trip-lower_trip")
    circuit.meas("TRAN", "expected_trip", "PARAM VTRIP")
    circuit.meas("TRAN", "vout_max", "MAX V(out) FROM=1m TO=8m")
    circuit.meas("TRAN", "vout_min", "MIN V(out) FROM=1m TO=8m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "schmitt_trigger_simple.cir"),
        "asc": circuit.write_asc(output / "schmitt_trigger_simple.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
