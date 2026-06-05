from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Diode clipper harmonic spectrum")
    circuit.voltage("VIN", "in", "0", "SINE(0 3 1k)", at=(96, 288))
    circuit.resistor("RSRC", "in", "clip", "1k", at=(384, 288))
    circuit.resistor("RLOAD", "clip", "0", "10k", at=(600, 288), symbol="res_v")
    circuit.diode("DCLIP", "clip", "0", "DCLAW", at=(760, 288), symbol="diode_v")
    circuit.wire(64, 288, 384, 288)
    circuit.wire(480, 288, 920, 288)
    circuit.wire(600, 384, 760, 384)
    circuit.iopin(64, 288, "in", "In")
    circuit.iopin(920, 288, "clip", "Out")
    circuit.flag(96, 384, "0")
    circuit.flag(600, 384, "0")
    circuit.flag(760, 384, "0")
    circuit.directive(".model DCLAW D(Is=2n Rs=0.25 N=1.8 Cjo=2p M=0.33 Eg=1.11)")
    circuit.directive(".options plotwinsize=0")
    circuit.tran("0", "8m", "0", "1u")
    circuit.meas("TRAN", "clip_max", "MAX V(clip) FROM=2m TO=8m")
    circuit.meas("TRAN", "clip_min", "MIN V(clip) FROM=2m TO=8m")
    circuit.meas("TRAN", "clip_avg", "AVG V(clip) FROM=2m TO=8m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    circuit = create_circuit()
    return {
        "cir": circuit.write_netlist(output / "diode_clipper_spectrum.cir"),
        "asc": circuit.write_asc(output / "diode_clipper_spectrum.asc"),
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
