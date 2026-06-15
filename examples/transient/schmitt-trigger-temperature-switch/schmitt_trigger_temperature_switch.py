from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit


def create_circuit(include_path: str = "../../lib/claw_opamps.lib") -> Circuit:
    circuit = Circuit("Noisy temperature switch Schmitt trigger")
    circuit.include(include_path)
    circuit.directive(".param RIN=100k")
    circuit.directive(".param RHYS=1Meg")
    circuit.directive(".param VREF=2.5")
    circuit.directive(".param VOUT_H=4.8")
    circuit.directive(".param VOUT_L=0.2")
    circuit.directive(".param UPPER_TRIP=VREF*(1+RIN/RHYS)-VOUT_L*(RIN/RHYS)")
    circuit.directive(".param LOWER_TRIP=VREF*(1+RIN/RHYS)-VOUT_H*(RIN/RHYS)")
    circuit.voltage("VRIPPLE", "sensor_raw", "temp_base", "SINE(0 80m 600)", at=(96, 352))
    circuit.voltage("VTEMP", "temp_base", "0", "PWL(0 2.0 50m 3.1 100m 2.0 150m 3.1 200m 2.0)", at=(96, 544))
    circuit.voltage("VCC", "vcc", "0", "5", at=(448, 64))
    circuit.resistor("RFLT", "sensor_raw", "sense", "4.7k", at=(320, 352))
    circuit.capacitor("CFILT", "sense", "0", "1u", at=(496, 352))
    circuit.resistor("RSENSE", "sense", "0", "1Meg", at=(608, 352), symbol="res_v")
    circuit.resistor("RIN", "sense", "cmp", "{RIN}", at=(720, 432))
    circuit.resistor("RHYS", "fan_en", "cmp", "{RHYS}", at=(928, 240))
    circuit.resistor("RTOP", "vcc", "ref", "100k", at=(848, 32), symbol="res_v")
    circuit.resistor("RBOT", "ref", "0", "100k", at=(848, 192), symbol="res_v")
    circuit.capacitor("CREF", "ref", "0", "100n", at=(736, 192))
    circuit.opamp("XU1", "cmp", "ref", "vcc", "0", "fan_en", at=(976, 400))
    circuit.resistor("RLOAD", "fan_en", "0", "10k", at=(1216, 464), symbol="res_v")
    circuit.wire(96, 448, 96, 544)
    circuit.wire(64, 352, 320, 352)
    circuit.wire(416, 352, 672, 352)
    circuit.wire(672, 352, 672, 432)
    circuit.wire(672, 432, 720, 432)
    circuit.wire(816, 432, 896, 432)
    circuit.wire(896, 432, 976, 432)
    circuit.wire(896, 432, 896, 240)
    circuit.wire(896, 240, 928, 240)
    circuit.wire(1024, 240, 1216, 240)
    circuit.wire(1216, 240, 1216, 464)
    circuit.wire(1120, 464, 1328, 464)
    circuit.wire(1216, 464, 1216, 560)
    circuit.wire(496, 448, 608, 448)
    circuit.wire(608, 448, 608, 496)
    circuit.wire(736, 192, 848, 192)
    circuit.wire(848, 128, 848, 192)
    circuit.wire(736, 288, 848, 288)
    circuit.wire(848, 192, 864, 192)
    circuit.wire(864, 192, 864, 496)
    circuit.wire(864, 496, 976, 496)
    circuit.iopin(64, 352, "sensor_raw", "In")
    circuit.iopin(1328, 464, "fan_en", "Out")
    circuit.flag(96, 640, "0")
    circuit.flag(448, 64, "vcc")
    circuit.flag(448, 160, "0")
    circuit.flag(608, 496, "0")
    circuit.flag(848, 32, "vcc")
    circuit.flag(848, 288, "0")
    circuit.flag(736, 288, "0")
    circuit.flag(1216, 560, "0")
    circuit.flag(416, 352, "sense")
    circuit.flag(864, 496, "ref")
    circuit.flag(896, 432, "cmp")
    circuit.opamp_supply_flags(976, 400, vee="0")
    circuit.tran("0", "200m", "0", "20u")
    circuit.meas("TRAN", "turn_on_sensor", "FIND V(sense) WHEN V(fan_en)=2.5 RISE=1")
    circuit.meas("TRAN", "turn_off_sensor", "FIND V(sense) WHEN V(fan_en)=2.5 FALL=1")
    circuit.meas("TRAN", "hysteresis_width", "PARAM turn_on_sensor-turn_off_sensor")
    circuit.meas("TRAN", "expected_upper", "PARAM UPPER_TRIP")
    circuit.meas("TRAN", "expected_lower", "PARAM LOWER_TRIP")
    circuit.meas("TRAN", "fan_on_time", "TRIG V(fan_en) VAL=2.5 RISE=1 TARG V(fan_en) VAL=2.5 FALL=1")
    circuit.meas("TRAN", "fan_en_avg", "AVG V(fan_en) FROM=0 TO=200m")
    circuit.meas("TRAN", "raw_ripple_pp", "PP V(sensor_raw) FROM=20m TO=25m")
    circuit.meas("TRAN", "filtered_ripple_pp", "PP V(sense) FROM=20m TO=25m")
    circuit.meas("TRAN", "ripple_reduction", "PARAM raw_ripple_pp/filtered_ripple_pp")
    return circuit


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    library = output / "claw_opamps.lib"
    shutil.copyfile(Path(__file__).parents[2] / "lib" / "claw_opamps.lib", library)
    circuit = create_circuit("claw_opamps.lib")
    return {
        "cir": circuit.write_netlist(output / "schmitt_trigger_temperature_switch.cir"),
        "asc": circuit.write_asc(output / "schmitt_trigger_temperature_switch.asc"),
        "lib": library,
    }


if __name__ == "__main__":
    print(build(Path(__file__).parent / "generated"))
