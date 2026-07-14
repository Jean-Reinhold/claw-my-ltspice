#!/usr/bin/env bash
# UFPel lab-report builds — Docker only (texlive image via the `latex`
# compose service); the host never needs a TeX installation.
#
# Usage:
#   ./claw-spice report            # build -> latex/build/main.pdf
#   ./claw-spice report clean      # remove build output
#   ./claw-spice report watch      # rebuild on every .tex save (latexmk -pvc)
#   ./claw-spice report serve      # auto-refreshing viewer on http://localhost:8001
set -uo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker daemon is not running — start Docker and retry." >&2
  echo "[INFO]  Reports build only in the texlive container (./claw-spice report)." >&2
  exit 1
fi

case "${1:-build}" in
  build)
    echo "[INFO] Building report (first run pulls the ~3GB texlive image — be patient)..."
    if docker compose run --rm latex latexmk -pdf -interaction=nonstopmode -outdir=build main.tex; then
      echo "[OK] PDF ready: latex/build/main.pdf"
    else
      status=$?
      echo "[ERROR] LaTeX build failed. First error block from latex/build/main.log:" >&2
      if [ -f latex/build/main.log ]; then
        awk '/^!/{found=1} found{print; n++} n>=15{exit}' latex/build/main.log >&2
        echo "[INFO] Full log: latex/build/main.log" >&2
      else
        echo "[WARN] No main.log was produced — read the latexmk output above." >&2
      fi
      exit "$status"
    fi
    ;;
  clean)
    docker compose run --rm latex latexmk -C -outdir=build main.tex >/dev/null 2>&1 || true
    rm -rf latex/build
    echo "[OK] LaTeX build output removed."
    ;;
  watch)
    docker compose run --rm latex latexmk -pvc -pdf -interaction=nonstopmode -outdir=build main.tex
    ;;
  serve)
    echo "[INFO] Report preview: http://localhost:8001 (Ctrl+C to stop)"
    echo "[INFO] Pair with './claw-spice report watch' for rebuild-on-save."
    docker compose run --rm --service-ports latex python3 /opt/report/serve_pdf.py 8001
    ;;
  *)
    echo "Usage: ./claw-spice report [build|clean|watch|serve]" >&2
    exit 2
    ;;
esac
