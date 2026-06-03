# Gallery

Generated gallery artifacts are produced by GitHub Actions and the Dockerized
toolchain.

## RC Step Response

The Pages workflow runs:

```bash
./claw-spice examples render
```

Artifacts are generated under `runs/latest/` during CI and uploaded as workflow
artifacts. Selected stable images can be promoted into this gallery as the
examples mature.

## Terminal Preview

`claw-spice` can render a schematic in the terminal:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
```

## Visual Preview

`claw-spice` can render SVG inside Docker and open it on the host:

```bash
./claw-spice show examples/transient/rc-step/rc_step.asc
```
