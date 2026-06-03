---
name: ltspice-transient-simulation
description: Use when creating, running, debugging, or interpreting LTspice transient simulations using .tran, PULSE, SINE, PWL, startup, initial conditions, waveforms, and time-domain measurements.
---

# LTspice Transient Simulation

## .tran Guidance

Use explicit stop time and max timestep for edge-sensitive circuits:

```spice
.tran 0 5m 0 10u
.tran 0 10m 1m 5u
.tran 0 5m 0 10u startup
```

Do not rely on default timesteps for fast edges, switching behavior, or rise
time measurements.

## Sources

Use realistic rise and fall times:

```spice
V1 in 0 PULSE(0 5 0 1n 1n 1m 2m)
V2 in 0 SINE(0 1 1k)
```

For exact stimuli, use PWL and keep referenced files in the repo.

## Initial Conditions

- `.nodeset` is a solver hint.
- `.ic` forces initial conditions.
- `UIC` skips the operating point. Use it only when that is intentional.
- `startup` ramps independent sources from zero. Use it deliberately.

## Measurements

Examples:

```spice
.meas TRAN vout_max MAX V(out)
.meas TRAN vout_min MIN V(out)
.meas TRAN vout_pp PP V(out)
.meas TRAN vout_avg AVG V(out) FROM=1m TO=5m
.meas TRAN rise_time TRIG V(out) VAL=0.5 RISE=1 TARG V(out) VAL=4.5 RISE=1
.meas TRAN tau_rise WHEN V(out)=3.16 RISE=1
```

RISE, FALL, and CROSS counts start at 1.

## OpenCode Rule

Never claim transient success because `.raw` exists. Check `.log`, `.meas`, and
the waveform traces or statistics.
