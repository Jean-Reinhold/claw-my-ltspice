from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Diode clipper harmonic spectrum")
    circuit.voltage("VIN", "in", "0", "SINE(0 3 1k)", at=(96, 256))
    circuit.resistor("RSRC", "in", "clip", "1k", at=(224, 256))
    circuit.resistor("RLOAD", "clip", "0", "10k", at=(384, 256), rotation="R90")
    circuit.diode("DCLIP", "clip", "0", "DCLAW", at=(480, 256))
    circuit.wire(64, 256, 224, 256)
    circuit.wire(320, 256, 480, 256)
    circuit.wire(384, 256, 384, 352)
    circuit.wire(544, 256, 544, 352)
    circuit.wire(96, 352, 544, 352)
    circuit.iopin(64, 256, "in", "In")
    circuit.iopin(448, 256, "clip", "Out")
    circuit.flag(96, 352, "0")
    circuit.flag(384, 352, "0")
    circuit.flag(544, 352, "0")
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
