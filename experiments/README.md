# Experiments

One directory per experiment, named after its paired report slug
(`experiments/lab-01/` ↔ `reports/lab-01/`). Keep the circuit sources
here, committed:

- `<name>.py` — circuit generator (`./claw-spice code build`)
- `<name>.cir` — netlist as simulated
- `<name>.asc` — schematic for rendering

Generated artifacts (`.raw`, `.log`, `.net`) are gitignored; the figures
that matter are exported as PNG into the paired report, where they ARE
committed:

```bash
./claw-spice render experiments/lab-01/<name>.asc \
    --output reports/lab-01/imagens/generated/<name>.svg --png
./claw-spice raw plot <run>.raw V(out) \
    --output reports/lab-01/imagens/generated/<plot>.svg --png
```

Build the paired report with `./claw-spice report lab-01`. Scaffold a new
experiment + report pair with `./claw-spice report new lab-04`.
