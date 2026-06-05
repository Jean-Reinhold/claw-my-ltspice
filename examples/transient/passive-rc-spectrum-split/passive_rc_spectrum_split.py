from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Passive RC spectrum split")
    circuit.voltage("VLOW", "mid", "0", "SINE(0 1 250)", at=(96, 288))
    circuit.voltage("VHIGH", "in", "mid", "SINE(0 0.6 4k)", at=(96, 160))
    circuit.resistor("RLP", "in", "low", "3.3k", at=(224, 160))
    circuit.capacitor("CLP", "low", "0", "47n", at=(384, 160))
    circuit.capacitor("CHP", "in", "high", "47n", at=(224, 320), rotation="R90")
    circuit.resistor("RHP", "high", "0", "3.3k", at=(384, 320), rotation="R90")
    circuit.wire(64, 160, 224, 160)
    circuit.wire(160, 160, 160, 320)
    circuit.wire(160, 320, 224, 320)
    circuit.wire(320, 160, 448, 160)
    circuit.wire(320, 320, 448, 320)
    circuit.wire(384, 256, 512, 256)
    circuit.wire(384, 416, 512, 416)
    circuit.wire(512, 256, 512, 416)
    circuit.wire(96, 256, 96, 288)
    circuit.wire(96, 384, 512, 384)
    circuit.iopin(64, 160, "in", "In")
    circuit.iopin(448, 160, "low", "Out")
    circuit.iopin(448, 320, "high", "Out")
    circuit.flag(96, 384, "0")
    circuit.flag(512, 384, "0")
    circuit.flag(384, 416, "0")
    circuit.directive(".options plotwinsize=0")
    circuit.tran("0", "20m", "0", "5u")
    circuit.meas("TRAN", "vin_rms", "RMS V(in) FROM=4m TO=20m")
    circuit.meas("TRAN", "low_rms", "RMS V(low) FROM=4m TO=20m")
    circuit.meas("TRAN", "high_rms", "RMS V(high) FROM=4m TO=20m")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    circuit = create_circuit()
    return {
        "cir": circuit.write_netlist(output / "passive_rc_spectrum_split.cir"),
        "asc": circuit.write_asc(output / "passive_rc_spectrum_split.asc"),
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
