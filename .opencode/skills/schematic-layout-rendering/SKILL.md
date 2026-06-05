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
