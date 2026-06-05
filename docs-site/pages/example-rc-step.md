# RC Step Walkthrough

The RC step example is the smallest complete circuit in the project. It verifies
generation, simulation, measurement parsing, raw plotting, and schematic
rendering without active models.

<div class="schematic-frame" markdown>
![Rendered RC step response schematic](assets/generated/rc-step.svg)
</div>

## Theory

The circuit uses `R = 1 kOhm` and `C = 1 uF`, so the nominal time constant is:

```text
tau = R * C = 1 ms
```

For a `5 V` step, the ideal capacitor voltage is:

```text
V(out) = 5 * (1 - exp(-t / tau))
```

At one time constant, `V(out)` should be about `63.2%` of final value, or
approximately `3.16 V`.

## Files

| File | Purpose |
| --- | --- |
| `examples/transient/rc-step/rc_step.py` | source generator |
| `examples/transient/rc-step/rc_step.cir` | committed netlist |
| `examples/transient/rc-step/rc_step.asc` | committed schematic |
| `docs-site/pages/assets/plots/rc-step-vout.svg` | expected docs plot |

## Commands

```bash
./claw-spice code build examples/transient/rc-step/rc_step.py
./claw-spice sim run examples/transient/rc-step/rc_step.cir
./claw-spice log summary examples/transient/rc-step/rc_step.log
./claw-spice raw traces examples/transient/rc-step/rc_step.raw
./claw-spice raw plot examples/transient/rc-step/rc_step.raw V(in) V(out) --output runs/latest/rc_step.svg
./claw-spice show examples/transient/rc-step/rc_step.asc --terminal
```

## Measurements

- `vout_max`: maximum output voltage.
- `vout_ss`: output voltage near the end of the transient run.
- `tau_rise`: time when `V(out)` reaches `3.16 V`.

![RC step output plot](assets/plots/rc-step-vout.svg)

## Common Mistakes

- Missing ground node `0`.
- Using `1M` when `1MEG` was intended.
- Using too-large max timestep and missing the time-constant crossing.
- Plotting from the wrong `.raw` path after regenerating examples into `runs/latest`.
