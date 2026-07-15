# RS2 — Somador e Subtrator (EB2, Aula S2)

Roteiro: `roteiro-eb2-rs2.pdf`. Matrícula **21101175** →
A7=2, A6=1, A5=1, A4=0, A3=1, A2=1, A1=7, A0=5.

## Funções-alvo

| Bloco | Função com dígitos substituídos |
|-------|----------------------------------|
| A | vout1 = (5−2·7)vin1 + (1/5−3)vin2 + ((6−1)/2)vin3 = **−9·vin1 − 2.8·vin2 + 2.5·vin3** |
| B | vout2 = (0+2)vin4 + 1·[4vin5 − (10−1)vin6] = **2·vin4 + 4·vin5 − 9·vin6** |
| C | G = 10·2+5 = 25 → vout = **12.5·(vout2 − vout1)** |

Função global resultante:

vout = 112.5·vin1 + 35·vin2 − 31.25·vin3 + 25·vin4 + 50·vin5 − 112.5·vin6

## Bloco A — somente somadores/subtratores (2 × LM741)

Cascata de dois somadores inversores; vin3 sofre duas inversões (sinal +),
vin1/vin2 apenas uma (sinal −):

- **A1** (inversor, ganho −2.5): vA = −2.5·vin3 — R=10k, Rf=25k
- **A2** (somador inversor de 3 entradas, Rf=100k):
  vout1 = −(9·vin1 + 2.8·vin2 + 1·vA)
  - R(vin1) = 100k/9 = 11.1111k
  - R(vin2) = 100k/2.8 = 35.7143k
  - R(vA) = 100k

## Bloco B — topologia livre (2 × LM741)

Mesma estratégia (vin4/vin5 duas inversões → +, vin6 uma inversão → −):

- **B1** (somador inversor, Rf=40k): vB = −(2·vin4 + 4·vin5) — R(vin4)=20k, R(vin5)=10k
- **B2** (somador inversor, Rf=90k): vout2 = −(1·vB + 9·vin6) — R(vB)=90k, R(vin6)=10k

## Bloco C — amplificador de instrumentação (3 × LM741)

Ganho 12.5 dividido em 5 (entrada) × 2.5 (diferencial):

- Estágio de entrada: buffers com ganho diferencial 1 + 2R/Rg = 5 → R=10k, Rg=5k
- Estágio diferencial: R3/R2 = 25k/10k = 2.5
- Entrada não-inversora ← vout2; entrada inversora ← vout1

## Validação (Parte II)

- 6 simulações individuais: seno 1 kHz, 50 mV em UMA entrada, demais aterradas.
  Ganho com sinal medido por `.meas FIND V(out) AT=2.25m` (pico do seno) / 50 mV.
- 1 simulação global: 6 senos de 20 mV em frequências distintas
  (500/700/900/1100/1300/1500 Hz), sobreposição com fonte comportamental
  que calcula a função ideal; erro medido com `.meas MAX(abs(...))`.
- Sanidade por bloco: rs2_bloco_{a,b,c}.cir isolados.
- Cross-check de realismo com macromodelo vendor do LM741 (não versionado).

Amplitudes escolhidas para pior caso |vout| ≤ 0.02·366.25 ≈ 7.3 V < 14 V
(sem saturação nos trilhos ±15 V).

## Modelo do amplificador operacional

Roteiro pede "LM741 Level 1: ideal model" (Micro-Cap). Equivalente LTspice
implementado em `models/lm741_level1.lib`: ganho DC 200k (datasheet: 200 V/mV),
Rin 2 MΩ, Rout 75 Ω, saída limitada aos trilhos — sem polos (nível 1 = ideal).
Alimentação simétrica ±15 V adicionada explicitamente (LTspice não a inclui
automaticamente como o Micro-Cap).
