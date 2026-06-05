# Models And Licensing

SPICE models are source code with licensing and provenance requirements. Do not
commit unknown-license model files.

## Manifest

Track model intent and redistribution status in:

```text
models/manifest.toml
```

Each entry should record:

- model or subcircuit name
- model kind
- source or intended source
- file path when committed
- license
- redistribution status
- notes on accuracy, pin order, and intended use

## Current Entries

| Model | Kind | Source | Redistribution | Use |
| --- | --- | --- | --- | --- |
| `CLAW_IDEAL_OPAMP` | op-amp | repo-owned | allowed | educational topology validation |
| `DCLAW` | diode | repo-owned inline model | allowed | educational nonlinear examples |
| `2N3904` | BJT | LTspice built-in target | not redistributed | future built-in-library examples |
| `LM741` | op-amp | vendor/user-installed target | not redistributed | future model-onboarding example |
| `TL072` | op-amp | vendor/user-installed target | not redistributed | future model-onboarding example |
| `LM358` | op-amp | vendor/user-installed target | not redistributed | future model-onboarding example |

## Onboarding Workflow

Before adding a model:

1. Identify the exact source and author/vendor.
2. Read the license and redistribution terms.
3. Record the model in `models/manifest.toml`.
4. Verify `.model` or `.subckt` names.
5. Verify pin order and symbol mapping.
6. Add or document the matching `.asy` symbol if rendering needs it.
7. Add a small example or fixture.
8. Run the Docker simulation/rendering loop.

## Accepted Model Categories

- Repo-owned educational models with explicit project license.
- LTspice built-in models referenced from an installed LTspice runtime, not
  copied into the repository.
- Vendor/user-installed models documented in the manifest but not vendored until
  redistribution is explicitly allowed.

## Rejected Model Categories

- Unknown-license files copied from forums, PDFs, textbooks, or random archives.
- Vendor models without redistribution permission.
- Binary model packages or installers.
- Models whose pin order cannot be verified.

## Current Educational Models

`CLAW_IDEAL_OPAMP` and `DCLAW` are intentionally simple. They are useful for
workflow validation, topology documentation, rendering, and CI smoke tests. They
are not substitutes for real vendor macromodels when device accuracy matters.
