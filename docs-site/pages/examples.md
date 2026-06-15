# Circuit Examples

The examples are executable specifications. Each one has a Python generator, a
committed `.cir` netlist, a committed `.asc` schematic, expected `.meas` values,
a rendered schematic preview, and an expected signal-shape plot.

The Schmitt trigger examples are included as a pair: one small configurable
threshold circuit for learning the hysteresis math, and one practical noisy
temperature-switch circuit for a real load-control use case.

List the configured samples:

```bash
./claw-spice examples list
./claw-spice examples list --json
```

Run the full generation path without LTspice simulation:

```bash
./claw-spice examples run --skip-sim
```

## RC Step Response

<div class="schematic-frame" markdown>
![Rendered RC step response schematic](assets/generated/rc-step.svg)
</div>

The RC step response is the smallest verification circuit. A `1 kOhm` resistor
and `1 uF` capacitor produce a nominal `1 ms` time constant, so the `tau_rise`
measurement should occur near the point where `V(out)` reaches `63.2%` of the
`5 V` final value.

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice raw plot examples/transient/rc-step/rc_step.raw V(in) V(out) --output runs/latest/rc_step.svg
```

Measurements: `vout_max`, `vout_ss`, `tau_rise`.

![RC step output plot](assets/plots/rc-step-vout.svg)

## Op-Amp Voltage Follower

<div class="schematic-frame" markdown>
![Rendered op-amp voltage follower schematic](assets/generated/opamp-voltage-follower.svg)
</div>

The voltage follower checks the generic op-amp model, supply routing, and unity
feedback. It is a useful first active-circuit smoke test because `V(out)` should
track `V(in)` after the output settles.

```bash
./claw-spice code build examples/transient/opamp-voltage-follower/opamp_voltage_follower.py
./claw-spice sim run examples/transient/opamp-voltage-follower/opamp_voltage_follower.cir
./claw-spice raw plot examples/transient/opamp-voltage-follower/opamp_voltage_follower.raw V(in) V(out) --output runs/latest/opamp_voltage_follower.svg
```

Measurements: `vout_2ms`, `tracking_error_max`.

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

## Op-Amp Non-Inverting Gain

<div class="schematic-frame" markdown>
![Rendered op-amp non-inverting schematic](assets/generated/opamp-noninverting.svg)
</div>

The non-inverting amplifier uses `Rf = 20 kOhm` and `Rg = 10 kOhm`, giving an
ideal closed-loop gain of `1 + Rf/Rg = 3`. The example verifies the gain at
`2 ms` after the step settles.

```bash
./claw-spice code build examples/transient/opamp-noninverting/opamp_noninverting.py
./claw-spice sim run examples/transient/opamp-noninverting/opamp_noninverting.cir
./claw-spice raw plot examples/transient/opamp-noninverting/opamp_noninverting.raw V(in) V(out) --output runs/latest/opamp_noninverting.svg
```

Measurements: `vout_2ms`, `gain_2ms`.

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

## Op-Amp Inverting Gain

<div class="schematic-frame" markdown>
![Rendered op-amp inverting schematic](assets/generated/opamp-inverting.svg)
</div>

The inverting amplifier uses `Rf = 20 kOhm` and `Rin = 10 kOhm`, giving an ideal
closed-loop gain of `-Rf/Rin = -2`. This example exercises virtual-ground
feedback routing and negative output behavior.

```bash
./claw-spice code build examples/transient/opamp-inverting/opamp_inverting.py
./claw-spice sim run examples/transient/opamp-inverting/opamp_inverting.cir
./claw-spice raw plot examples/transient/opamp-inverting/opamp_inverting.raw V(in) V(out) --output runs/latest/opamp_inverting.svg
```

Measurements: `vout_2ms`, `gain_2ms`.

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

## Op-Amp Inverting Summing Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp summing schematic](assets/generated/opamp-summing.svg)
</div>

The summing amplifier uses two input paths with different resistor values. The
expected relationship is approximately `V(out) = -(2 * V(in1) + V(in2))`. The
delayed second input makes it easy to see each contribution in the waveform.

```bash
./claw-spice code build examples/transient/opamp-summing/opamp_summing.py
./claw-spice sim run examples/transient/opamp-summing/opamp_summing.cir
./claw-spice raw plot examples/transient/opamp-summing/opamp_summing.raw V(in1) V(in2) V(out) --output runs/latest/opamp_summing.svg
```

Measurements: `vout_2ms`, `vout_3ms`.

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

## Op-Amp Difference Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp difference schematic](assets/generated/opamp-difference.svg)
</div>

The difference amplifier uses matched resistor ratios for an expected
relationship of approximately `V(out) = 2 * (V(plus) - V(minus))`. It is useful
for checking differential signal naming, multi-input routing, and matched-gain
documentation.

```bash
./claw-spice code build examples/transient/opamp-difference/opamp_difference.py
./claw-spice sim run examples/transient/opamp-difference/opamp_difference.cir
./claw-spice raw plot examples/transient/opamp-difference/opamp_difference.raw V(plus) V(minus) V(out) --output runs/latest/opamp_difference.svg
```

Measurements: `vout_2ms`, `vout_3ms`.

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

## Buffered Active Low-Pass

<div class="schematic-frame" markdown>
![Rendered active low-pass schematic](assets/generated/opamp-active-lowpass.svg)
</div>

The buffered active low-pass filters a pulsed input through an RC network and
buffers the filtered node. The schematic intentionally routes the op-amp supply
wires into the visible supply pins to avoid floating-looking power labels.

```bash
./claw-spice code build examples/transient/opamp-active-lowpass/opamp_active_lowpass.py
./claw-spice sim run examples/transient/opamp-active-lowpass/opamp_active_lowpass.cir
./claw-spice raw plot examples/transient/opamp-active-lowpass/opamp_active_lowpass.raw V(in) V(filt) V(out) --output runs/latest/opamp_active_lowpass.svg
```

Measurements: `vout_avg`, `vout_max`.

![Buffered active low-pass plot](assets/plots/opamp-active-lowpass.svg)

## Precision Half-Wave Rectifier

<div class="schematic-frame" markdown>
![Rendered precision rectifier schematic](assets/generated/precision-rectifier.svg)
</div>

The precision rectifier demonstrates how to document a simple nonlinear circuit
without committing vendor models. The op-amp drives a diode and receives
feedback from the rectified output node. During positive half-cycles the op-amp
compensates the diode drop; during negative half-cycles the diode disconnects
the output and the load returns the node to ground.

```bash
./claw-spice code build examples/transient/precision-rectifier/precision_rectifier.py
./claw-spice sim run examples/transient/precision-rectifier/precision_rectifier.cir
./claw-spice raw plot examples/transient/precision-rectifier/precision_rectifier.raw V(in) V(rect) --output runs/latest/precision_rectifier.svg
```

Measurements: `vrect_max`, `vrect_min`, `vrect_avg`.

![Precision rectifier response plot](assets/plots/precision-rectifier.svg)

## Sallen-Key Low-Pass Filter

<div class="schematic-frame" markdown>
![Rendered Sallen-Key low-pass schematic](assets/generated/sallen-key-lowpass.svg)
</div>

The unity-gain Sallen-Key filter uses equal `10 kOhm` resistors and equal `10 nF`
capacitors, placing the idealized pole frequency near `1.6 kHz`. The transient
example uses a `1 kHz` sine input, while the documentation FFT preview uses a
synthetic mixed-frequency waveform to show high-frequency attenuation.

```bash
./claw-spice code build examples/transient/sallen-key-lowpass/sallen_key_lowpass.py
./claw-spice sim run examples/transient/sallen-key-lowpass/sallen_key_lowpass.cir
./claw-spice raw plot examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(in) V(filt) V(out) --output runs/latest/sallen_key_lowpass.svg
./claw-spice raw fft examples/transient/sallen-key-lowpass/sallen_key_lowpass.raw V(out) --output runs/latest/sallen_key_lowpass_fft.svg
```

Measurements: `vout_peak`, `vout_min`, `filt_peak`.

![Sallen-Key low-pass response plot](assets/plots/sallen-key-lowpass.svg)

![Sallen-Key low-pass FFT plot](assets/plots/sallen-key-lowpass-fft.svg)

## Diode Clipper Spectrum

<div class="schematic-frame" markdown>
![Rendered diode clipper schematic](assets/generated/diode-clipper-spectrum.svg)
</div>

The diode clipper is a compact nonlinear waveshaping example. A sine source
drives a resistor into a diode/load node. Positive peaks are compressed by diode
conduction, which creates harmonic content that is visible in the FFT plot.

```bash
./claw-spice code build examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.py
./claw-spice sim run examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.cir
./claw-spice raw plot examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.raw V(in) V(clip) --output runs/latest/diode_clipper_spectrum.svg
./claw-spice raw fft examples/transient/diode-clipper-spectrum/diode_clipper_spectrum.raw V(clip) --output runs/latest/diode_clipper_spectrum_fft.svg
```

Measurements: `clip_max`, `clip_min`, `clip_avg`.

![Diode clipper response plot](assets/plots/diode-clipper-spectrum.svg)

![Diode clipper FFT plot](assets/plots/diode-clipper-spectrum-fft.svg)

## Passive RLC Step Ringing

<div class="schematic-frame" markdown>
![Rendered RLC step ringing schematic](assets/generated/rlc-step-ringing.svg)
</div>

The RLC example introduces a second-order transient response. A step drives a
series resistor and inductor into a capacitive output node. The output overshoots
and rings before settling, which makes damping and natural frequency visible.

```bash
./claw-spice code build examples/transient/rlc-step-ringing/rlc_step_ringing.py
./claw-spice sim run examples/transient/rlc-step-ringing/rlc_step_ringing.cir
./claw-spice raw plot examples/transient/rlc-step-ringing/rlc_step_ringing.raw V(in) V(out) --output runs/latest/rlc_step_ringing.svg
```

Measurements: `ring_peak`, `ring_min`, `vout_3ms`.

![RLC step ringing response plot](assets/plots/rlc-step-ringing.svg)

## Passive RC Spectrum Split

<div class="schematic-frame" markdown>
![Rendered passive RC spectrum split schematic](assets/generated/passive-rc-spectrum-split.svg)
</div>

The RC spectrum split example sends a mixed low/high-frequency input into
passive low-pass and high-pass branches. It is useful for teaching cutoff,
frequency-selective attenuation, and FFT-based evidence without any active model.

```bash
./claw-spice code build examples/transient/passive-rc-spectrum-split/passive_rc_spectrum_split.py
./claw-spice sim run examples/transient/passive-rc-spectrum-split/passive_rc_spectrum_split.cir
./claw-spice raw plot examples/transient/passive-rc-spectrum-split/passive_rc_spectrum_split.raw V(in) V(low) V(high) --output runs/latest/passive_rc_spectrum_split.svg
./claw-spice raw fft examples/transient/passive-rc-spectrum-split/passive_rc_spectrum_split.raw V(low) --output runs/latest/passive_rc_spectrum_low_fft.svg
./claw-spice raw fft examples/transient/passive-rc-spectrum-split/passive_rc_spectrum_split.raw V(high) --output runs/latest/passive_rc_spectrum_high_fft.svg
```

Measurements: `vin_rms`, `low_rms`, `high_rms`.

![Passive RC spectrum split plot](assets/plots/passive-rc-spectrum-split.svg)

![Passive RC low-pass FFT plot](assets/plots/passive-rc-spectrum-low-fft.svg)

![Passive RC high-pass FFT plot](assets/plots/passive-rc-spectrum-high-fft.svg)

## Practical Op-Amp Integrator

<div class="schematic-frame" markdown>
![Rendered practical op-amp integrator schematic](assets/generated/opamp-practical-integrator.svg)
</div>

The practical integrator adds a high-value leakage resistor across the feedback
capacitor so the ideal op-amp model has a DC path and the output remains bounded.
The waveform shows ramp-like integration of a small finite-edge pulse input.

```bash
./claw-spice code build examples/transient/opamp-practical-integrator/opamp_practical_integrator.py
./claw-spice sim run examples/transient/opamp-practical-integrator/opamp_practical_integrator.cir
./claw-spice raw plot examples/transient/opamp-practical-integrator/opamp_practical_integrator.raw V(in) V(out) --output runs/latest/opamp_practical_integrator.svg
```

Measurements: `vout_max`, `vout_min`, `vout_avg`.

![Practical op-amp integrator plot](assets/plots/opamp-practical-integrator.svg)

## Practical Op-Amp Differentiator

<div class="schematic-frame" markdown>
![Rendered practical op-amp differentiator schematic](assets/generated/opamp-practical-differentiator.svg)
</div>

The practical differentiator limits high-frequency gain with a feedback
capacitor and finite input edge times. It demonstrates edge-sensitive response
without relying on unrealistic nanosecond transitions.

```bash
./claw-spice code build examples/transient/opamp-practical-differentiator/opamp_practical_differentiator.py
./claw-spice sim run examples/transient/opamp-practical-differentiator/opamp_practical_differentiator.cir
./claw-spice raw plot examples/transient/opamp-practical-differentiator/opamp_practical_differentiator.raw V(in) V(out) --output runs/latest/opamp_practical_differentiator.svg
```

Measurements: `vout_max`, `vout_min`, `vout_rms`.

![Practical op-amp differentiator plot](assets/plots/opamp-practical-differentiator.svg)

## Op-Amp MLP Forward Pass

<div class="schematic-frame" markdown>
![Rendered op-amp MLP forward-pass schematic](assets/generated/opamp-mlp-forward-pass.svg)
</div>

The `opamp-mlp-forward-pass` example implements a three-layer multilayer
perceptron with op-amp weighted-sum neurons. Behavioral clamp sources model ReLU
activations so the transient run can step through multiple input vectors and
measure the expected forward-pass output for each vector.

```bash
./claw-spice code build examples/transient/opamp-mlp-forward-pass/opamp_mlp_forward_pass.py
./claw-spice sim run examples/transient/opamp-mlp-forward-pass/opamp_mlp_forward_pass.cir
./claw-spice raw plot examples/transient/opamp-mlp-forward-pass/opamp_mlp_forward_pass.raw V(x1) V(x2) V(yout) --output runs/latest/opamp_mlp_forward_pass.svg
./claw-spice show examples/transient/opamp-mlp-forward-pass/opamp_mlp_forward_pass.asc --terminal
```

Measurements: `y_vec1`, `y_vec2`, `y_vec3`, `y_vec4`, and `a1b_vec1`.

## Simple Configurable Schmitt Trigger

<div class="schematic-frame" markdown>
![Rendered simple Schmitt trigger schematic](assets/generated/schmitt-trigger-simple.svg)
</div>

The `schmitt-trigger-simple` example is a compact inverting comparator with
positive feedback. A slow triangle-like input crosses the two thresholds, while
`RHYS` and `RREF` set the hysteresis band through
`VTRIP = 4.8 * RREF / (RHYS + RREF)`.

```bash
./claw-spice code build examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.py
./claw-spice sim run examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.cir
./claw-spice raw plot examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.raw V(in) V(trip) V(out) --output runs/latest/schmitt_trigger_simple.svg
./claw-spice show examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.asc --terminal
```

Measurements: `upper_trip`, `lower_trip`, `hysteresis_width`, `expected_trip`,
`expected_hysteresis`.

![Simple Schmitt trigger hysteresis plot](assets/plots/schmitt-trigger-simple.svg)

## Noisy Temperature Switch Schmitt Trigger

<div class="schematic-frame" markdown>
![Rendered temperature switch Schmitt trigger schematic](assets/generated/schmitt-trigger-temperature-switch.svg)
</div>

The `schmitt-trigger-temperature-switch` example turns a noisy analog
temperature signal into a clean `fan_en` output. It combines input filtering, a
quiet mid-supply reference, and configurable hysteresis so the output changes
state at useful turn-on and turn-off points instead of chattering around the
setpoint.

```bash
./claw-spice code build examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.py
./claw-spice sim run examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.cir
./claw-spice raw plot examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.raw V(sensor_raw) V(sense) V(fan_en) --output runs/latest/schmitt_trigger_temperature_switch.svg
./claw-spice show examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.asc --terminal
```

Measurements: `turn_on_sensor`, `turn_off_sensor`, `hysteresis_width`,
`fan_on_time`, `fan_en_avg`, `ripple_reduction`.

![Temperature switch Schmitt trigger plot](assets/plots/schmitt-trigger-temperature-switch.svg)

## Sallen-Key High-Pass Filter

<div class="schematic-frame" markdown>
![Rendered Sallen-Key high-pass schematic](assets/generated/sallen-key-highpass.svg)
</div>

The high-pass Sallen-Key example complements the low-pass filter. It uses the
same scale of `10 kOhm` and `10 nF` parts but moves the capacitors into the input
path so low-frequency content is rejected and high-frequency content remains.

```bash
./claw-spice code build examples/transient/sallen-key-highpass/sallen_key_highpass.py
./claw-spice sim run examples/transient/sallen-key-highpass/sallen_key_highpass.cir
./claw-spice raw plot examples/transient/sallen-key-highpass/sallen_key_highpass.raw V(in) V(out) --output runs/latest/sallen_key_highpass.svg
./claw-spice raw fft examples/transient/sallen-key-highpass/sallen_key_highpass.raw V(out) --output runs/latest/sallen_key_highpass_fft.svg
```

Measurements: `vout_max`, `vout_min`, `vout_avg`.

![Sallen-Key high-pass response plot](assets/plots/sallen-key-highpass.svg)

![Sallen-Key high-pass FFT plot](assets/plots/sallen-key-highpass-fft.svg)
