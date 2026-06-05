# Troubleshooting

Start with the smallest command that separates environment problems from circuit
problems.

```bash
./claw-spice doctor
./claw-spice test
./claw-spice examples run --skip-sim --skip-render
```

## Docker Build Fails

Check Compose first:

```bash
docker compose config
./claw-spice doctor
```

Likely causes:

- Docker daemon is not running.
- LTspice download URL changed or is blocked.
- Apple Silicon emulation is slow or unstable.

Try the prebuilt fallback for local diagnosis:

```bash
./claw-spice build-prebuilt
```

## Simulation Fails

Read the log before changing the circuit:

```bash
./claw-spice log summary path/to/circuit.log
```

Check:

- ground node `0` exists
- every node has a DC path
- model and subcircuit names resolve
- `.include` paths are valid inside Docker
- sources have finite rise/fall times where appropriate
- `.tran` max timestep is small enough for the waveform being measured

## `.raw` Is Missing

If the simulation returns non-zero or LTspice aborts early, the `.raw` file may
not be produced. Inspect the `.log` and `sim run --json` payload first.

```bash
./claw-spice sim run path/to/circuit.cir --json
```

## Plot Command Cannot Find A Trace

List traces exactly as LTspice wrote them:

```bash
./claw-spice raw traces path/to/circuit.raw
```

Then pass the exact trace name:

```bash
./claw-spice raw plot path/to/circuit.raw V(out) --output runs/latest/out.svg
```

## FFT Plot Looks Wrong

FFT plots need enough uniformly spaced transient samples and enough simulated
time for useful frequency resolution. Increase simulation duration, reduce max
timestep, and make sure `plotwinsize=0` is used when compression hides detail.

## Schematic Rendering Fails

Render without opening a viewer:

```bash
./claw-spice render path/to/circuit.asc --output runs/latest/circuit.svg
```

Likely causes:

- `ltspice_to_svg` is unavailable in the environment.
- a symbol is missing from bundled symbols or LTspice libraries.
- the `.asc` contains unsupported symbol names.
- the renderer produced a stale or flag-only SVG and the quality gate rejected it.

Fix the `.asc` source layout, bundled `.asy` symbol, or IR generator. Do not
replace a failed schematic with fake fallback art.

## SVG Exists But Looks Bad

Treat this as a source layout bug. Improve the generator:

- add explicit `WIRE` routing
- attach labels to wires or pins
- move directives below the circuit
- route supplies visibly into active devices
- space parallel branches and feedback paths apart
- rerender and inspect both SVG and terminal preview

## Docs Build Fails

Generate assets before building:

```bash
./claw-spice docs assets
./claw-spice docs build
```

Missing `ai-instructions.md`, missing plot SVGs, or missing generated schematic
SVGs usually mean `docs assets` did not complete.
