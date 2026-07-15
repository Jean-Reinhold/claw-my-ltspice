#!/usr/bin/env bash
# Fetch the ADI OP07 datasheet (Rev. G) used by reports/rs1-nao-idealidades-op07 (RS1).
# analog.com blocks non-browser clients; the Internet Archive mirror serves
# the identical PDF. Kept out of git (copyrighted vendor doc).
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
URL="https://web.archive.org/web/2024id_/https://www.analog.com/media/en/technical-documentation/data-sheets/OP07.pdf"
DEST="$ROOT/experiments/rs1-nao-idealidades-op07/datasheet/op07.pdf"
mkdir -p "$(dirname "$DEST")"
curl -sL --max-time 120 -o "$DEST.dl" "$URL"
if file "$DEST.dl" | grep -q gzip; then mv "$DEST.dl" "$DEST.gz"; gunzip -f "$DEST.gz"; else mv "$DEST.dl" "$DEST"; fi
file "$DEST"
cp "$DEST" "$ROOT/reports/rs1-nao-idealidades-op07/imagens/datasheet-op07.pdf"
echo "OK: $DEST (+ copia em reports/rs1-nao-idealidades-op07/imagens/datasheet-op07.pdf)"
