# Troubleshooting

## Docker Build Fails

Run:

```bash
./claw-spice doctor
docker compose config
```

If LTspice download fails, check the Analog Devices LTspice download URL and
network access.

## Simulation Fails

Read the log first:

```bash
./claw-spice log summary path/to/circuit.log
```

Check:

- Ground node `0` exists.
- Every node has a DC path.
- Model names resolve.
- `.include` and `.lib` paths are valid inside Docker.
- `.tran` duration and max timestep are appropriate.

## Schematic Does Not Open

Render without opening:

```bash
./claw-spice show path/to/circuit.asc --no-open
```

Render in terminal:

```bash
./claw-spice show path/to/circuit.asc --terminal
```

The container generates SVG files, and the host wrapper opens them using the
host's default SVG viewer.
