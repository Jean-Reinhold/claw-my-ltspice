# GitHub Actions

GitHub Actions turns the local engineering loop into repeatable repository
evidence. The workflows build the Docker runtime, generate examples, render
schematics, run smoke simulations, upload artifacts, and publish GitHub Pages.

## Workflow Matrix

| Workflow | Trigger | Main Work | Artifacts |
| --- | --- | --- | --- |
| `CI` | push, pull request | unit tests and Docker Compose validation | test output and fallback artifacts |
| `Examples` | push, pull request, manual | generate examples without LTspice simulation | `runs/latest/**` |
| `Render Schematics` | push, pull request, manual | build Docker image and run `claw-spice docs assets` | rendered SVGs and terminal previews |
| `LTspice Docker Smoke` | push, schedule, manual | build Docker image, run doctor, run examples, render examples | `.log`, `.raw`, SVGs, summaries |
| `Manual LTspice Simulation` | manual | simulate a selected circuit path | selected run logs/raw/renders |
| `GitHub Pages` | push, manual | generate docs assets, build MkDocs, deploy Pages | public documentation site |

## Manual Simulation

Use the manual workflow for a specific circuit path, for example:

```text
examples/transient/sallen-key-lowpass/sallen_key_lowpass.cir
```

The expected review sequence is the same as local work: inspect `.log`, check
`.meas`, inspect traces, render the schematic, and report residual risk.

## Pages Publishing

The Pages workflow runs:

```bash
claw-spice docs assets
claw-spice docs build
```

That order matters because MkDocs references generated schematic previews,
expected waveform plots, FFT plots, and the generated full AI instruction page.

## Failure Triage

- Docker build failures usually indicate LTspice download, Wine package, or image
  build issues.
- Render failures usually indicate missing `.asy` symbols, bad `.asc` routing, or
  `ltspice-to-svg` behavior changes.
- Simulation failures should be diagnosed from uploaded `.log` files first.
- Pages failures usually mean a missing generated asset, broken nav target, or
  MkDocs build error.

## Licensing Note

The workflows build a local Docker image that downloads LTspice during the build.
The repository does not redistribute LTspice binaries or publish a LTspice image.
