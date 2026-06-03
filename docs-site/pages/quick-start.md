# Quick Start

## Requirements

Install these on the host:

- Docker
- Docker Compose
- Git
- OpenCode, if using the included agents and skills

Do not install LTspice, Wine, Python packages, `chafa`, or schematic rendering
tools locally for normal usage. Docker handles those dependencies.

## Build

```bash
./claw-spice build
```

The image downloads LTspice from Analog Devices during the build. This repo does
not redistribute LTspice binaries.

## Diagnose

```bash
./claw-spice doctor
```

## Generate And Render

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice show examples/transient/rc-step/rc_step.asc
```

## Simulate

```bash
./claw-spice sim run examples/transient/rc-step/rc_step.cir
```

## Inspect Results

```bash
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice raw traces examples/transient/rc-step/rc_step.raw
```
