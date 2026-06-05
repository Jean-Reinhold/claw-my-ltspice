# CLI Reference

Run normal commands through the host wrapper from the repository root:

```bash
./claw-spice <command>
```

The wrapper starts Docker Compose, mounts the repository into `/workspace`, sets
the container user to the host UID/GID, and opens rendered SVGs on the host when
`show` is used without `--terminal` or `--no-open`.

## Wrapper Commands

| Command | Purpose | Notes |
| --- | --- | --- |
| `./claw-spice build` | Build the default Docker image | Downloads LTspice during the build; no LTspice binary is committed. |
| `./claw-spice build-prebuilt` | Build with `Dockerfile.prebuilt` | Local fallback for difficult Wine/Apple Silicon environments. |
| `./claw-spice shell` | Open a shell in the container | Use for diagnosis, not host dependency installs. |
| `./claw-spice show <file.asc>` | Render SVG and open on host | Wrapper-specific host viewer behavior. |
| `./claw-spice show <file.asc> --no-open` | Render without opening | Useful for scripts and CI-like local checks. |

## Global Options

| Option | Purpose |
| --- | --- |
| `--version` | Print the installed `claw-spice` version. |
| `--debug` | Raise full Python tracebacks instead of concise CLI errors. |

## Environment Checks

```bash
./claw-spice doctor
./claw-spice doctor --json
./claw-spice test
./claw-spice test --pattern 'test_plot.py'
```

`doctor` checks Python, workspace mapping, LTspice wrapper, Wine, Xvfb,
`ltspice_to_svg`, `chafa`, raster converters, and MkDocs. Run it before circuit
debugging so environment failures are separated from SPICE failures.

## Simulation Commands

```bash
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice sim run examples/transient/precision-rectifier/precision_rectifier.cir --timeout 600
./claw-spice sim run examples/transient/rc-step/rc_step.cir --json
./claw-spice sim netlist examples/transient/rc-step/rc_step.asc
./claw-spice sim netlist examples/transient/rc-step/rc_step.asc --timeout 120
```

`sim run` accepts `.cir`, `.net`, and `.asc`. For `.asc`, LTspice is asked to
export a netlist first. Outputs normally appear next to the simulated input:
`.log` for messages/measurements and `.raw` for waveforms.

## Logs And Measurements

```bash
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice log summary examples/transient/rc-step/rc_step.log --json
```

The summary extracts LTspice errors, warnings, and `.meas` values. Treat this as
the first verification step after every simulation.

## Raw Waveforms

```bash
./claw-spice raw traces examples/transient/rc-step/rc_step.raw
./claw-spice raw traces examples/transient/rc-step/rc_step.raw --json
./claw-spice raw stats examples/transient/rc-step/rc_step.raw V(out)
./claw-spice raw stats examples/transient/rc-step/rc_step.raw V(out) --json
./claw-spice raw plot examples/transient/rc-step/rc_step.raw V(in) V(out) --output runs/latest/rc_step.svg
./claw-spice raw plot examples/transient/opamp-summing/opamp_summing.raw V(in1) V(in2) V(out) --title "Summing amplifier" --png
./claw-spice raw fft examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(out) --output runs/latest/sallen_key_lowpass_fft.svg
./claw-spice raw fft examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.raw V(clip) --title "Clipped output FFT"
```

`raw plot` makes SVG time-domain or XY plots. Use `--x <trace>` to select a
non-time x-axis. `raw fft` transforms one trace into a single-sided magnitude
spectrum. Both support `--png` when a raster converter is available.

## Schematic Rendering

```bash
./claw-spice render examples/transient/rc-step/rc_step.asc --output runs/latest/rc-step.svg
./claw-spice render examples/transient/rc-step/rc_step.asc --png
./claw-spice render examples/transient/rc-step/rc_step.asc --terminal-text runs/latest/rc-step.terminal.txt
./claw-spice render examples/transient/rc-step/rc_step.asc --print-svg-path
./claw-spice show examples/transient/rc-step/rc_step.asc
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
./claw-spice show runs/latest/rc-step.svg --terminal
```

Rendering is strict. Missing symbols, stale output, or flag-only schematic SVGs
are failures. Fix the `.asc`, generator layout, or bundled `.asy` symbols instead
of replacing output with fake art.

## Code Generation

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice code build examples/transient/sallen-key-lowpass/sallen_key_lowpass.py --output-dir runs/latest/manual
./claw-spice code build examples/transient/sallen-key-lowpass/sallen_key_lowpass.py --json
```

A generator may define `build(output_dir)` or `create_circuit()`. `build` is
preferred when the example must copy support files such as `claw_opamps.lib`.

## Examples

```bash
./claw-spice examples list
./claw-spice examples list --json
./claw-spice examples run --skip-sim
./claw-spice examples run --skip-sim --skip-render
./claw-spice examples render
```

`examples render` regenerates `runs/latest/*.svg`, terminal previews, docs
schematic assets, and per-example `preview.svg` files when stable source
schematics are listed in `examples/sample-runs.toml`.

## Documentation

```bash
./claw-spice docs assets
./claw-spice docs assets --skip-schematics
./claw-spice docs build
./claw-spice docs serve
```

`docs assets` regenerates deterministic plot SVGs, FFT SVGs, schematic previews,
terminal previews, and `docs-site/pages/ai-instructions.md`. `docs build` runs
MkDocs against `docs-site/mkdocs.yml`.

## CI Parity

```bash
./claw-spice ci smoke
./claw-spice ci render
```

`ci smoke` runs tests and then renders examples when the schematic renderer is
available. `ci render` is the same render path used by documentation workflows.
