# Engineering Workflow

This repository uses an evidence-first workflow for both humans and AI agents.
The output is not complete when files are written; it is complete when the circuit
behavior, simulation evidence, rendered schematic, and documentation all agree.

## Definition Of Done

1. State expected behavior and measurable outcomes.
2. Create or modify the generator, `.cir`, `.net`, or `.asc` source.
3. Generate deterministic `.cir` and `.asc` artifacts.
4. Run tests and example generation.
5. Run LTspice through Docker when the runtime is available.
6. Inspect `.log` errors, warnings, and `.meas` values.
7. Inspect `.raw` traces, statistics, time-domain plots, or FFT plots.
8. Render the schematic to SVG and terminal preview.
9. Reject missing symbols, flag-only SVGs, and visibly bad layouts.
10. Report commands, evidence, failures, and residual risk.

## Required Commands

| Phase | Command |
| --- | --- |
| Environment | `./claw-spice doctor` |
| Tests | `./claw-spice test` |
| List examples | `./claw-spice examples list` |
| Generate examples | `./claw-spice examples run --skip-sim --skip-render` |
| Build one generator | `./claw-spice code build <example.py>` |
| Simulate | `./claw-spice sim run <circuit.cir>` |
| Log review | `./claw-spice log summary <circuit.log>` |
| Trace inventory | `./claw-spice raw traces <circuit.raw>` |
| Trace statistics | `./claw-spice raw stats <circuit.raw> V(out)` |
| Plot waveform | `./claw-spice raw plot <circuit.raw> V(out) --output <plot.svg>` |
| Plot spectrum | `./claw-spice raw fft <circuit.raw> V(out) --output <fft.svg>` |
| Terminal schematic | `./claw-spice show <schematic.asc> --terminal` |
| Visual schematic | `./claw-spice show <schematic.asc>` |
| Docs assets | `./claw-spice docs assets` |
| Docs build | `./claw-spice docs build` |

## Artifact Matrix

| Artifact | Producer | Review Check |
| --- | --- | --- |
| `.py` generator | human or AI edit | source is readable and deterministic |
| `.cir` netlist | `code build` | directives, includes, models, and node names are correct |
| `.asc` schematic | `code build` | explicit wires, visible symbols, labels attached to nodes |
| `.log` | `sim run` | no unhandled errors, warnings understood, `.meas` values present |
| `.raw` | `sim run` | expected traces exist and sample count is appropriate |
| waveform SVG | `raw plot` | trace labels and trends match expectations |
| FFT SVG | `raw fft` | spectral peaks make sense for the stimulus and circuit |
| schematic SVG | `render` / `show` / `docs assets` | real component shapes and wires are visible |
| terminal preview | `show --terminal` / `examples render` | quick no-GUI inspection is readable |

## Reporting Template

Use this structure in PRs, issue comments, and AI-generated summaries:

```text
Expected behavior:
Commands run:
Measurements:
Waveform/FFT evidence:
Rendered schematic evidence:
Failures or warnings:
Residual risks:
```

## Local Runtime Caveats

If local LTspice/Wine simulation times out but rendering/tests/docs pass, keep the
simulation caveat explicit and rely on GitHub's `LTspice Docker Smoke` workflow
after pushing. Do not hide the caveat or claim full simulation success without a
passing LTspice run.
