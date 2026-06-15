# Gallery

The gallery is the fastest way to inspect the generated visual artifacts. GitHub
Actions and `./claw-spice docs assets` regenerate these files from committed
examples using the Dockerized toolchain.

## Schematics

<div class="schematic-frame" markdown>
![Rendered RC step response schematic](assets/generated/rc-step.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp voltage follower schematic](assets/generated/opamp-voltage-follower.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp non-inverting schematic](assets/generated/opamp-noninverting.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp inverting schematic](assets/generated/opamp-inverting.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp summing schematic](assets/generated/opamp-summing.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp difference schematic](assets/generated/opamp-difference.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered op-amp active low-pass schematic](assets/generated/opamp-active-lowpass.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered precision rectifier schematic](assets/generated/precision-rectifier.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered Sallen-Key low-pass schematic](assets/generated/sallen-key-lowpass.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered diode clipper schematic](assets/generated/diode-clipper-spectrum.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered RLC step ringing schematic](assets/generated/rlc-step-ringing.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered passive RC spectrum split schematic](assets/generated/passive-rc-spectrum-split.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered practical op-amp integrator schematic](assets/generated/opamp-practical-integrator.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered practical op-amp differentiator schematic](assets/generated/opamp-practical-differentiator.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered simple Schmitt trigger schematic](assets/generated/schmitt-trigger-simple.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered temperature switch Schmitt trigger schematic](assets/generated/schmitt-trigger-temperature-switch.svg)
</div>

<div class="schematic-frame" markdown>
![Rendered Sallen-Key high-pass schematic](assets/generated/sallen-key-highpass.svg)
</div>

## Signal Plots

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

![Simple Schmitt trigger hysteresis plot](assets/plots/schmitt-trigger-simple.svg)

![Temperature switch Schmitt trigger plot](assets/plots/schmitt-trigger-temperature-switch.svg)

![Sallen-Key high-pass response plot](assets/plots/sallen-key-highpass.svg)

![Sallen-Key high-pass FFT plot](assets/plots/sallen-key-highpass-fft.svg)

## Regenerate Locally

```bash
./claw-spice examples render
./claw-spice docs assets
./claw-spice docs build
```

Generated SVGs are intentionally ignored in the working tree except for stable
plot assets. Recreate them when needed rather than manually editing rendered
output.
