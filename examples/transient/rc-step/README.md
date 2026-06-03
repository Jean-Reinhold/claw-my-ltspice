# RC Step Response

Minimal transient example used as the first `claw-spice` smoke test.

The circuit applies a 5 V step through a 1 kOhm resistor into a 1 uF capacitor.
The expected time constant is approximately 1 ms.

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice show examples/transient/rc-step/rc_step.asc
```

Measurements:

- `vout_max`: maximum output voltage.
- `vout_ss`: output voltage near the end of the run.
- `tau_rise`: time at which `V(out)` reaches 63.2% of 5 V.
