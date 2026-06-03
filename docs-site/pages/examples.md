# Examples

## RC Step Response

The first example is a 1 kOhm / 1 uF RC step response. The expected time
constant is approximately 1 ms.

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice show examples/transient/rc-step/rc_step.asc
```

Measurements:

- `vout_max`: maximum output voltage.
- `vout_ss`: output voltage near the end of the run.
- `tau_rise`: time at which `V(out)` reaches 63.2% of 5 V.

Future examples will cover BJT amplifiers, generic op-amp buffers, parameter
sweeps, and model-library workflows.
