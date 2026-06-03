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

## Dependency Policy

Do not run host `pip`, `uv`, `brew`, `apt`, or `npm` for project dependencies.
The host should need Docker, Docker Compose, Git, and OpenCode only.

## Model Policy

Do not commit unknown-license SPICE model files. Track intended models and
license/source status in `models/manifest.toml`.

## OpenCode

Project OpenCode agents and skills live under `.opencode/`. Restart OpenCode
after changing them.
