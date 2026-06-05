from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Passive RLC step ringing")
    circuit.voltage("VSTEP", "in", "0", "PULSE(0 5 0 1u 1u 10m 20m)", at=(96, 288))
    circuit.resistor("RS", "in", "n1", "47", at=(400, 288))
    circuit.inductor("L1", "n1", "out", "10m", at=(584, 288))
    circuit.capacitor("C1", "out", "0", "100n", at=(768, 288))
    circuit.resistor("RLOAD", "out", "0", "10k", at=(920, 288), symbol="res_v")
    circuit.wire(64, 288, 400, 288)
    circuit.wire(496, 288, 584, 288)
    circuit.wire(680, 288, 1040, 288)
    circuit.wire(768, 288, 768, 384)
    circuit.iopin(64, 288, "in", "In")
    circuit.iopin(1040, 288, "out", "Out")
    circuit.flag(96, 384, "0")
    circuit.flag(768, 384, "0")
    circuit.flag(920, 384, "0")
    circuit.tran("0", "4m", "0", "1u")
    circuit.meas("TRAN", "ring_peak", "MAX V(out) FROM=0 TO=2m")
    circuit.meas("TRAN", "ring_min", "MIN V(out) FROM=0 TO=2m")
    circuit.meas("TRAN", "vout_3ms", "FIND V(out) AT=3m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    circuit = create_circuit()
    return {
        "cir": circuit.write_netlist(output / "rlc_step_ringing.cir"),
        "asc": circuit.write_asc(output / "rlc_step_ringing.asc"),
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
