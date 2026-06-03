#!/usr/bin/env bash
set -euo pipefail

export HOME="${HOME:-/tmp/claw-home}"
export WINEPREFIX="${WINEPREFIX:-/tmp/wine-prefix}"
export LOGNAME="${LOGNAME:-claw}"
export USER="${USER:-claw}"

mkdir -p "$HOME"

TEMPLATE=/opt/wineprefix-template
if [ ! -d "$WINEPREFIX" ]; then
  echo "[entrypoint] Materialising WINEPREFIX at ${WINEPREFIX} (uid $(id -u))" >&2
  cp -a --no-preserve=ownership "$TEMPLATE" "$WINEPREFIX"
fi

USER_DISPLAY="${DISPLAY:-}"
XVFB_DISPLAY="${XVFB_DISPLAY:-:99}"
DISPLAY_NUM="${XVFB_DISPLAY#:}"
XVFB_RESOLUTION="${XVFB_RESOLUTION:-1280x960x16}"

if [ -n "$USER_DISPLAY" ]; then
  export DISPLAY="$USER_DISPLAY"
else
  rm -f "/tmp/.X${DISPLAY_NUM}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM}" 2>/dev/null || true
  Xvfb "$XVFB_DISPLAY" -screen 0 "$XVFB_RESOLUTION" -nolisten tcp >/tmp/xvfb.log 2>&1 &
  export DISPLAY="$XVFB_DISPLAY"
fi

exec "$@"
