#!/usr/bin/env bash
# UFPel lab-report builds — Docker only (texlive image via the `latex`
# compose service); the host never needs a TeX installation.
#
# Reports live one-per-directory under reports/ (reports/_template is the
# skeleton for new ones). Shared class/bibstyle/logos live in latex/ and
# reach latexmk through TEXINPUTS/BSTINPUTS set on the compose service.
#
# Usage:
#   ./claw-spice report [<slug>|all]      # build reports/<slug>/build/main.pdf (default: all)
#   ./claw-spice report clean [<slug>|all]
#   ./claw-spice report watch <slug>      # rebuild on every source save (latexmk -pvc)
#   ./claw-spice report serve <slug>      # auto-refreshing viewer on http://localhost:8001
#   ./claw-spice report new <slug>        # scaffold reports/<slug> + experiments/<slug>
set -uo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"

list_reports() {
  find reports -mindepth 2 -maxdepth 2 -name main.tex 2>/dev/null \
    | sed 's|^reports/||; s|/main\.tex$||' | grep -v '^_template$' | sort
}

require_slug() {
  if [ ! -f "reports/$1/main.tex" ]; then
    echo "[ERROR] No report at reports/$1 (expected reports/$1/main.tex)." >&2
    echo "[INFO]  Available reports: $(list_reports | tr '\n' ' ')" >&2
    exit 1
  fi
}

require_docker() {
  if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker daemon is not running — start Docker and retry." >&2
    echo "[INFO]  Reports build only in the texlive container (./claw-spice report)." >&2
    exit 1
  fi
}

build_one() {
  local slug="$1" status
  echo "[INFO] Building reports/$slug (first run pulls the ~3GB texlive image — be patient)..."
  if docker compose run --rm latex latexmk -pdf -interaction=nonstopmode -outdir=build -cd "reports/$slug/main.tex"; then
    echo "[OK] PDF ready: reports/$slug/build/main.pdf"
  else
    status=$?
    echo "[ERROR] LaTeX build failed for reports/$slug. First error block from reports/$slug/build/main.log:" >&2
    if [ -f "reports/$slug/build/main.log" ]; then
      awk '/^!/{found=1} found{print; n++} n>=15{exit}' "reports/$slug/build/main.log" >&2
      echo "[INFO] Full log: reports/$slug/build/main.log" >&2
    else
      echo "[WARN] No main.log was produced — read the latexmk output above." >&2
    fi
    return "$status"
  fi
}

sub="${1:-all}"
case "$sub" in
  clean)
    target="${2:-all}"
    if [ "$target" = "all" ]; then
      for s in $(list_reports); do rm -rf "reports/$s/build"; done
    else
      require_slug "$target"
      rm -rf "reports/$target/build"
    fi
    echo "[OK] LaTeX build output removed."
    ;;
  watch)
    slug="${2:?Usage: ./claw-spice report watch <slug>}"
    require_slug "$slug"
    require_docker
    docker compose run --rm latex latexmk -pvc -pdf -interaction=nonstopmode -outdir=build -cd "reports/$slug/main.tex"
    ;;
  serve)
    slug="${2:?Usage: ./claw-spice report serve <slug>}"
    require_slug "$slug"
    require_docker
    echo "[INFO] Report preview: http://localhost:8001 (Ctrl+C to stop)"
    echo "[INFO] Pair with './claw-spice report watch $slug' for rebuild-on-save."
    docker compose run --rm --service-ports \
      -e REPORT_PDF="/workspace/reports/$slug/build/main.pdf" \
      latex python3 scripts/report/serve_pdf.py 8001
    ;;
  new)
    slug="${2:?Usage: ./claw-spice report new <slug>}"
    if [ -e "reports/$slug" ]; then
      echo "[ERROR] reports/$slug already exists." >&2
      exit 1
    fi
    cp -R reports/_template "reports/$slug"
    mkdir -p "experiments/$slug"
    echo "[OK] Created reports/$slug and experiments/$slug."
    echo "[INFO] Fill the <placeholders> in reports/$slug/main.tex, then: ./claw-spice report $slug"
    ;;
  all)
    require_docker
    failed=0
    for s in $(list_reports); do
      build_one "$s" || failed=1
    done
    exit "$failed"
    ;;
  *)
    require_slug "$sub"
    require_docker
    build_one "$sub"
    ;;
esac
