# claw-spice

OpenCode-assisted LTspice automation for Docker-first circuit simulation,
code-generated schematics, terminal rendering, transient simulation results,
and GitHub Actions workflows.

`claw-spice` turns LTspice into a reproducible terminal-first workflow for
humans and OpenCode agents. The normal workflow needs only Docker, Git, and
OpenCode on the host. LTspice, Wine, Python, schematic rendering, terminal
preview tooling, and test dependencies live inside Docker.

## Features

- Dockerized LTspice execution using Wine and Xvfb.
- Host wrapper: `./claw-spice`.
- Code-generated LTspice netlists and `.asc` schematics.
- Transient simulation-first workflow with `.meas` summaries.
- SVG schematic rendering and host-side opening.
- Terminal schematic previews via `chafa`.
- OpenCode agents and skills for LTspice design, simulation, debugging, model
  handling, schematic layout, and GitHub Actions.
- GitHub Actions scaffolding for CI, simulation smoke tests, render artifacts,
  manual simulation runs, and GitHub Pages publishing.

## Quick Start

```bash
git clone git@github.com:Jean-Reinhold/claw-spice.git
cd claw-spice
./claw-spice build
./claw-spice doctor
./claw-spice examples run
./claw-spice show examples/transient/rc-step/rc_step.asc
```

You can also call Docker Compose directly:

```bash
docker compose run --rm claw-spice claw-spice doctor
```

## Example Workflow

Generate a circuit from code:

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
```

Run a transient simulation:

```bash
./claw-spice sim run examples/transient/rc-step/rc_step.cir
```

Inspect the log:

```bash
./claw-spice log summary runs/latest/rc_step.log
```

Render and open the schematic:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc
```

Render in the terminal:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
```

## Docker-First Dependencies

Do not install project dependencies on the host. The host wrapper runs the
containerized CLI. The only normal host dependencies are:

- Docker
- Docker Compose
- Git
- OpenCode, if using the included agents and skills

## LTspice In Docker

LTspice has no native Linux Docker runtime. This project runs the Windows
LTspice build inside a Linux container through Wine and Xvfb. On Apple Silicon,
the container runs as `linux/amd64` under emulation.

This repository does not redistribute LTspice. The Dockerfile downloads LTspice
from Analog Devices during image build. Review `NOTICE.md` before publishing any
container image that contains LTspice.

## OpenCode Skills

The repository includes project-local OpenCode skills and agents under
`.opencode/`. They instruct agents to:

- Use `./claw-spice`, not host package managers.
- Run LTspice after circuit changes.
- Inspect `.log` files and `.meas` results.
- Render schematics after generating or changing them.
- Track component model sources and licenses.
- Use GitHub Actions as a reproducible task surface.

Restart OpenCode after changing `.opencode` files; OpenCode loads config at
startup.

## GitHub Pages

The Pages scaffold under `docs-site/` is designed to publish generated
schematics, waveform plots, terminal previews, and measurement summaries after
the simulation toolchain is ready.

Build locally through Docker:

```bash
./claw-spice docs build
```

Serve locally through Docker:

```bash
./claw-spice docs serve
```

## Repository Status

This is the initial project setup. The next major validation step is a full
Docker LTspice build and smoke simulation on both GitHub Actions and local
Apple Silicon Docker.
