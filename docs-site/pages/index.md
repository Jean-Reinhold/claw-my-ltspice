# claw-spice

OpenCode-assisted LTspice automation with Docker, code-generated schematics,
rendered example previews, terminal rendering, transient simulation results,
GitHub Pages, and GitHub Actions workflows.

![claw-spice workflow](assets/images/workflow.svg)

## Why

LTspice is excellent, but automated workflows around it are usually brittle.
`claw-spice` makes LTspice reproducible from the terminal and useful for AI
assistants by standardizing the loop:

```text
code / schematic
→ LTspice Docker simulation
→ .log and .raw analysis
→ generated SVG schematic
→ terminal preview
→ GitHub Actions artifacts
```

## Highlights

- Docker-first LTspice runtime through Wine and Xvfb.
- `./claw-spice` host wrapper with no host Python dependency.
- Code-generated `.cir` netlists and `.asc` schematics.
- Real-renderer SVG previews for examples and generated SVG gallery assets.
- Terminal and SVG schematic rendering.
- On-demand `.raw` waveform plotting to SVG/PNG.
- OpenCode skills for circuit design, simulation, convergence, measurements,
  model policy, rendering, and GitHub Actions.
- CI, manual simulation, render, and Pages workflow scaffolding.

## First Command

```bash
./claw-spice doctor
```

## First Circuit

```bash
./claw-spice examples run
./claw-spice show examples/transient/rc-step/rc_step.asc
```

![Rendered RC step response schematic](assets/generated/rc-step.svg)

## Rendered Examples

The Pages build includes stable SVG previews generated from the example
schematics and expected signal plots. These assets are produced by
`claw-spice docs assets` before the MkDocs site is built.

[Open the gallery](gallery.md)

## Signal Plots

Generate waveform plots directly from LTspice `.raw` files:

```bash
./claw-spice raw plot runs/latest/rc_step.raw V(out) --output runs/latest/rc_step_vout.svg
```

[Open the signal plotting guide](signal-plots.md)
