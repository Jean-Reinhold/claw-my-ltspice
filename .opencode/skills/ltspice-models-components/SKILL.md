---
name: ltspice-models-components
description: Use when adding, selecting, installing, documenting, or debugging LTspice component models, classic op-amps, vendor libraries, .include, .lib, .model, and .subckt files.
---

# LTspice Models And Components

## Model Policy

Do not vendor unknown-license model files. Track model intent and source status
in `models/manifest.toml`.

Before adding a model, record:

- Source URL or package.
- Vendor or author.
- License.
- Redistribution status.
- `.model` or `.subckt` name.
- Pin order.
- Required symbol attributes.
- CI installation strategy.

## Classic Targets

Classic parts such as LM741, TL072, LM358, 2N3904, 2N3906, 1N4148, and 1N400x
are important, but exact model files must be source/license checked.

Prefer LTspice built-ins for basic transistors and diodes when adequate. Use
generic/universal op-amp models for topology validation before exact vendor
macromodels.

## Includes

Prefer repo-relative paths and explicit directives:

```spice
.include models/vendor/example.lib
.lib models/vendor/example.lib
```

Avoid hidden host-specific LTspice library paths in examples and CI.

## OpenCode Rule

Before committing a model file, identify source, license, redistribution status,
and pin order. If uncertain, document a manifest entry instead of committing the
model.
