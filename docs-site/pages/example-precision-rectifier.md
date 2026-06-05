# Precision Rectifier Walkthrough

The precision rectifier demonstrates an active nonlinear circuit using only
repo-owned educational models.

<div class="schematic-frame" markdown>
![Rendered precision rectifier schematic](assets/generated/precision-rectifier.svg)
</div>

## Theory

A passive diode rectifier loses roughly one diode forward drop, which is a large
error when the input is small. In a precision rectifier, the op-amp drives the
diode so feedback is taken from the rectified output node. During positive
half-cycles the op-amp compensates the diode drop. During negative half-cycles
the diode disconnects and the load returns the output to ground.

## Model Policy

The diode is an inline repo-owned `DCLAW` educational model. It is recorded in
`models/manifest.toml`. No vendor diode model is copied from the source theory
PDFs or external libraries.

## Commands

```bash
./claw-spice code build examples/transient/precision-rectifier/precision_rectifier.py
./claw-spice sim run examples/transient/precision-rectifier/precision_rectifier.cir
./claw-spice log summary examples/transient/precision-rectifier/precision_rectifier.log
./claw-spice raw plot examples/transient/precision-rectifier/precision_rectifier.raw V(in) V(rect) --output runs/latest/precision_rectifier.svg
./claw-spice show examples/transient/precision-rectifier/precision_rectifier.asc --terminal
```

## Measurements

- `vrect_max`: maximum rectified output over the settled window.
- `vrect_min`: minimum rectified output over the settled window.
- `vrect_avg`: average rectified output over the settled window.

![Precision rectifier response plot](assets/plots/precision-rectifier.svg)

## Failure Checks

- Wrong diode polarity produces little or no positive rectification.
- Missing load path leaves the rectified node floating.
- Excessive input amplitude clips the educational op-amp model at the rails.
- Too-large timestep can hide diode switching details.
