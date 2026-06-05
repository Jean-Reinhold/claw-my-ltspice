from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Passive RLC step ringing")
    circuit.voltage("VSTEP", "in", "0", "PULSE(0 5 0 1u 1u 10m 20m)", at=(96, 256))
    circuit.resistor("RS", "in", "n1", "47", at=(224, 256))
    circuit.inductor("L1", "n1", "out", "10m", at=(384, 256))
    circuit.capacitor("C1", "out", "0", "100n", at=(560, 256))
    circuit.resistor("RLOAD", "out", "0", "10k", at=(704, 256), rotation="R90")
    circuit.wire(64, 256, 224, 256)
    circuit.wire(320, 256, 384, 256)
    circuit.wire(480, 256, 768, 256)
    circuit.wire(560, 256, 560, 352)
    circuit.wire(704, 256, 704, 352)
    circuit.wire(96, 352, 704, 352)
    circuit.iopin(64, 256, "in", "In")
    circuit.iopin(768, 256, "out", "Out")
    circuit.flag(96, 352, "0")
    circuit.flag(560, 352, "0")
    circuit.flag(704, 352, "0")
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
