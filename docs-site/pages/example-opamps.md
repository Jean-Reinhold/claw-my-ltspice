# Op-Amp Walkthroughs

The op-amp examples use the repo-owned `CLAW_IDEAL_OPAMP` educational macromodel.
It is useful for topology and workflow validation, not vendor-accurate device
prediction.

## Shared Assumptions

- Supply rails are explicit and visible in the rendered schematic.
- The model is included from `examples/lib/claw_opamps.lib` in committed source examples.
- Generated runs copy the model beside generated files and include `claw_opamps.lib`.
- Measurements use settled windows to avoid startup transients dominating results.

## Voltage Follower

<div class="schematic-frame" markdown>
![Rendered op-amp voltage follower schematic](assets/generated/opamp-voltage-follower.svg)
</div>

The follower verifies unity feedback:

```text
V(out) ~= V(in)
```

Measurements: `vout_2ms`, `tracking_error_max`.

![Op-amp voltage follower plot](assets/plots/opamp-voltage-follower.svg)

## Non-Inverting Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp non-inverting schematic](assets/generated/opamp-noninverting.svg)
</div>

Closed-loop gain:

```text
gain = 1 + Rf / Rg = 3
```

Measurements: `vout_2ms`, `gain_2ms`.

![Op-amp non-inverting gain plot](assets/plots/opamp-noninverting.svg)

## Inverting Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp inverting schematic](assets/generated/opamp-inverting.svg)
</div>

Closed-loop gain:

```text
gain = -Rf / Rin = -2
```

Measurements: `vout_2ms`, `gain_2ms`.

![Op-amp inverting gain plot](assets/plots/opamp-inverting.svg)

## Summing Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp summing schematic](assets/generated/opamp-summing.svg)
</div>

The inverting summer approximates:

```text
V(out) = -Rf * (V(in1) / R1 + V(in2) / R2)
```

Measurements: `vout_2ms`, `vout_3ms`.

![Op-amp summing amplifier plot](assets/plots/opamp-summing.svg)

## Difference Amplifier

<div class="schematic-frame" markdown>
![Rendered op-amp difference schematic](assets/generated/opamp-difference.svg)
</div>

Matched resistor ratios create a differential output proportional to
`V(plus) - V(minus)`.

Measurements: `vout_2ms`, `vout_3ms`.

![Op-amp difference amplifier plot](assets/plots/opamp-difference.svg)

## Practical Integrator And Differentiator

The practical integrator uses a leakage resistor across the feedback capacitor to
define DC gain. The practical differentiator adds bandwidth limiting so ideal
high-frequency gain does not dominate.

![Practical op-amp integrator plot](assets/plots/opamp-practical-integrator.svg)

![Practical op-amp differentiator plot](assets/plots/opamp-practical-differentiator.svg)
