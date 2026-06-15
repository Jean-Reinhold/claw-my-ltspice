# Schmitt Trigger Walkthrough

The Schmitt trigger examples show why positive feedback is useful when a slow or
noisy analog signal must become a clean digital decision. Both examples use the
repo-owned `CLAW_IDEAL_OPAMP` model so the topology, measurements, and layout can
be reviewed without adding vendor model licensing questions.

## Simple Configurable Trigger

The simple example is an inverting Schmitt comparator. The input drives the
inverting input, while the non-inverting input receives a fraction of the output
through `RHYS` and `RREF`.

```text
VTRIP = 4.8 * RREF / (RHYS + RREF)
```

With the default `RHYS=100k` and `RREF=20k`, the ideal trip level is about
`0.8 V`. A rising input crosses the upper threshold and drives the output low.
The low output moves the trip node to about `-0.8 V`, so the input must fall
below that lower threshold before the output returns high.

```bash
./claw-spice code build examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.py
./claw-spice sim run examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.cir
./claw-spice log summary runs/latest/schmitt_trigger_simple.log
./claw-spice raw plot runs/latest/schmitt_trigger_simple.raw V(in) V(trip) V(out) --output runs/latest/schmitt_trigger_simple.svg
./claw-spice show examples/transient/schmitt-trigger-simple/schmitt_trigger_simple.asc --terminal
```

![Simple Schmitt trigger hysteresis plot](assets/plots/schmitt-trigger-simple.svg)

Key measurements: `upper_trip`, `lower_trip`, `hysteresis_width`,
`expected_trip`, and `expected_hysteresis`.

## Temperature Switch Use Case

The practical example models a temperature-controlled fan-enable signal. The raw
sensor voltage includes high-frequency ripple to represent cable pickup or supply
noise. The circuit then adds three practical blocks before producing `fan_en`:

- `RFLT` and `CFILT` attenuate ripple before the comparator input.
- `RTOP`, `RBOT`, and `CREF` make a quiet mid-supply reference.
- `RHYS` feeds back a small part of the output state, creating separate turn-on
  and turn-off thresholds.

For the default non-inverting topology, the sensor thresholds are:

```text
UPPER_TRIP = VREF * (1 + RIN/RHYS) - VOUT_L * (RIN/RHYS)
LOWER_TRIP = VREF * (1 + RIN/RHYS) - VOUT_H * (RIN/RHYS)
```

With `RIN=100k`, `RHYS=1Meg`, `VOUT_H=4.8`, and `VOUT_L=0.2`, the turn-on point
is near `2.73 V`, the turn-off point is near `2.27 V`, and the hysteresis band is
about `460 mV`.

```bash
./claw-spice code build examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.py
./claw-spice sim run examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.cir
./claw-spice log summary runs/latest/schmitt_trigger_temperature_switch.log
./claw-spice raw plot runs/latest/schmitt_trigger_temperature_switch.raw V(sensor_raw) V(sense) V(fan_en) --output runs/latest/schmitt_trigger_temperature_switch.svg
./claw-spice show examples/transient/schmitt-trigger-temperature-switch/schmitt_trigger_temperature_switch.asc --terminal
```

![Temperature switch Schmitt trigger plot](assets/plots/schmitt-trigger-temperature-switch.svg)

Key measurements: `turn_on_sensor`, `turn_off_sensor`, `hysteresis_width`,
`expected_upper`, `expected_lower`, `fan_on_time`, `raw_ripple_pp`, and
`filtered_ripple_pp`, and `ripple_reduction`.

## Design Tuning

Use a wider hysteresis band when the sensor is noisy or the controlled load would
wear out from rapid toggling. Use a narrower band when the controlled process can
tolerate more switching and needs tighter regulation.

For the simple inverting trigger, increase `RREF` or decrease `RHYS` to widen the
band. For the practical non-inverting trigger, decrease `RHYS` relative to `RIN`
to widen the band.
