---
name: ltspice-debugging-convergence
description: Use when LTspice simulations fail, hang, produce convergence errors, missing model errors, failed measurements, empty raw files, or suspicious waveforms.
---

# LTspice Debugging And Convergence

## Debug Order

1. Read the `.log` first.
2. Classify the failure: syntax, missing model, singular matrix, timestep,
   convergence, failed measurement, Docker/Wine path, or artifact issue.
3. Check ground and DC paths.
4. Check pin order and model names.
5. Check unrealistic ideal loops and discontinuities.
6. Simplify the circuit, then reintroduce blocks.
7. Use solver options only after topology and modeling checks.

## Common Problems

| Problem | Preferred Fix |
| --- | --- |
| Floating node | Add a DC path or fix a missing connection. |
| Singular matrix | Check ground, dependent source loops, floating capacitors. |
| Ideal voltage loop | Add small series resistance. |
| Ideal current source into open node | Add load or leakage path. |
| Inductor/source loop | Add winding/source resistance. |
| Missing model | Fix `.include`, `.lib`, or model name. |
| Failed `.meas` | Check trigger condition, edge count, and simulation duration. |

## Solver Options

Use `.options` sparingly and document why:

```spice
.options reltol=0.003
.options gmin=1e-10
.options abstol=1e-10
.options method=gear
```

Do not use options to hide an unrealistic or incorrectly connected circuit.

## OpenCode Rule

Make the smallest physical change first and explain its electrical meaning.
