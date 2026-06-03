# GitHub Actions

`claw-spice` uses GitHub Actions as a simulation task surface.

## Workflows

- `ci.yml`: automatic unit/integration tests and fallback rendering.
- `examples.yml`: automatic example generation and render artifacts.
- `render.yml`: rendered schematic artifacts.
- `ltspice-smoke.yml`: full Docker LTspice smoke test.
- `simulate.yml`: manual selected-circuit simulation.
- `pages.yml`: generated gallery and GitHub Pages publishing.

## Manual Simulation

Use the `Manual LTspice Simulation` workflow and provide a circuit path such as:

```text
examples/transient/rc-step/rc_step.cir
```

The workflow uploads logs, raw files, schematic renders, and summaries as
artifacts.

## Pages Publishing

The Pages workflow builds the same Docker image, generates gallery artifacts,
builds MkDocs, and deploys through GitHub Pages.
