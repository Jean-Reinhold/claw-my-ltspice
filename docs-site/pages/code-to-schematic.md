# Code To Schematic

`claw-spice` includes a small circuit IR that can generate both LTspice netlists
and `.asc` schematics.

```python
from claw_spice.ir import Circuit

circuit = Circuit("RC step response")
circuit.voltage("V1", "in", "0", "PULSE(0 5 0 1n 1n 5m 10m)")
circuit.resistor("R1", "in", "out", "1k")
circuit.capacitor("C1", "out", "0", "1u")
circuit.tran("0", "6m", "0", "10u")
circuit.meas("TRAN", "vout_max", "MAX V(out)")
circuit.write_netlist("rc_step.cir")
circuit.write_asc("rc_step.asc")
```

The first goal is deterministic, readable schematics for simple analog circuits.
As the renderer matures, layout hints and higher-level blocks can improve larger
schematics.
