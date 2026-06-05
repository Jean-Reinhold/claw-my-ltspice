from __future__ import annotations

from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit() -> Circuit:
    circuit = Circuit("Passive RC spectrum split")
    circuit.voltage("VHIGH", "in", "mid", "SINE(0 0.6 4k)", at=(96, 176))
    circuit.voltage("VLOW", "mid", "0", "SINE(0 1 250)", at=(96, 432))
    circuit.resistor("RLP", "in", "low", "3.3k", at=(400, 176))
    circuit.capacitor("CLP", "low", "0", "47n", at=(608, 176))
    circuit.capacitor("CHP", "in", "high", "47n", at=(400, 384), symbol="cap_h")
    circuit.resistor("RHP", "high", "0", "3.3k", at=(608, 384), symbol="res_v")
    circuit.wire(64, 176, 400, 176)
    circuit.wire(320, 176, 320, 384)
    circuit.wire(320, 384, 400, 384)
    circuit.wire(496, 176, 768, 176)
    circuit.wire(608, 176, 608, 272)
    circuit.wire(496, 384, 768, 384)
    circuit.wire(96, 272, 96, 432)
    circuit.iopin(64, 176, "in", "In")
    circuit.iopin(768, 176, "low", "Out")
    circuit.iopin(768, 384, "high", "Out")
    circuit.flag(96, 528, "0")
    circuit.flag(608, 272, "0")
    circuit.flag(608, 480, "0")
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
