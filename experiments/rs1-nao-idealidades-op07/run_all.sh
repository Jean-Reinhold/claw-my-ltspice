#!/usr/bin/env bash
# RS1 (Aula S1) - pipeline completo do experimento OP07.
#
# Cada item roda em seu PROPRIO container descartavel (docker compose run --rm),
# com WINEPREFIX materializado por container — execucoes independentes que
# podem rodar em paralelo entre si e em paralelo com outros experimentos.
#
# Lote A (itens 1-3 e o teste extra do item 7) nao tem dependencias e roda
# em paralelo. O item 3 mede o VOS usado como compensacao nos itens 4-6
# (vos_comp.inc), entao o Lote B (itens 4-6) so comeca depois do Lote A.
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"

LAB=experiments/rs1-nao-idealidades-op07

sim() {
  # 2400 s: sob contencao (varios containers Wine/qemu em paralelo no mesmo
  # host) o startup do LTspice pode levar varios minutos.
  docker compose run --rm -T claw-spice claw-spice sim run "$LAB/$1" --timeout 2400
}

py() {
  docker compose run --rm -T claw-spice python3 "$LAB/analyze.py" "$@"
}

echo "== Lote A: itens 1-3 e teste extra (item 7) em containers paralelos =="
pids=()
sim item1_bias.cir & pids+=("$!")
sim item2_ios.cir & pids+=("$!")
sim item3_vos.cir & pids+=("$!")
sim item7_slew_ada.cir & pids+=("$!")
fail=0
for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
[ "$fail" -eq 0 ] || { echo "ERRO: Lote A falhou" >&2; exit 1; }

echo "== Gerando vos_comp.inc com o VOS medido no item 3 =="
py --phase vos

echo "== Lote B: itens 4-6 em containers paralelos =="
pids=()
sim item4_avd.cir & pids+=("$!")
sim item5_acm.cir & pids+=("$!")
sim item6_slew.cir & pids+=("$!")
fail=0
for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
[ "$fail" -eq 0 ] || { echo "ERRO: Lote B falhou" >&2; exit 1; }

echo "== Medidas e graficos para o relatorio =="
py --phase report

echo "OK: $LAB/results.json, $LAB/results.md e reports/rs1-nao-idealidades-op07/imagens/generated/"
