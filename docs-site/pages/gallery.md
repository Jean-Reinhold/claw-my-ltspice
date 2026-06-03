# Gallery

Rendered gallery artifacts are produced by GitHub Actions and the Dockerized
toolchain. The Pages workflow runs `claw-spice docs assets` before building
MkDocs, which refreshes schematic previews under `assets/generated/` with the
real `ltspice_to_svg` renderer and plot previews under `assets/plots/`.

## RC Step Response

![Rendered RC step response schematic](assets/generated/rc-step.svg)

## Op-Amp Voltage Follower

![Rendered op-amp voltage follower schematic](assets/generated/opamp-voltage-follower.svg)

## Op-Amp Non-Inverting Gain

![Rendered op-amp non-inverting schematic](assets/generated/opamp-noninverting.svg)

## Op-Amp Inverting Gain

![Rendered op-amp inverting schematic](assets/generated/opamp-inverting.svg)

## Op-Amp Inverting Summing Amplifier

![Rendered op-amp summing schematic](assets/generated/opamp-summing.svg)

## Op-Amp Difference Amplifier

![Rendered op-amp difference schematic](assets/generated/opamp-difference.svg)

## Op-Amp Buffered Active Low-Pass

![Rendered op-amp active low-pass schematic](assets/generated/opamp-active-lowpass.svg)

## Render Command

```bash
./claw-spice examples render
```

Artifacts are generated under `runs/latest/` during CI and copied into the Pages
asset directory for publication.

## Signal Plots

Waveform plots are generated on demand from LTspice `.raw` files:

```bash
./claw-spice raw plot runs/latest/rc_step.raw V(out) --output runs/latest/rc_step_vout.svg
```

The documentation also includes expected signal-shape plots for each example:

![RC step output plot](assets/plots/rc-step-vout.svg)

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

![Buffered active low-pass plot](assets/plots/opamp-active-lowpass.svg)

## Terminal Preview

`claw-spice` can render a schematic in the terminal:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
```

## Visual Preview

`claw-spice` can render SVG inside Docker and open it on the host:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc
```
