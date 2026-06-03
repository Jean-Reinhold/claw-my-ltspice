# Docker LTspice

LTspice has no native Linux Docker binary. `claw-spice` runs the Windows LTspice
build inside a Linux container through Wine and Xvfb.

## Local Build

```bash
./claw-spice build
```

## Apple Silicon Fallback

If the local Wine build hits an Apple Silicon emulation issue, use:

```bash
./claw-spice build-prebuilt
```

This uses `Dockerfile.prebuilt`, which layers `claw-spice` tooling on top of an
existing LTspice/Wine image. The default local build remains preferred for a
cleaner licensing boundary.

## Direct Compose Usage

```bash
docker compose run --rm claw-spice claw-spice doctor
```

## Apple Silicon

The Compose service uses:

```yaml
platform: linux/amd64
```

On Apple Silicon this runs under emulation. GitHub-hosted Ubuntu runners are
typically x86_64, so CI avoids that local emulation cost.

## Licensing

The Dockerfile downloads LTspice during build. This repository does not
redistribute LTspice binaries or prebuilt images containing LTspice.
