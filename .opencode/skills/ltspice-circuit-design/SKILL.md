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
