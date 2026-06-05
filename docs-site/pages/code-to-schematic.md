# Code To Schematic

`claw-spice` includes a small circuit IR that generates both LTspice netlists and
LTspice `.asc` schematics. The IR is intentionally simple: it is not a full EDA
database, but it is deterministic enough for examples, AI-assisted iteration,
tests, rendering, and GitHub Actions artifacts.

```python
from claw_spice.ir import Circuit

circuit = Circuit("RC step response")
circuit.voltage("V1", "in", "0", "PULSE(0 5 0 1n 1n 5m 10m)", at=(96, 112))
circuit.resistor("R1", "in", "out", "1k", at=(176, 112))
circuit.capacitor("C1", "out", "0", "1u", at=(352, 112))
circuit.wire(64, 112, 176, 112)
circuit.wire(272, 112, 416, 112)
circuit.wire(96, 208, 352, 208)
circuit.iopin(64, 112, "in", "In")
circuit.iopin(416, 112, "out", "Out")
circuit.flag(96, 208, "0")
circuit.flag(352, 208, "0")
circuit.tran("0", "6m", "0", "10u")
circuit.meas("TRAN", "vout_max", "MAX V(out)")
circuit.write_netlist("rc_step.cir")
circuit.write_asc("rc_step.asc")
```

## Netlist Model

The netlist side is direct SPICE text generation:

- Components are emitted in insertion order.
- `include(...)` statements are emitted before components.
- Analysis directives and `.meas` statements are emitted before `.end`.
- Subcircuits use normal `X...` syntax, so the generic op-amp examples can use
  `CLAW_IDEAL_OPAMP` without vendor models.

## Schematic Model

The schematic side emits LTspice `.asc` source records:

- `SYMBOL` records for resistors, capacitors, voltage sources, current sources,
  diodes, and the generic op-amp symbol.
- `WIRE` records for explicit orthogonal routing.
- `FLAG` records for ground and named nodes.
- `IOPIN` records for visible input and output ports.
- `TEXT` records for includes, analyses, model directives, and measurements.

The key principle is that non-trivial schematics must include explicit wires.
Labels alone can be electrically meaningful to LTspice but visually poor after
rendering. The project therefore treats disconnected-looking output as a source
layout bug.

## Layout Guidelines

- Place signal flow left to right: sources, input networks, active stage, output
  load, then output port.
- Use orthogonal wire segments with intentional spacing between branches.
- Put supply sources above and below the active device and route them into the
  visible supply pins when space allows.
- Put directives below the circuit body, not between components.
- Prefer explicit `iopin(...)` labels for public input/output nodes and `flag(...)`
  for ground and named internal anchors.
- Render the schematic and inspect the SVG before accepting layout changes.

## Rendering Quality Gate

Rendering must use `ltspice_to_svg` or the real `ltspice-to-svg` package
adapter. The renderer fails when symbols cannot be resolved or when an SVG has
no component groups despite `.asc` `SYMBOL` records. This prevents the docs from
publishing flag-only diagrams.

```bash
./claw-spice render examples/transient/sallen-key-lowpass/sallen_key_lowpass.asc --png
./claw-spice show examples/transient/sallen-key-lowpass/sallen_key_lowpass.asc --terminal
```

## Example Output

<div class="schematic-frame" markdown>
![Rendered Sallen-Key low-pass schematic](assets/generated/sallen-key-lowpass.svg)
</div>
