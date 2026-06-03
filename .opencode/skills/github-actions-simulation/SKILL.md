---
name: github-actions-simulation
description: Use when creating or modifying GitHub Actions for LTspice Docker builds, simulation smoke tests, schematic rendering, artifact uploads, job summaries, and GitHub Pages publishing.
---

# GitHub Actions Simulation Workflows

## CI Principles

- Use the same Docker image and `./claw-spice` commands as local workflows.
- Do not install LTspice or Python dependencies directly on the runner outside
  Docker.
- Upload `.log`, `.raw`, `.svg`, `.png`, terminal previews, and summaries as
  artifacts when relevant.
- Fail workflows on failed measurements, not only crashed commands.
- Do not publish LTspice-containing images until redistribution terms are clear.

## Workflow Types

- `ci.yml`: tests and static checks.
- `ltspice-smoke.yml`: Docker LTspice transient smoke test.
- `simulate.yml`: manual selected-circuit simulation.
- `render.yml`: schematic rendering artifacts.
- `examples.yml`: example suite.
- `pages.yml`: generated gallery and GitHub Pages deploy.

## Job Summary

Each simulation workflow should write a human-readable summary with:

- Circuit path.
- Docker image/build status.
- Simulation command.
- Measurement table.
- Warnings/errors.
- Artifact links.

## OpenCode Rule

A simulation workflow is incomplete unless it uploads logs and writes a
measurement summary.
