# Contributing

## Principles

- Use LTspice as the simulation backend for this project.
- Keep normal usage Docker-first. Do not require host Python, Wine, LTspice,
  chafa, or schematic-rendering packages.
- Add objective `.meas` checks to examples.
- Render schematics after generating or changing `.asc` files.
- Do not commit unknown-license SPICE models.

## Local Workflow

```bash
./claw-spice build
./claw-spice doctor
./claw-spice examples run
./claw-spice show examples/transient/rc-step/rc_step.asc
```

## Adding Examples

Every example should include:

- A short README.
- A `.cir`, `.asc`, or code generator.
- At least one transient `.meas` statement.
- Expected measurement ranges in tests or documentation.
- A schematic render path using `./claw-spice show`.
