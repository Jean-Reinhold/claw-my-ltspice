# OpenCode Skills

The repository includes project-local OpenCode agents and skills under
`.opencode/`.

## Agents

- `ltspice-sim-engineer`: design, simulate, inspect, render, summarize.
- `circuit-design-reviewer`: review topology and simulation realism.
- `schematic-generator`: generate and render `.asc` schematics.
- `spice-model-librarian`: manage models, licensing, pin order, manifests.
- `simulation-debugger`: diagnose LTspice failures and convergence issues.
- `repo-maintainer`: maintain docs, workflows, tests, and repo polish.

## Skills

- `claw-spice-workflow`
- `ltspice-circuit-design`
- `ltspice-transient-simulation`
- `ltspice-debugging-convergence`
- `ltspice-measurements-analysis`
- `ltspice-models-components`
- `code-to-schematic`
- `schematic-layout-rendering`
- `github-actions-simulation`

The skills require agents to run simulations, inspect logs, validate
measurements, render schematics, and report evidence before claiming success.

Restart OpenCode after changing `.opencode` files.
