# Sallen-Key Walkthrough

The Sallen-Key examples demonstrate active second-order filters and FFT-based
evidence from transient waveforms.

## Low-Pass Filter

<div class="schematic-frame" markdown>
![Rendered Sallen-Key low-pass schematic](assets/generated/sallen-key-lowpass.svg)
</div>

With equal `10 kOhm` resistors and equal `10 nF` capacitors, the characteristic
frequency scale is approximately:

```text
fc ~= 1 / (2 * pi * R * C) ~= 1.6 kHz
```

The low-pass output preserves lower-frequency content and attenuates higher
frequency components.

```bash
./claw-spice code build examples/transient/sallen-key-lowpass/sallen_key_lowpass.py
./claw-spice sim run examples/transient/sallen-key-lowpass/sallen_key_lowpass.cir
./claw-spice raw plot examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(in) V(filt) V(out) --output runs/latest/sallen_key_lowpass.svg
./claw-spice raw fft examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(out) --output runs/latest/sallen_key_lowpass_fft.svg
```

Measurements: `vout_peak`, `vout_min`, `filt_peak`.

![Sallen-Key low-pass response plot](assets/plots/sallen-key-lowpass.svg)

![Sallen-Key low-pass FFT plot](assets/plots/sallen-key-lowpass-fft.svg)

## High-Pass Filter

<div class="schematic-frame" markdown>
![Rendered Sallen-Key high-pass schematic](assets/generated/sallen-key-highpass.svg)
</div>

The high-pass companion uses the same component scale but moves the capacitors
into the input path. It rejects low-frequency/DC content and emphasizes faster
transitions.

Measurements: `vout_max`, `vout_min`, `vout_avg`.

![Sallen-Key high-pass response plot](assets/plots/sallen-key-highpass.svg)

![Sallen-Key high-pass FFT plot](assets/plots/sallen-key-highpass-fft.svg)

## Layout Notes

The Sallen-Key layouts intentionally route supplies away from the filter body so
component labels and feedback paths remain readable. If the supply symbols collide
with the feedback path, move the supplies before accepting the render.
