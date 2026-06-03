# Notices

`claw-spice` is open-source tooling around LTspice. LTspice itself is not part
of this repository.

## LTspice

LTspice is owned by Analog Devices, Inc. The Dockerfile downloads the LTspice
installer from Analog Devices during a local or CI image build. This repository
does not redistribute LTspice binaries, installers, bundled symbols, bundled
models, or generated Wine prefixes.

Review Analog Devices' LTspice terms before redistributing any container image
that contains LTspice.

## Component Models

SPICE model files can carry vendor-specific redistribution terms. Do not commit
third-party model files unless their source and redistribution license are clear.
Use `models/manifest.toml` to document requested or installed model sources.

## Third-Party Tools

This project uses or documents integration with:

- Wine and Xvfb for running Windows LTspice in Linux containers.
- PyLTSpice and spicelib for LTspice automation and result parsing.
- ltspice-to-svg for converting LTspice `.asc` schematics to SVG.
- chafa for terminal image previews.
- MkDocs Material for GitHub Pages documentation.
