# Simulation And Analysis

Simulation evidence comes from LTspice return codes, logs, measurements, raw
traces, waveform plots, and FFT plots. A passing command alone is not enough.

## Transient Setup

Most examples use transient analysis:

```spice
.tran 0 6m 0 1u
```

Use an explicit max timestep when measuring edges, filters, oscillation, FFT
content, or nonlinear clipping. Use realistic source rise/fall times rather than
ideal discontinuities unless the ideal step is the topic being tested.

## Sources

Common LTspice source forms in this repo:

```spice
PULSE(0 5 0 1u 1u 5m 10m)
SINE(0 1 1k)
```

For multi-tone examples, use simple source composition that remains easy to read
and simulate. Keep amplitudes small enough that the educational op-amp model does
not hide the intended behavior through rail saturation.

## Measurements

Prefer robust `.meas` values for CI and documentation:

```spice
.meas TRAN vout_max MAX V(out) FROM=2m TO=6m
.meas TRAN vout_min MIN V(out) FROM=2m TO=6m
.meas TRAN vout_avg AVG V(out) FROM=2m TO=6m
.meas TRAN vout_rms RMS V(out) FROM=2m TO=6m
.meas TRAN vout_2ms FIND V(out) AT=2m
```

Use threshold and edge measurements only after the waveform is stable enough to
make them reproducible across local and CI LTspice runs.

## Log Review

```bash
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice log summary examples/transient/rc-step/rc_step.log --json
```

Check errors first, then warnings, then `.meas` values. A waveform file can exist
even when the simulation produced warnings that invalidate the result.

## Raw Review

```bash
./claw-spice raw traces examples/transient/rc-step/rc_step.raw
./claw-spice raw stats examples/transient/rc-step/rc_step.raw V(out)
```

Use trace listing to avoid typos in names like `V(out)`, `V(filt)`, `V(rect)`,
or `V(clip)`.

## Time-Domain Plots

```bash
./claw-spice raw plot examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(in) V(out) --output runs/latest/sallen_key_lowpass.svg
```

Time-domain plots are best for steps, settling, clipping, rectification,
ringing, integration, differentiation, and visible filter response.

## FFT Plots

```bash
./claw-spice raw fft examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.raw V(clip) --output runs/latest/clip_fft.svg
```

The built-in FFT path is for quick engineering evidence:

- one trace at a time
- DC mean removed
- Hann window applied
- single-sided magnitude spectrum
- frequency axis in hertz
- transform length capped for CLI responsiveness

Use dedicated numerical tools for calibrated production spectral analysis. Use
the built-in FFT to show broad harmonic/filter behavior in examples and docs.

## Troubleshooting Suspicious Results

- If `.meas` values are missing, check `.log` for syntax or convergence errors.
- If the FFT looks flat or noisy, increase transient duration and reduce max timestep.
- If a nonlinear circuit looks linear, confirm the input amplitude reaches the diode or rail threshold.
- If an op-amp output clips unexpectedly, lower the input amplitude or adjust feedback gain.
- If a filter response looks wrong, check topology signs, capacitor orientation, and feedback node names.
