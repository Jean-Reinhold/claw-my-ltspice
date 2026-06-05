# claw-spice

`claw-spice` is a Docker-first LTspice automation project for building,
simulating, rendering, documenting, and reviewing code-generated schematics and
analog circuits with OpenCode.
It is designed for a practical engineering loop: code creates circuits, LTspice
simulates them, logs and raw waveforms are inspected, schematics are rendered by
a real LTspice schematic renderer, and GitHub Actions publishes the results.

![claw-spice workflow](assets/images/workflow.svg)

## What This Project Does

<div class="claw-grid" markdown>

<div class="claw-card" markdown>
### Reproducible LTspice

The host wrapper runs a Docker container with Wine, Xvfb, Python tooling,
schematic rendering, terminal previews, and MkDocs. The host should only need
Docker, Docker Compose, Git, and OpenCode.
</div>

<div class="claw-card" markdown>
### Code-Generated Circuits

Examples are written as Python circuit generators. Each generator emits a `.cir`
netlist and a routed `.asc` schematic with explicit wires, flags, and I/O pins.
</div>

<div class="claw-card" markdown>
### Real Schematic Rendering

Rendered previews use `ltspice_to_svg` / `ltspice-to-svg`. Fake fallback artwork
is intentionally rejected because schematic quality matters for review.
</div>

<div class="claw-card" markdown>
### AI-Guided Engineering

Project-local OpenCode agents and skills instruct AI collaborators to simulate,
inspect logs, inspect `.raw` traces, render schematics, and report evidence.
</div>

</div>

## Engineering Loop

The loop is intentionally explicit because it gives both people and AI agents a
shared definition of done.

```text
write generator / edit schematic
→ generate .cir and .asc
→ run LTspice in Docker
→ inspect .log errors, warnings, and .meas values
→ inspect .raw traces and FFT plots when relevant
→ render .asc to SVG and terminal preview
→ publish artifacts through GitHub Actions and Pages
```

## Start Here

```bash
./claw-spice doctor
./claw-spice examples list
./claw-spice examples run --skip-sim
./claw-spice show examples/transient/rc-step/rc_step.asc
```

<div class="schematic-frame" markdown>
![Rendered RC step response schematic](assets/generated/rc-step.svg)
</div>

## Included Example Families

- Passive RC step response with `.meas` time-constant checks.
- Op-amp follower, non-inverting, inverting, summing, and difference amplifiers.
- Buffered active low-pass response.
- Precision half-wave rectifier with an inline repo-owned diode model.
- Unity-gain Sallen-Key low-pass filter with time-domain and FFT documentation.
- Diode clipper, passive RC spectrum split, and RLC step ringing examples.
- Practical op-amp integrator, differentiator, and Sallen-Key high-pass examples.

## What To Read Next

- [Quick Start](quick-start.md) for the first end-to-end workflow.
- [Engineering Workflow](engineering-workflow.md) for the evidence loop and definition of done.
- [Command Reference](command-reference.md) for every major CLI path.
- [Schematic Rendering](schematic-rendering.md) for visual quality gates and renderer behavior.
- [Simulation And Analysis](simulation-analysis.md) for `.log`, `.raw`, plotting, and FFT work.
- [Circuit Examples](examples.md) for schematics, expected behavior, and commands.
- [Theory To Examples](theory-to-examples.md) for the mapping from the external
  EB2 theoretical material into original LTspice examples.
- [Plots And FFT](signal-plots.md) for `.raw` plotting and spectrum generation.
- [AI Workflow](opencode.md) for how OpenCode is instructed to work in this repo.
- [Full AI Instructions](ai-instructions.md) for the full text of every agent and skill.
