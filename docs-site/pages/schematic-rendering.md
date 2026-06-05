# Schematic Rendering

Schematic rendering is a quality gate. The project renders `.asc` files through a
real LTspice schematic renderer and rejects misleading output.

## Renderer Chain

```text
.asc source
→ ltspice_to_svg / ltspice-to-svg
→ SVG schematic
→ optional PNG conversion
→ optional terminal preview
```

The renderer tries configured LTspice symbol paths and bundled repo-owned symbols
under `src/claw_spice/symbols`. It does not draw fake fallback schematics.

## Commands

```bash
./claw-spice render examples/transient/rc-step/rc_step.asc --output runs/latest/rc-step.svg
./claw-spice render examples/transient/rc-step/rc_step.asc --png
./claw-spice render examples/transient/rc-step/rc_step.asc --terminal-text runs/latest/rc-step.terminal.txt
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
./claw-spice examples render
./claw-spice docs assets
```

## Acceptance Checklist

- Component bodies are visible, not only text labels.
- Non-trivial circuits include explicit `WIRE` records.
- Inputs are left, outputs are right, and feedback paths are readable.
- Grounds attach to wires or pins and are not scattered in blank space.
- Supply sources are clear and routed into active-device pins when practical.
- Directives are grouped below the circuit body.
- Labels do not collide with component values or directive text.
- The SVG contains component groups and expected wire line count.

## Rejection Criteria

- `Symbol definition not found` or unresolved symbol warnings.
- SVGs that contain only flags, labels, or ground symbols.
- Overlapping directives and component labels.
- Floating input/output labels with no visible connection.
- Supply symbols that crowd the main signal path.
- Decorative substitute art that is not derived from the `.asc`.

## Fix Strategy

Fix the source, not the rendered output:

1. Add or correct `Circuit.wire(...)` routes.
2. Add `Circuit.flag(...)` and `Circuit.iopin(...)` only where they attach to real nodes.
3. Move components to reduce label and branch collisions.
4. Route supplies away from feedback networks.
5. Add bundled `.asy` symbols for repo-owned/basic components.
6. Rerender and inspect SVG, PNG, and terminal preview.

## Current Bundled Symbols

The package includes renderer symbols for the current examples:

- `res`
- `cap`
- `ind`
- `voltage`
- `current`
- `diode`
- `opamp2`

If a new example emits a new `SYMBOL` name, add a corresponding bundled symbol or
document the required LTspice library source.
