# AI Workflow

This repository is designed for AI-assisted circuit engineering, but not for
unchecked AI output. The `.opencode/` files define project-local agents and
skills that turn OpenCode into a disciplined LTspice collaborator.

## The Contract

AI agents in this repository are instructed to follow the same evidence loop a
human reviewer should follow:

```text
state expected behavior
→ generate or edit circuit source
→ run tests and generation
→ run LTspice when available
→ inspect .log warnings, errors, and .meas values
→ inspect .raw traces or FFT plots when relevant
→ render the .asc schematic
→ reject bad schematic output
→ report evidence and residual risk
```

The important constraint is that the AI should not merely write a plausible
netlist. It must produce artifacts that can be simulated, inspected, rendered,
documented, and reviewed.

## Agents

The project-local agents live in `.opencode/agent/`:

- `ltspice-sim-engineer`: owns the end-to-end design, simulation, analysis, and
  evidence loop.
- `circuit-design-reviewer`: reviews topology, signal assumptions, realism, and
  missing verification.
- `schematic-generator`: generates and improves `.asc` schematics, with special
  attention to visible routing and renderer output.
- `spice-model-librarian`: manages model provenance, licensing, pin order, and
  manifest updates.
- `simulation-debugger`: diagnoses LTspice failures, convergence problems, and
  suspicious results.
- `repo-maintainer`: maintains documentation, tests, workflows, and repository
  polish.

## Skills

The project-local skills live in `.opencode/skills/`:

- `claw-spice-workflow`: Docker-first project workflow and quality gates.
- `ltspice-circuit-design`: analog design and topology guidance.
- `ltspice-transient-simulation`: transient setup and measurement strategy.
- `ltspice-debugging-convergence`: convergence and runtime troubleshooting.
- `ltspice-measurements-analysis`: `.meas`, logs, and waveform interpretation.
- `ltspice-models-components`: model provenance and component policy.
- `code-to-schematic`: Python IR to `.cir` and `.asc` generation.
- `schematic-layout-rendering`: real renderer and visual quality standards.
- `github-actions-simulation`: CI, render, smoke, and Pages workflows.

## How We Instruct The AI

The instruction files emphasize several rules that are easy for automated agents
to miss:

- Use `./claw-spice`, not host dependency installs.
- Treat LTspice simulation, `.log` parsing, `.raw` inspection, and schematic
  rendering as separate evidence sources.
- Do not commit unknown-license SPICE models.
- Do not accept missing symbol definitions or flag-only schematic SVGs.
- Add explicit `.asc` `WIRE` routing for non-trivial circuits.
- Keep directives grouped away from components.
- Restart OpenCode after `.opencode` changes.

## Full Instruction Text

The complete source text of every agent and skill is published in the generated
reference page:

[Open the full AI instructions](ai-instructions.md)

Regenerate the reference page after changing `.opencode/` files:

```bash
./claw-spice docs assets
```

## Practical Prompting Pattern

Useful prompts should ask for engineering evidence, not only code:

```text
Create a Sallen-Key low-pass example. State the expected cutoff, generate the
.cir and .asc files, run the tests, run LTspice if available, inspect the .log
measurements, plot V(in)/V(out), render the schematic, and report evidence.
```

That prompt works because the project instructions already define the tools,
quality gates, and model policy. The user does not need to restate every rule in
every request.
