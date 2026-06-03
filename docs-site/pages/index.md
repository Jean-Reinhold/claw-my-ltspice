# claw-spice

OpenCode-assisted LTspice automation with Docker, code-generated schematics,
terminal rendering, transient simulation results, and GitHub Actions workflows.

![claw-spice workflow](../assets/images/workflow.svg)

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
- Terminal and SVG schematic rendering.
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
