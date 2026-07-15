# rs2-somador-subtrator

Roteiro EB2 S2 (`roteiro-eb2-rs2.pdf`): somador/subtrator com LM741,
matrícula 21101175. Projeto e derivação completa em `DESIGN.md`; relatório
pareado em `reports/rs2-somador-subtrator/`.

Tudo é gerado por `rs2_somador_subtrator.py`:

```bash
./claw-spice code build experiments/rs2-somador-subtrator/rs2_somador_subtrator.py \
    --output-dir experiments/rs2-somador-subtrator
```

Artefatos: `rs2_bloco_{a,b,c}.{asc,cir}` (blocos isolados),
`rs2_completo.{asc,cir}` (sistema com 7 amp-ops + referência
comportamental ideal), `rs2_vin{1..6}.cir` (resposta individual por
entrada), `rs2_completo_vendor.cir` (cross-check com macromodelo TI).

Modelos: `lm741_level1.lib` (cópia de `models/lm741_level1.lib`, MIT) e
`lm741_vendor.lib` (cópia de `models/vendor/lm741.lib`, download TI —
gitignored; ver `models/manifest.toml`).

Simulações rodam uma por contêiner (`./claw-spice sim run --timeout 2400 ...`)
e podem ser lançadas em paralelo. Sob emulação amd64 cada LTspice demora
vários minutos — o `--timeout` alto é necessário.
