# Examples

## RC Step Response

![Rendered RC step response schematic](assets/generated/rc-step.svg)

The first example is a 1 kOhm / 1 uF RC step response. The expected time
constant is approximately 1 ms.

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice show examples/transient/rc-step/rc_step.asc
./claw-spice raw plot runs/latest/rc_step.raw V(out) --output runs/latest/rc_step_vout.svg
```

Measurements:

- `vout_max`: maximum output voltage.
- `vout_ss`: output voltage near the end of the run.
- `tau_rise`: time at which `V(out)` reaches 63.2% of 5 V.

Expected signal plot:

![RC step output plot](assets/plots/rc-step-vout.svg)

## Op-Amp Voltage Follower

![Rendered op-amp voltage follower schematic](assets/generated/opamp-voltage-follower.svg)

This example uses the repo-owned `CLAW_IDEAL_OPAMP` macromodel as a unity-gain
buffer. It checks that `V(out)` tracks `V(in)` after the transient step settles.

```bash
./claw-spice code build examples/transient/opamp-voltage-follower/opamp_voltage_follower.py
./claw-spice sim run examples/transient/opamp-voltage-follower/opamp_voltage_follower.cir
./claw-spice raw plot runs/latest/opamp_voltage_follower.raw V(in) V(out) --output runs/latest/opamp_voltage_follower.svg
./claw-spice show examples/transient/opamp-voltage-follower/opamp_voltage_follower.asc
```

Measurements:

- `vout_2ms`: output voltage after the input step settles.
- `tracking_error_max`: maximum absolute `V(out)-V(in)` error over the settled window.

Expected signal plot:

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

## Op-Amp Non-Inverting Gain

![Rendered op-amp non-inverting schematic](assets/generated/opamp-noninverting.svg)

This example uses feedback resistors for an expected gain of approximately
`1 + Rf/Rg = 3`.

```bash
./claw-spice code build examples/transient/opamp-noninverting/opamp_noninverting.py
./claw-spice sim run examples/transient/opamp-noninverting/opamp_noninverting.cir
./claw-spice raw plot runs/latest/opamp_noninverting.raw V(in) V(out) --output runs/latest/opamp_noninverting.svg
./claw-spice show examples/transient/opamp-noninverting/opamp_noninverting.asc
```

Measurements:

- `vout_2ms`: output voltage after settling.
- `gain_2ms`: measured gain at 2 ms.

Expected signal plot:

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

## Op-Amp Inverting Gain

![Rendered op-amp inverting schematic](assets/generated/opamp-inverting.svg)

This example uses feedback resistors for an expected gain of approximately
`-Rf/Rin = -2`.

```bash
./claw-spice code build examples/transient/opamp-inverting/opamp_inverting.py
./claw-spice sim run examples/transient/opamp-inverting/opamp_inverting.cir
./claw-spice raw plot runs/latest/opamp_inverting.raw V(in) V(out) --output runs/latest/opamp_inverting.svg
./claw-spice show examples/transient/opamp-inverting/opamp_inverting.asc
```

Measurements:

- `vout_2ms`: output voltage after settling.
- `gain_2ms`: measured gain at 2 ms.

Expected signal plot:

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

## Op-Amp Inverting Summing Amplifier

![Rendered op-amp summing schematic](assets/generated/opamp-summing.svg)

This example uses two weighted input resistors and one feedback resistor. The
expected relationship is approximately `V(out) = -(2 * V(in1) + V(in2))`.

```bash
./claw-spice code build examples/transient/opamp-summing/opamp_summing.py
./claw-spice sim run examples/transient/opamp-summing/opamp_summing.cir
./claw-spice raw plot runs/latest/opamp_summing.raw V(in1) V(in2) V(out) --output runs/latest/opamp_summing.svg
./claw-spice show examples/transient/opamp-summing/opamp_summing.asc
```

Measurements:

- `vout_2ms`: output after the delayed second input has settled.
- `vout_3ms`: output later in the same state.

Expected signal plot:

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

## Op-Amp Difference Amplifier

![Rendered op-amp difference schematic](assets/generated/opamp-difference.svg)

This example uses matched resistor ratios for an expected relationship of
approximately `V(out) = 2 * (V(plus) - V(minus))`.

```bash
./claw-spice code build examples/transient/opamp-difference/opamp_difference.py
./claw-spice sim run examples/transient/opamp-difference/opamp_difference.cir
./claw-spice raw plot runs/latest/opamp_difference.raw V(plus) V(minus) V(out) --output runs/latest/opamp_difference.svg
./claw-spice show examples/transient/opamp-difference/opamp_difference.asc
```

Measurements:

- `vout_2ms`: output after both inputs have settled.
- `vout_3ms`: output later in the same state.

Expected signal plot:

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

## Op-Amp Buffered Active Low-Pass

![Rendered active low-pass schematic](assets/generated/opamp-active-lowpass.svg)

This example filters a pulsed input with an RC pole and buffers the filtered node
with the generic op-amp model.

```bash
./claw-spice code build examples/transient/opamp-active-lowpass/opamp_active_lowpass.py
./claw-spice sim run examples/transient/opamp-active-lowpass/opamp_active_lowpass.cir
./claw-spice raw plot runs/latest/opamp_active_lowpass.raw V(in) V(filt) V(out) --output runs/latest/opamp_active_lowpass.svg
./claw-spice show examples/transient/opamp-active-lowpass/opamp_active_lowpass.asc
```

Measurements:

- `vout_avg`: average output over the later settled window.
- `vout_max`: maximum output over the later settled window.

Expected signal plot:

![Buffered active low-pass plot](assets/plots/opamp-active-lowpass.svg)
