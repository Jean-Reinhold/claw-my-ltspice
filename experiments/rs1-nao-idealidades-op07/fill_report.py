#!/usr/bin/env python3
"""Preenche os placeholders %%TOKEN%% do relatorio rs1-nao-idealidades-op07 com os valores
medidos em results.json e com as netlists como simuladas.

Rodar apos analyze.py --phase report:
  python3 experiments/rs1-nao-idealidades-op07/fill_report.py
Idempotente apenas na primeira execucao (os tokens deixam de existir);
para re-preencher, restaure os .tex com git antes.
"""

from __future__ import annotations

import json
from pathlib import Path

LAB = Path(__file__).resolve().parent
REPORT = LAB.parent.parent / "reports" / "rs1-nao-idealidades-op07"

results = json.loads((LAB / "results.json").read_text())

ib_plus = results["item1"]["ib_plus_A"]
vout1 = results["item1"]["vout_V"]
ib_minus = results["item2"]["ib_minus_A"]
vout2 = results["item2"]["vout_V"]
ios = abs(results["item2"]["ios_A"])
vos = results["item3"]["vos_V"]
avd = results["item4"]["avd"]
avd_db = results["item4"]["avd_db"]
acm = results["item5"]["acm"]
cmrr_db = results["item5"]["cmrr_db"]
sr = results["item6"]["sr_max_V_per_us"]
sr_avg = results["item6"]["sr_media_10V_meas_V_per_us"]

tokens = {
    "%%IB_PLUS_NA%%": f"{ib_plus * 1e9:.2f}",
    "%%VOUT1_MV%%": f"{vout1 * 1e3:.3f}",
    "%%IB_MINUS_NA%%": f"{ib_minus * 1e9:.2f}",
    "%%VOUT2_MV%%": f"{vout2 * 1e3:.3f}",
    "%%IOS_NA%%": f"{ios * 1e9:.2f}",
    "%%VOS_UV%%": f"{vos * 1e6:.1f}",
    "%%AVD%%": f"{avd:.0f}",
    "%%AVD_DB%%": f"{avd_db:.1f}",
    "%%AVD_VMV%%": f"{avd / 1e3:.0f}",
    "%%ACM%%": f"{acm:.3f}",
    "%%CMRR_DB%%": f"{cmrr_db:.1f}",
    "%%SR%%": f"{sr:.3f}",
    "%%SR_AVG%%": f"{sr_avg:.3f}" if sr_avg is not None else "---",
    "%%NETLIST_ITEM1%%": (LAB / "item1_bias.cir").read_text().strip(),
    "%%NETLIST_ITEM2%%": (LAB / "item2_ios.cir").read_text().strip(),
    "%%NETLIST_ITEM3%%": (LAB / "item3_vos.cir").read_text().strip(),
    "%%NETLIST_ITEM4%%": (LAB / "item4_avd.cir").read_text().strip(),
    "%%NETLIST_ITEM5%%": (LAB / "item5_acm.cir").read_text().strip(),
    "%%NETLIST_ITEM6%%": (LAB / "item6_slew.cir").read_text().strip(),
    "%%VOS_COMP_INC%%": (LAB / "vos_comp.inc").read_text().strip(),
}

targets = [REPORT / "main.tex", *sorted((REPORT / "chapters").glob("*.tex"))]
for path in targets:
    text = path.read_text()
    replaced = text
    for token, value in tokens.items():
        replaced = replaced.replace(token, value)
    if replaced != text:
        path.write_text(replaced)
        print(f"preenchido: {path.relative_to(REPORT.parent.parent)}")

leftover = [
    f"{path.name}: {line.strip()}"
    for path in targets
    for line in path.read_text().splitlines()
    if "%%" in line
]
if leftover:
    print("ATENCAO - tokens nao preenchidos:")
    print("\n".join(leftover))
else:
    print("OK: nenhum token pendente")
