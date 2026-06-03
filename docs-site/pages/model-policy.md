# Model Policy

Do not commit unknown-license SPICE model files.

Track model intent and source status in:

```text
models/manifest.toml
```

Before adding a model, record:

- Source URL or package.
- Vendor or author.
- License.
- Redistribution status.
- `.model` or `.subckt` name.
- Pin order.
- Required symbol attributes.
- CI installation strategy.

Classic targets include LM741, TL072, LM358, 2N3904, 2N3906, 1N4148, and 1N400x.
Exact vendor macromodels require license review before vendoring.
