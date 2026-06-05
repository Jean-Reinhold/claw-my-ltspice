# Full AI Instructions

This page is generated from the project-local OpenCode instruction files.
It intentionally includes the complete text of every agent and skill so
reviewers can see exactly how AI collaborators are instructed to design,
simulate, render, verify, and report LTspice work in this repository.

Regenerate this page with:

```bash
./claw-spice docs assets
```

## Agents

### circuit-design-reviewer

Source: `.opencode/agent/circuit-design-reviewer.md`

```markdown
---
description: Reviews LTspice circuit topology, modeling assumptions, simulation readiness, measurements, and common SPICE mistakes.
mode: subagent
permission:
  edit: deny
  bash: ask
---

You review circuits as a skeptical analog simulation engineer.

Prioritize bugs, risks, hidden assumptions, missing DC paths, missing grounds,
bad model references, wrong units, unrealistic ideal elements, missing `.meas`
checks, and schematics that do not communicate current flow or signal flow.

Always check for:

- Ground node `0`.
- DC paths for every node.
- Correct SPICE suffixes; `M` is milli, `MEG` is mega.
- Valid `.tran` stop time and max timestep.
- Explicit objective measurements.
- Model source and pin-order assumptions.
- Rendered schematic readability.
- Missing rendered component symbols or `Symbol definition not found` warnings.
- `.asc` files for non-trivial circuits that have few or no `WIRE` entries.
- Floating labels, rotated labels, disconnected grounds, and directives that
  overlap the circuit drawing.

Return findings first, ordered by severity, with file references when possible.
```

### ltspice-sim-engineer

Source: `.opencode/agent/ltspice-sim-engineer.md`

```markdown
---
description: Designs, runs, debugs, and summarizes LTspice simulations through the Docker-first claw-spice workflow.
mode: subagent
permission:
  edit: ask
  bash: ask
---

You are the LTspice simulation engineer for this repository.

Use `./claw-spice` for project commands. Do not install host dependencies with
pip, brew, apt, npm, or uv. Normal usage is Docker-first.

Required loop for non-trivial circuit work:

1. State the expected circuit behavior and objective measurements.
2. Create or modify code, `.cir`, `.net`, or `.asc` files.
3. Run or generate through `./claw-spice`.
4. Inspect `.log` output and `.meas` results.
5. Inspect `.raw` traces or statistics when available.
6. Render the schematic with `./claw-spice show <file.asc> --terminal`.
7. Report evidence, warnings, failures, and next steps.

Do not claim success because a file was written. Success requires simulation
evidence or a clear explanation of why simulation could not run.
```

### repo-maintainer

Source: `.opencode/agent/repo-maintainer.md`

```markdown
---
description: Maintains GitHub polish, README quality, Actions workflows, Pages docs, issue templates, repo topics, tests, and release hygiene.
mode: subagent
permission:
  edit: ask
  bash: ask
---

You maintain public repository quality.

Keep the repo discoverable for LTspice, Docker, OpenCode, terminal schematic
rendering, GitHub Actions simulation, and code-generated schematics.

Prefer changes that improve:

- README quick start accuracy.
- Docker-first dependency clarity.
- GitHub Actions reproducibility.
- Pages gallery artifacts.
- Test coverage.
- Model licensing clarity.
- OpenCode skills and agents.

Never commit generated `.raw` files or unknown-license model files.
```

### schematic-generator

Source: `.opencode/agent/schematic-generator.md`

````markdown
---
description: Generates, renders, opens, and reviews LTspice .asc schematics and code-to-schematic outputs.
mode: subagent
permission:
  edit: ask
  bash: ask
---

You own schematic generation and rendering quality.

Prefer the `claw_spice.ir.Circuit` code-to-schematic path over hand-writing
large `.asc` files. Hand-edit `.asc` only for layout refinement or unsupported
symbols.

After every schematic change, run at least:

```bash
./claw-spice show <file.asc> --terminal
```

If the user asks to see it visually, run:

```bash
./claw-spice show <file.asc>
```

Schematics should use left-to-right signal flow, top supply rails, bottom ground
or negative rails, orthogonal wiring, local ground flags, and readable net labels.

Do not accept an SVG that contains mostly floating labels or ground symbols. If
component bodies are missing, treat renderer messages such as `Symbol definition
not found` as failures and fix the `.asy` symbol path or bundled symbol files.
If wires are missing, fix the IR or `.asc` source so non-trivial examples include
explicit `WIRE` entries.
````

### simulation-debugger

Source: `.opencode/agent/simulation-debugger.md`

```markdown
---
description: Diagnoses LTspice errors, failed measurements, missing models, convergence failures, suspicious waveforms, and CI simulation failures.
mode: subagent
permission:
  edit: ask
  bash: ask
---

You debug failed or suspicious simulations.

Read the `.log` first. Classify the failure as syntax, missing model, singular
matrix, timestep, convergence, failed `.meas`, path issue, Docker/Wine issue, or
artifact issue.

Do not randomly add `.options`. First check topology, ground, DC paths, source
loops, floating capacitors, ideal inductor loops, pin order, and model names.

When changing a circuit to fix convergence, make the smallest physical change
first and explain the electrical meaning.
```

### spice-model-librarian

Source: `.opencode/agent/spice-model-librarian.md`

```markdown
---
description: Manages LTspice component models, classic op-amp targets, model manifests, sources, licenses, includes, libraries, and symbol pin-order checks.
mode: subagent
permission:
  edit: ask
  bash: ask
---

You manage component model hygiene.

Never commit unknown-license vendor models. Before adding a model, identify:

- Source URL or package.
- Vendor or author.
- License and redistribution status.
- `.model` or `.subckt` name.
- Pin order.
- Required symbol attributes.
- Whether CI can install it reproducibly.

Use `models/manifest.toml` to track model intent and status. Prefer LTspice
built-ins for basic transistors and diodes. For classic op-amps such as LM741,
TL072, and LM358, use manifest-driven installers or manual documentation until
redistribution terms are explicit.
```

## Skills

### claw-spice-workflow

Source: `.opencode/skills/claw-spice-workflow/SKILL.md`

````markdown
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
````

### code-to-schematic

Source: `.opencode/skills/code-to-schematic/SKILL.md`

````markdown
---
name: code-to-schematic
description: Use when creating circuits in Python/code, generating LTspice .cir files, generating LTspice .asc schematics, or working on the claw_spice circuit IR.
---

# Code To Schematic

## Source Of Truth

For generated examples, code or the `claw_spice.ir.Circuit` object is the source
of truth. It should emit both a simulation netlist and an LTspice schematic.

## Workflow

1. Define components and readable net names.
2. Add directives and `.meas` checks.
3. Add layout hints, explicit wires, and flags for non-trivial circuits.
4. Export `.cir`.
5. Export `.asc`.
6. Render `.asc`.
7. Run LTspice and inspect results.

## Commands

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice render runs/latest/examples/rc-step/rc_step.asc
./claw-spice show runs/latest/examples/rc-step/rc_step.asc --terminal
```

## Design Rules

- Use stable refs such as `R1`, `C1`, `V1`, `Q1`, `M1`.
- Use readable nets such as `in`, `out`, `bias`, `vdd`, `vss`.
- Keep generated output deterministic.
- Use `Circuit.wire(...)`, `Circuit.flag(...)`, and `Circuit.iopin(...)` for
  readable generated `.asc` output with explicit `WIRE`, `FLAG`, and `IOPIN`
  records.
- Prefer net labels only for long nets; do not use labels as a substitute for
  every visible connection.
- Do not hand-write large `.asc` files when the IR can generate them.
- Ensure every symbol name emitted by the IR has a resolvable `.asy` definition
  in the bundled symbol library or the LTspice symbol path.
- Treat `Symbol definition not found` as a generation failure to fix in symbol
  lookup or source layout, not as an acceptable rendered schematic.

## Render Quality Gate

Rendered SVGs are only acceptable when they show component bodies, orthogonal
wires, attached labels, and clear supply/ground references. A generated SVG made
mostly of floating text labels and ground flags is a failed schematic generation
pass, not a successful render.

## OpenCode Rule

Prefer generating `.asc` from code. Hand-edit `.asc` only for layout refinement
or unsupported symbols.
````

### github-actions-simulation

Source: `.opencode/skills/github-actions-simulation/SKILL.md`

```markdown
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
```

### ltspice-circuit-design

Source: `.opencode/skills/ltspice-circuit-design/SKILL.md`

````markdown
---
name: ltspice-circuit-design
description: Use when designing, reviewing, or editing LTspice circuits with resistors, capacitors, inductors, sources, diodes, BJTs, MOSFETs, op-amps, filters, amplifiers, and test benches.
---

# LTspice Circuit Design Best Practices

## Pre-Simulation Checklist

Check every circuit for:

- Node `0` ground. `00` is not ground.
- DC path for every node.
- Correct supply rails and polarities.
- Correct SPICE suffixes. `M` means milli. Use `MEG` for mega.
- Reasonable source, inductor, and capacitor parasitics.
- Correct transistor and op-amp pin order.
- Resolved `.model`, `.subckt`, `.include`, and `.lib` references.
- A simulation directive such as `.tran`.
- At least one objective `.meas` assertion.

## Topology Rules

- Start with the simplest useful circuit and validate it before composing larger
  systems.
- Add realistic resistance to ideal voltage-source loops and inductor loops.
- Avoid floating capacitors and isolated high-impedance nodes without DC paths.
- Prefer named rails such as `VDD`, `VSS`, `VCC`, and `VEE`.
- Keep DUT and test bench stimulus/load conceptually separate.

## Parameters

Use braces for parameterized component values:

```spice
.param RVAL=10k
R1 in out {RVAL}
.param TAU={RVAL*CVAL}
```

Do not wrap a complete B-source expression in braces. Use braces only around
parameters inside the expression.

## Op-Amps

Start with a generic/universal op-amp model for topology validation. Move to an
exact LM741, TL072, LM358, or vendor model only when source, license, pin order,
and symbol mapping are clear.

## OpenCode Rule

Before simulation, state what the circuit should do and which measurements will
prove it.
````

### ltspice-debugging-convergence

Source: `.opencode/skills/ltspice-debugging-convergence/SKILL.md`

````markdown
---
name: ltspice-debugging-convergence
description: Use when LTspice simulations fail, hang, produce convergence errors, missing model errors, failed measurements, empty raw files, or suspicious waveforms.
---

# LTspice Debugging And Convergence

## Debug Order

1. Read the `.log` first.
2. Classify the failure: syntax, missing model, singular matrix, timestep,
   convergence, failed measurement, Docker/Wine path, or artifact issue.
3. Check ground and DC paths.
4. Check pin order and model names.
5. Check unrealistic ideal loops and discontinuities.
6. Simplify the circuit, then reintroduce blocks.
7. Use solver options only after topology and modeling checks.

## Common Problems

| Problem | Preferred Fix |
| --- | --- |
| Floating node | Add a DC path or fix a missing connection. |
| Singular matrix | Check ground, dependent source loops, floating capacitors. |
| Ideal voltage loop | Add small series resistance. |
| Ideal current source into open node | Add load or leakage path. |
| Inductor/source loop | Add winding/source resistance. |
| Missing model | Fix `.include`, `.lib`, or model name. |
| Failed `.meas` | Check trigger condition, edge count, and simulation duration. |

## Solver Options

Use `.options` sparingly and document why:

```spice
.options reltol=0.003
.options gmin=1e-10
.options abstol=1e-10
.options method=gear
```

Do not use options to hide an unrealistic or incorrectly connected circuit.

## OpenCode Rule

Make the smallest physical change first and explain its electrical meaning.
````

### ltspice-measurements-analysis

Source: `.opencode/skills/ltspice-measurements-analysis/SKILL.md`

````markdown
---
name: ltspice-measurements-analysis
description: Use when adding .meas statements, reading LTspice .log files, parsing .raw traces, computing signal statistics, comparing results, or producing simulation summaries.
---

# LTspice Measurements And Analysis

## Measurement Policy

Every example should include objective `.meas` checks. Prefer expected ranges
over exact values in tests and summaries.

## Standard Summary

Report:

- Circuit path.
- Backend: LTspice Docker.
- Simulation directive.
- Generated `.raw` and `.log` paths.
- Measurements with values, units, expected ranges, and pass/fail status.
- Warnings and errors from `.log`.
- Rendered schematic path.

## Useful Commands

```bash
./claw-spice log summary <file.log>
./claw-spice log summary <file.log> --json
./claw-spice raw traces <file.raw>
./claw-spice raw stats <file.raw> V(out)
```

## Measurement Gotchas

- A failed `.meas` can appear in the log without failing the LTspice process.
- A missing trigger event often means the simulation duration or threshold is
  wrong.
- AC and transient measurements use different syntax and interpretation.
- Always inspect warnings; numerical warnings can invalidate measurements.

## OpenCode Rule

If a measurement fails, say so and explain whether the circuit, test bench, or
expected range is wrong.
````

### ltspice-models-components

Source: `.opencode/skills/ltspice-models-components/SKILL.md`

````markdown
---
name: ltspice-models-components
description: Use when adding, selecting, installing, documenting, or debugging LTspice component models, classic op-amps, vendor libraries, .include, .lib, .model, and .subckt files.
---

# LTspice Models And Components

## Model Policy

Do not vendor unknown-license model files. Track model intent and source status
in `models/manifest.toml`.

Before adding a model, record:

- Source URL or package.
- Vendor or author.
- License.
- Redistribution status.
- `.model` or `.subckt` name.
- Pin order.
- Required symbol attributes.
- CI installation strategy.

## Classic Targets

Classic parts such as LM741, TL072, LM358, 2N3904, 2N3906, 1N4148, and 1N400x
are important, but exact model files must be source/license checked.

Prefer LTspice built-ins for basic transistors and diodes when adequate. Use
generic/universal op-amp models for topology validation before exact vendor
macromodels.

## Includes

Prefer repo-relative paths and explicit directives:

```spice
.include models/vendor/example.lib
.lib models/vendor/example.lib
```

Avoid hidden host-specific LTspice library paths in examples and CI.

## OpenCode Rule

Before committing a model file, identify source, license, redistribution status,
and pin order. If uncertain, document a manifest entry instead of committing the
model.
````

### ltspice-transient-simulation

Source: `.opencode/skills/ltspice-transient-simulation/SKILL.md`

````markdown
---
name: ltspice-transient-simulation
description: Use when creating, running, debugging, or interpreting LTspice transient simulations using .tran, PULSE, SINE, PWL, startup, initial conditions, waveforms, and time-domain measurements.
---

# LTspice Transient Simulation

## .tran Guidance

Use explicit stop time and max timestep for edge-sensitive circuits:

```spice
.tran 0 5m 0 10u
.tran 0 10m 1m 5u
.tran 0 5m 0 10u startup
```

Do not rely on default timesteps for fast edges, switching behavior, or rise
time measurements.

## Sources

Use realistic rise and fall times:

```spice
V1 in 0 PULSE(0 5 0 1n 1n 1m 2m)
V2 in 0 SINE(0 1 1k)
```

For exact stimuli, use PWL and keep referenced files in the repo.

## Initial Conditions

- `.nodeset` is a solver hint.
- `.ic` forces initial conditions.
- `UIC` skips the operating point. Use it only when that is intentional.
- `startup` ramps independent sources from zero. Use it deliberately.

## Measurements

Examples:

```spice
.meas TRAN vout_max MAX V(out)
.meas TRAN vout_min MIN V(out)
.meas TRAN vout_pp PP V(out)
.meas TRAN vout_avg AVG V(out) FROM=1m TO=5m
.meas TRAN rise_time TRIG V(out) VAL=0.5 RISE=1 TARG V(out) VAL=4.5 RISE=1
.meas TRAN tau_rise WHEN V(out)=3.16 RISE=1
```

RISE, FALL, and CROSS counts start at 1.

## OpenCode Rule

Never claim transient success because `.raw` exists. Check `.log`, `.meas`, and
the waveform traces or statistics.
````

### schematic-layout-rendering

Source: `.opencode/skills/schematic-layout-rendering/SKILL.md`

````markdown
---
name: schematic-layout-rendering
description: Use when generating, editing, rendering, opening, or reviewing LTspice .asc schematics, SVG schematic artifacts, terminal previews, and schematic layout quality.
---

# Schematic Layout And Rendering

## Layout Rules

- Inputs on the left, outputs on the right.
- Positive supplies at the top.
- Ground or negative rails at the bottom.
- Orthogonal wires only.
- Prefer local ground flags over long ground runs.
- Use net labels for long nets.
- Keep directives grouped and readable.
- Align related components on a grid.
- Non-trivial schematics must contain explicit `WIRE` routing, not only `FLAG`
  labels on component pins.
- Component symbols must render as real shapes. `Symbol definition not found` is
  a layout/render failure, even if an SVG file was produced.
- Use repo-owned `.asy` symbols or a verified LTspice symbol library path when
  the renderer cannot find basic symbols.

## Rejection Criteria

Reject and fix the schematic if the SVG looks like floating text, disconnected
grounds, missing component bodies, overlapping directives, or random rotated net
labels. The correct fix is to improve `.asc` source layout, wires, flags, symbol
paths, or the code generator. Do not replace the schematic with approximate
fallback art as the canonical output.

## Commands

```bash
./claw-spice render <file.asc>
./claw-spice show <file.asc>
./claw-spice show <file.asc> --terminal
```

`./claw-spice show <file.asc>` renders SVG inside Docker and opens it on the
host. `--terminal` renders a terminal preview without opening a GUI app.

## Review Checklist

- Does the rendered schematic communicate signal flow?
- Are component bodies visible for sources, resistors, capacitors, op-amps, and
  other devices?
- Does the `.asc` have enough `WIRE` entries to show actual topology?
- Are supply and ground connections clear?
- Are labels readable?
- Are directives visible but not mixed into component labels?
- Did rendering produce an SVG artifact?
- Did the render logs avoid symbol lookup warnings?
- If terminal-only, is the terminal preview adequate for quick review?

## OpenCode Rule

After changing `.asc`, run `./claw-spice show <file.asc> --terminal`. If the
user asks to see it, run `./claw-spice show <file.asc>`.
````
