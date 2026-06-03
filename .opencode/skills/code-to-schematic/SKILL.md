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
3. Add layout hints for non-trivial circuits.
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
- Prefer net labels over complex auto-routing for early versions.
- Do not hand-write large `.asc` files when the IR can generate them.

## OpenCode Rule

Prefer generating `.asc` from code. Hand-edit `.asc` only for layout refinement
or unsupported symbols.
