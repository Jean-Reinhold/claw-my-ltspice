from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("RC step response")
    circuit.voltage("V1", "in", "0", "PULSE(0 5 0 1n 1n 5m 10m)", at=(96, 112))
    circuit.resistor("R1", "in", "out", "1k", at=(176, 112))
    circuit.capacitor("C1", "out", "0", "1u", at=(352, 112))
    circuit.wire(64, 112, 176, 112)
    circuit.wire(272, 112, 416, 112)
    circuit.wire(96, 208, 352, 208)
    circuit.iopin(64, 112, "in", "In")
    circuit.iopin(416, 112, "out", "Out")
    circuit.flag(96, 208, "0")
    circuit.flag(352, 208, "0")
    circuit.tran("0", "6m", "0", "10u")
    circuit.meas("TRAN", "vout_max", "MAX V(out)")
    circuit.meas("TRAN", "vout_ss", "FIND V(out) AT=5m")
    circuit.meas("TRAN", "tau_rise", "WHEN V(out)=3.16 RISE=1")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    circuit = create_circuit()
    cir = circuit.write_netlist(output / "rc_step.cir")
    asc = circuit.write_asc(output / "rc_step.asc")
    return {"cir": cir, "asc": asc}


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
