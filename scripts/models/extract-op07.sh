#!/usr/bin/env bash
# Extract the ADI OP07 macromodel bundled with the container's LTspice install
# into experiments/rs1-nao-idealidades-op07/models/op07-extracted.lib (gitignored, documentation
# only — netlists load the model via `.lib LTC.lib` at simulation time).
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
DEST_DIR="experiments/rs1-nao-idealidades-op07/models"
DEST="$DEST_DIR/op07-extracted.lib"

mkdir -p "$ROOT/$DEST_DIR"

docker compose -f "$ROOT/docker-compose.yml" run --rm -T --entrypoint /bin/bash claw-spice -c '
  set -euo pipefail
  LIB="/opt/wineprefix-template/drive_c/users/wineuser/AppData/Local/LTspice/lib/sub/LTC.lib"
  {
    echo "* OP07 macromodel extracted from the LTspice install inside the claw-spice image."
    echo "* Source file: lib/sub/LTC.lib (LTspice 26, Analog Devices). NOT redistributable;"
    echo "* kept out of git. Regenerate with scripts/models/extract-op07.sh."
    echo "*"
    for grade in OP07 OP07A OP07C OP07E; do
      awk -v g="$grade" "
        toupper(\$0) ~ (\"^\\\\.SUBCKT \" g \" \") {p=1}
        p {print}
        p && toupper(\$0) ~ (\"^\\\\.ENDS\") {p=0; print \"*\"}
      " "$LIB"
    done
  } > "'"$DEST"'"
  wc -l "'"$DEST"'"
'
echo "Extracted to $DEST"
