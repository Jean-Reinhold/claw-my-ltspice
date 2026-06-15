# Plots And FFT

`claw-spice` can create SVG plots directly from LTspice `.raw` files. The goal
is to make waveform inspection part of the repeatable engineering loop instead
of a manual screenshot step.

## Time-Domain Plots

List the available traces first:

```bash
./claw-spice raw traces runs/latest/rc_step.raw
```

Plot one or more traces:

```bash
./claw-spice raw plot runs/latest/rc_step.raw V(in) V(out) --output runs/latest/rc_step.svg
./claw-spice raw plot runs/latest/opamp_summing.raw V(in1) V(in2) V(out) --output runs/latest/opamp_summing.svg
```

Useful options:

- `--x <trace>` selects a non-default x-axis trace.
- `--title <text>` sets a custom plot title.
- `--png` also converts the SVG to PNG when `rsvg-convert` or `resvg` is available.

## FFT Spectrum Plots

Use `raw fft` when a transient run contains a periodic or mixed-frequency signal:

```bash
./claw-spice raw fft runs/latest/sallen_key_lowpass.raw V(out) --output runs/latest/sallen_key_lowpass_fft.svg
```

The FFT implementation is dependency-free and intentionally conservative:

- It transforms one selected signal trace at a time.
- It uses the time axis as the sample spacing source.
- It removes the DC mean before the transform.
- It applies a Hann window to reduce spectral leakage.
- It emits a single-sided magnitude spectrum in hertz.
- It caps the transform length to keep CLI use responsive without requiring NumPy.

For production-grade spectral analysis, keep using the exported `.raw` data with
specialized tools when you need window selection, calibrated units, or very large
sample counts. The built-in FFT plot is for quick engineering evidence and docs
artifacts.

## Expected Example Plots

These documentation plots show expected signal shapes. Real simulation plots
should be regenerated from each run's `.raw` output.

![RC step output plot](assets/plots/rc-step-vout.svg)

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

![Buffered active low-pass plot](assets/plots/opamp-active-lowpass.svg)

![Precision rectifier response plot](assets/plots/precision-rectifier.svg)

![Sallen-Key low-pass response plot](assets/plots/sallen-key-lowpass.svg)

![Sallen-Key low-pass FFT plot](assets/plots/sallen-key-lowpass-fft.svg)

![Diode clipper response plot](assets/plots/diode-clipper-spectrum.svg)

![Diode clipper FFT plot](assets/plots/diode-clipper-spectrum-fft.svg)

![RLC step ringing response plot](assets/plots/rlc-step-ringing.svg)

![Passive RC spectrum split plot](assets/plots/passive-rc-spectrum-split.svg)

![Passive RC low-pass FFT plot](assets/plots/passive-rc-spectrum-low-fft.svg)

![Passive RC high-pass FFT plot](assets/plots/passive-rc-spectrum-high-fft.svg)

![Practical op-amp integrator plot](assets/plots/opamp-practical-integrator.svg)

![Practical op-amp differentiator plot](assets/plots/opamp-practical-differentiator.svg)

![Op-amp MLP forward-pass plot](assets/plots/opamp-mlp-forward-pass.svg)

![Simple Schmitt trigger hysteresis plot](assets/plots/schmitt-trigger-simple.svg)

![Temperature switch Schmitt trigger plot](assets/plots/schmitt-trigger-temperature-switch.svg)

![Sallen-Key high-pass response plot](assets/plots/sallen-key-highpass.svg)

![Sallen-Key high-pass FFT plot](assets/plots/sallen-key-highpass-fft.svg)
