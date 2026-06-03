---
name: ltspice-measurements-analysis
description: Use when adding .meas statements, reading LTspice .log files, parsing .raw traces, computing signal statistics, comparing results, or producing simulation summaries.
---

# LTspice Measurements And Analysis

## Measurement Policy

Every example should include objective `.meas` checks. Prefer expected ranges
over exact values in tests and summaries.

## Standard Summary

Report:

- Circuit path.
- Backend: LTspice Docker.
- Simulation directive.
- Generated `.raw` and `.log` paths.
- Measurements with values, units, expected ranges, and pass/fail status.
- Warnings and errors from `.log`.
- Rendered schematic path.

## Useful Commands

```bash
./claw-spice log summary <file.log>
./claw-spice log summary <file.log> --json
./claw-spice raw traces <file.raw>
./claw-spice raw stats <file.raw> V(out)
```

## Measurement Gotchas

- A failed `.meas` can appear in the log without failing the LTspice process.
- A missing trigger event often means the simulation duration or threshold is
  wrong.
- AC and transient measurements use different syntax and interpretation.
- Always inspect warnings; numerical warnings can invalidate measurements.

## OpenCode Rule

If a measurement fails, say so and explain whether the circuit, test bench, or
expected range is wrong.
