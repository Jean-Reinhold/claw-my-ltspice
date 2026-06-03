# Signal Plots

`claw-spice raw plot` creates SVG plots from LTspice `.raw` files on demand. It
uses `time` as the x-axis by default and can plot one or more traces.

```bash
./claw-spice raw traces runs/latest/rc_step.raw
./claw-spice raw plot runs/latest/rc_step.raw V(out) --output runs/latest/rc_step_vout.svg
./claw-spice raw plot runs/latest/opamp_summing.raw V(in1) V(in2) V(out) --output runs/latest/opamp_summing.svg
```

Options:

- `--x <trace>` selects a different x-axis trace.
- `--title <text>` sets the plot title.
- `--png` also converts the SVG to PNG when `rsvg-convert` or `resvg` is available.

## Expected Example Plots

These documentation plots show the expected signal shape for the examples. Real
simulation plots should be generated from each run's `.raw` output.

![RC step output plot](assets/plots/rc-step-vout.svg)

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

![Buffered active low-pass plot](assets/plots/opamp-active-lowpass.svg)
