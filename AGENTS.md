# AGENTS.md

This repository is Docker-first LTspice automation. Agents must use the
project wrapper and must not install project dependencies on the host.

## Required Commands

Use these commands for normal work:

```bash
./claw-spice doctor
./claw-spice test
./claw-spice examples list
./claw-spice examples run --skip-sim
./claw-spice code build <example.py>
./claw-spice sim run <circuit.cir>
./claw-spice log summary <circuit.log>
./claw-spice raw traces <circuit.raw>
./claw-spice raw plot <circuit.raw> V(out) --output <plot.svg>
./claw-spice show <schematic.asc> --terminal
./claw-spice show <schematic.asc>
./claw-spice docs assets
```

## Engineering Loop

For circuit work, do not stop after writing a file. Follow this loop:

1. State expected behavior and measurements.
2. Create or modify code, `.cir`, `.net`, or `.asc`.
3. Run tests and example generation.
4. Run LTspice through Docker when available.
5. Inspect `.log` warnings, errors, and `.meas` results.
6. Inspect `.raw` traces or stats when relevant.
7. Render the schematic in terminal and visually if requested.
8. Report evidence, failures, and residual risks.

## Schematic Quality Gate

Rendered schematics must look like real readable circuit schematics, not loose
labels, floating ground symbols, or decorative diagrams. Treat bad SVG output as
a bug in the `.asc`/IR/source layout, not as an acceptable render.

Before accepting schematic work:

1. Confirm the `.asc` contains explicit `WIRE` routing for non-trivial circuits.
2. Confirm all rendered components have symbol shapes; `Symbol definition not found`
   from `ltspice-to-svg` is a failure.
3. Confirm labels are attached to wires or pins and are readable, not rotated or
   scattered across blank space.
4. Confirm directives are grouped away from components and do not overlap labels.
5. Fix source layout, component coordinates, wires, flags, or bundled `.asy`
   symbols when the rendered SVG is ugly. Do not solve this by adding fake
   fallback schematic art.

## Dependency Policy

Do not run host `pip`, `uv`, `brew`, `apt`, or `npm` for project dependencies.
The host should need Docker, Docker Compose, Git, and OpenCode only.

## Model Policy

Do not commit unknown-license SPICE model files. Track intended models and
license/source status in `models/manifest.toml`.

## OpenCode

Project OpenCode agents and skills live under `.opencode/`. Restart OpenCode
after changing them.
