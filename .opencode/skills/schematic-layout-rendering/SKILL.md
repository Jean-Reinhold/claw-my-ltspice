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
- Are supply and ground connections clear?
- Are labels readable?
- Are directives visible but not mixed into component labels?
- Did rendering produce an SVG artifact?
- If terminal-only, is the terminal preview adequate for quick review?

## OpenCode Rule

After changing `.asc`, run `./claw-spice show <file.asc> --terminal`. If the
user asks to see it, run `./claw-spice show <file.asc>`.
