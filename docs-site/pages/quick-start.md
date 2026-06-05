# Quick Start

This page walks through the shortest useful path from a clean checkout to a
rendered schematic, an LTspice simulation, waveform plots, and documentation
assets.

## Requirements On The Host

Install these on the host:

- Docker
- Docker Compose
- Git
- OpenCode, if using the included agents and skills

Do not install LTspice, Wine, Python packages, `chafa`, or schematic rendering
tools locally for normal usage. Docker handles those dependencies.

## Build The Runtime

```bash
./claw-spice build
```

The image downloads LTspice from Analog Devices during the build. This repo does
not redistribute LTspice binaries.

If the local Wine/LTspice build is problematic on the host, the optional prebuilt
fallback can be used for local development:

```bash
./claw-spice build-prebuilt
```

The normal `Dockerfile` remains the clean path because it downloads LTspice from
Analog Devices during the user's build rather than redistributing LTspice.

## Diagnose The Toolchain

```bash
./claw-spice doctor
```

Expected important passes:

- `ltspice_wrapper` for batch simulation.
- `wine` and `xvfb` for headless LTspice.
- `ltspice_to_svg` for real schematic rendering.
- `mkdocs` for GitHub Pages documentation.

Missing optional raster tools only affect PNG conversion. Missing
`ltspice_to_svg` means schematic rendering should fail clearly.

## Generate And Render A Circuit

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice show examples/transient/rc-step/rc_step.asc
```

The generator writes a deterministic `.cir` netlist and `.asc` schematic. The
`show` command renders the `.asc` through the real renderer and opens the SVG on
the host.

<div class="schematic-frame" markdown>
![Rendered RC step response schematic](assets/generated/rc-step.svg)
</div>

## Simulate And Inspect

```bash
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice raw traces examples/transient/rc-step/rc_step.raw
```

The log summary is the first quality gate. It should be checked before trusting
any plot because a waveform file can exist even when a simulation produced
warnings or unexpected measurement values.

## Plot The Waveforms

```bash
./claw-spice raw plot examples/transient/rc-step/rc_step.raw V(out) --output runs/latest/rc_step_vout.svg
```

Expected shape:

![RC step output plot](assets/plots/rc-step-vout.svg)

## Generate The Documentation Assets

```bash
./claw-spice docs assets
./claw-spice docs build
```

This regenerates the rendered schematic gallery, expected waveform plots, FFT
plots, and the full AI instruction reference page. The Pages workflow runs these
same commands before publishing.
