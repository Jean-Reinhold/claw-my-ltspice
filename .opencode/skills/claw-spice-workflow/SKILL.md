---
name: claw-spice-workflow
description: Use when working in the claw-spice repository, running ./claw-spice, using Docker-first LTspice automation, generating examples, rendering schematics, or coordinating OpenCode agents.
---

# claw-spice Workflow

## Core Rule

Use `./claw-spice` for project workflows. Do not install project dependencies on
the host. The host should only need Docker, Docker Compose, Git, and OpenCode.

## Required Engineering Loop

For meaningful circuit work:

1. State expected behavior.
2. Define objective `.meas` checks.
3. Generate or edit circuit code, `.cir`, `.net`, or `.asc`.
4. Run LTspice through `./claw-spice` when the Docker image is available.
5. Inspect `.log` warnings, errors, and measurements.
6. Inspect `.raw` traces or statistics when relevant.
7. Render the schematic.
8. Report evidence and unresolved risks.

## Commands

```bash
./claw-spice build
./claw-spice doctor
./claw-spice test
./claw-spice examples run
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice log summary runs/latest/rc_step.log
./claw-spice raw traces runs/latest/rc_step.raw
./claw-spice show examples/transient/rc-step/rc_step.asc
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
```

## Generated Artifacts

Use `runs/` for generated outputs. Do not commit `.raw`, `.log`, `.db`, or
temporary LTspice artifacts unless a fixture is explicitly needed for tests.

## Success Criteria

A circuit change is successful only when at least one of these is true:

- LTspice simulation ran and measurements match expected ranges.
- Simulation could not run, and the blocker is clearly identified.
- The change is documentation-only or test-only.

## OpenCode Rules

- Do not stop after writing a circuit.
- Do not hide failed measurements.
- Do not vendor unknown-license models.
- Use terminal rendering for quick schematic checks.
- Use host visual opening only through `./claw-spice show`.
