# Docker Runtime

`claw-spice` is Docker-first. The host wrapper starts a container that contains
the Python package, Wine, Xvfb, LTspice batch execution, schematic rendering,
terminal preview tools, waveform plotting, and MkDocs.

## Host And Container Boundary

Normal usage starts from the repository root:

```bash
./claw-spice doctor
```

The host wrapper runs the container CLI roughly as:

```bash
docker compose run --rm claw-spice claw-spice doctor
```

The wrapper also exports `HOST_UID` and `HOST_GID` so generated files are owned
by the host user rather than by root inside the mounted workspace.

## Runtime Contents

The container provides:

- LTspice through Wine
- Xvfb for headless GUI-dependent LTspice paths
- `claw-spice` Python CLI
- `ltspice_to_svg` / `ltspice-to-svg` for real `.asc` rendering
- `chafa` for terminal previews
- `rsvg-convert` or `resvg` when available for PNG conversion
- MkDocs and Material for MkDocs for the Pages site

Check the runtime with:

```bash
./claw-spice doctor
./claw-spice doctor --json
```

## Build Paths

Preferred build:

```bash
./claw-spice build
```

The default Dockerfile downloads LTspice from Analog Devices during the user's
build. The repository does not redistribute LTspice binaries.

Optional local fallback:

```bash
./claw-spice build-prebuilt
```

The fallback layers project tooling on top of a prebuilt LTspice/Wine image. It
is useful when a local Apple Silicon/Wine build is blocked, but the default build
is the cleaner licensing boundary.

## Apple Silicon

The Compose service declares:

```yaml
platform: linux/amd64
```

On Apple Silicon this runs under emulation. GitHub-hosted Ubuntu runners are
typically x86_64, so CI avoids that local emulation cost.

## Output Locations

- Generated examples: `runs/latest/examples/...`
- Stable local render outputs: `runs/latest/*.svg`
- Documentation schematic assets: `docs-site/pages/assets/generated/*.svg`
- Documentation plot assets: `docs-site/pages/assets/plots/*.svg`
- Example preview SVGs: `examples/transient/*/preview.svg`

Generated schematic previews are intentionally ignored by Git so they can be
recreated from source. Stable documentation plot assets are committed because
they are deterministic and lightweight.

## Shell Access

Use a container shell for diagnosis, not for installing host dependencies:

```bash
./claw-spice shell
```

From inside the container, run the container CLI directly:

```bash
claw-spice doctor
claw-spice examples list
```

## Licensing Boundary

Do not commit LTspice binaries, Wine prefixes, generated `.raw` files, or
unknown-license vendor models. Record model provenance in `models/manifest.toml`.
