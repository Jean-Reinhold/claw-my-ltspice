"""RS2 (EB2 Aula S2) - somador e subtrator com LM741.

Matricula 21101175 -> A7..A0 = 2,1,1,0,1,1,7,5

Bloco A: vout1 = -9*vin1 + 0.2 - 3*vin2 + 2.5*vin3  (somente somadores; o termo
         constante A2/5 = 0.2 V vem de uma entrada de referencia ligada ao
         trilho de -15 V por 7.5 Meg no somador final)
Bloco B: vout2 =  2*vin4 + 4*vin5 - 9*vin6           (somadores inversores)
Bloco C: vout  = 12.5*(vout2 - vout1)                (amp. de instrumentacao, G=25)

Global: vout = 112.5*vin1 + 37.5*vin2 - 31.25*vin3 + 25*vin4 + 50*vin5
             - 112.5*vin6 - 2.5
"""

from __future__ import annotations

import shutil
from pathlib import Path

from claw_spice.ir import Circuit

SUBCKT_IDEAL = "LM741_LEVEL1"
INCLUDE_IDEAL = "lm741_level1.lib"
SUBCKT_VENDOR = "LM741"
INCLUDE_VENDOR = "lm741_vendor.lib"

ROW = 160  # vertical pitch between summer input rows (clears source value labels)

IDEAL_GLOBAL = (
    "112.5*V(in1)+37.5*V(in2)-31.25*V(in3)+25*V(in4)+50*V(in5)-112.5*V(in6)-2.5"
)
IDEAL_BLOCK_A = "-9*V(in1)-3*V(in2)+2.5*V(in3)+0.2"
IDEAL_BLOCK_B = "2*V(in4)+4*V(in5)-9*V(in6)"

GLOBAL_SRC = {
    "in1": "SINE(0 20m 500)",
    "in2": "SINE(0 20m 700)",
    "in3": "SINE(0 20m 900)",
    "in4": "SINE(0 20m 1100)",
    "in5": "SINE(0 20m 1300)",
    "in6": "SINE(0 20m 1500)",
}
BLOCK_A_SRC = {"in1": "SINE(0 0.1 300)", "in2": "SINE(0 0.2 700)", "in3": "SINE(0 0.4 1300)"}
BLOCK_B_SRC = {"in4": "SINE(0 0.2 300)", "in5": "SINE(0 0.2 700)", "in6": "SINE(0 0.1 1300)"}


def _draw_summer(circuit, bx, by, inputs, rf_value, rf_ref, op_ref, sum_node, out_node, subckt):
    """Somador inversor: entradas pela esquerda, realimentacao por cima.

    inputs: list of (node, resistor_value, resistor_ref). Returns (x, y) of the
    output pin junction.
    """
    n = len(inputs)
    y_inn = by + {1: 0, 2: 80, 3: ROW, 4: 240}[n]
    rail_x = bx + 112
    fy = min(y_inn - 176, by - 16)
    for i, (node, value, ref) in enumerate(inputs):
        yi = by + ROW * i
        circuit.resistor(ref, node, sum_node, value, at=(bx, yi))
        circuit.wire(bx + 96, yi, rail_x, yi)
    # sum rail doubles as the feedback riser
    circuit.wire(rail_x, fy, rail_x, by + ROW * (n - 1))
    circuit.wire(rail_x, y_inn, bx + 176, y_inn)
    opy = y_inn - 96
    circuit.opamp(op_ref, "0", sum_node, "vcc", "vee", out_node, at=(bx + 176, opy), subckt=subckt)
    circuit.flag(bx + 176, y_inn - 64, "0")
    circuit.opamp_supply_flags(bx + 176, opy)
    circuit.wire(rail_x, fy, bx + 224, fy)
    circuit.resistor(rf_ref, sum_node, out_node, rf_value, at=(bx + 224, fy))
    circuit.wire(bx + 320, fy, bx + 320, y_inn - 32)
    return bx + 320, y_inn - 32


def _draw_source(circuit, ref, node, value, ox, row_y, wire_to):
    circuit.voltage(ref, node, "0", value, at=(ox + 32, row_y))
    circuit.flag(ox + 32, row_y + 96, "0")
    circuit.wire(ox, row_y, wire_to, row_y)
    circuit.iopin(ox, row_y, node, "In")


def _draw_rails(circuit, x, y=96):
    circuit.voltage("VCC", "vcc", "0", "15", at=(x, y))
    circuit.flag(x, y, "vcc")
    circuit.flag(x, y + 96, "0")
    circuit.voltage("VEE", "vee", "0", "-15", at=(x, y + 192))
    circuit.flag(x, y + 192, "vee")
    circuit.flag(x, y + 288, "0")


def _draw_block_a(circuit, ox, oy, subckt, sources):
    """Bloco A. Retorna o ponto de saida (no vout1)."""
    _draw_summer(
        circuit,
        ox + 448,
        oy,
        [
            ("in1", "11.1111k", "RA1"),
            ("in2", "33.3333k", "RA2"),
            ("vee", "7.5Meg", "RAR"),
            ("va", "100k", "RA3"),
        ],
        "100k",
        "RAF2",
        "XA2",
        "suma2",
        "vout1",
        subckt,
    )
    _draw_summer(
        circuit,
        ox + 64,
        oy + 512,
        [("in3", "10k", "RA4")],
        "25k",
        "RAF1",
        "XA1",
        "suma1",
        "va",
        subckt,
    )
    # referencia DC: o trilho de -15 V entra na terceira linha do somador
    circuit.wire(ox + 384, oy + 320, ox + 448, oy + 320)
    circuit.flag(ox + 384, oy + 320, "vee")
    # va: saida de A1 segue reto para a quarta linha de A2
    circuit.wire(ox + 384, oy + 480, ox + 448, oy + 480)
    _draw_source(circuit, "VIN1", "in1", sources.get("in1", "0"), ox, oy, ox + 448)
    _draw_source(circuit, "VIN2", "in2", sources.get("in2", "0"), ox, oy + 160, ox + 448)
    _draw_source(circuit, "VIN3", "in3", sources.get("in3", "0"), ox, oy + 512, ox + 64)
    return ox + 768, oy + 128


def _draw_block_b(circuit, ox, oy, subckt, sources):
    """Bloco B. Retorna o ponto de saida (no vout2)."""
    _draw_summer(
        circuit,
        ox + 448,
        oy,
        [("in6", "10k", "RB3"), ("vb", "90k", "RB4")],
        "90k",
        "RBF2",
        "XB2",
        "sumb2",
        "vout2",
        subckt,
    )
    _draw_summer(
        circuit,
        ox + 64,
        oy + 512,
        [("in4", "20k", "RB1"), ("in5", "10k", "RB2")],
        "40k",
        "RBF1",
        "XB1",
        "sumb1",
        "vb",
        subckt,
    )
    # vb: saida de B1 sobe ate a linha de entrada 2 de B2
    circuit.wire(ox + 384, oy + 560, ox + 384, oy + 160)
    circuit.wire(ox + 384, oy + 160, ox + 448, oy + 160)
    _draw_source(circuit, "VIN6", "in6", sources.get("in6", "0"), ox, oy, ox + 448)
    _draw_source(circuit, "VIN4", "in4", sources.get("in4", "0"), ox, oy + 512, ox + 64)
    _draw_source(circuit, "VIN5", "in5", sources.get("in5", "0"), ox, oy + 672, ox + 64)
    return ox + 768, oy + 48


def _draw_block_c(circuit, ox, oy, subckt):
    """Bloco C: amplificador de instrumentacao de 3 amp-ops, ganho 12.5.

    Entradas pelos nos vout1 (caminho inversor) e vout2 (caminho nao
    inversor); as linhas de entrada comecam em (ox-160, oy+32) e
    (ox-160, oy+384). Retorna o ponto de saida (no out).
    """
    circuit.opamp("XC1", "vout1", "ng1", "vcc", "vee", "na", at=(ox, oy), subckt=subckt)
    circuit.opamp_supply_flags(ox, oy)
    circuit.opamp("XC2", "vout2", "ng2", "vcc", "vee", "nb", at=(ox, oy + 352), subckt=subckt)
    circuit.opamp_supply_flags(ox, oy + 352)
    circuit.opamp("XC3", "np", "nn", "vcc", "vee", "out", at=(ox + 448, oy + 192), subckt=subckt)
    circuit.opamp_supply_flags(ox + 448, oy + 192)

    # entradas dos buffers
    circuit.wire(ox - 160, oy + 32, ox, oy + 32)
    circuit.wire(ox - 160, oy + 384, ox, oy + 384)

    # coluna ng1: stub do inversor + realimentacao superior + topo de Rg
    circuit.wire(ox - 48, oy + 96, ox, oy + 96)
    circuit.wire(ox - 48, oy + 96, ox - 48, oy + 176)
    circuit.wire(ox - 48, oy + 160, ox - 32, oy + 160)
    circuit.resistor("RC1", "ng1", "na", "10k", at=(ox - 32, oy + 160))
    circuit.wire(ox + 64, oy + 160, ox + 144, oy + 160)
    circuit.wire(ox + 144, oy + 160, ox + 144, oy + 64)
    circuit.resistor("RCG", "ng1", "ng2", "5k", at=(ox - 48, oy + 176), symbol="res_v")

    # coluna ng2: base de Rg + stub do inversor + realimentacao inferior
    circuit.wire(ox - 48, oy + 272, ox - 48, oy + 512)
    circuit.wire(ox - 48, oy + 448, ox, oy + 448)
    circuit.wire(ox - 48, oy + 512, ox - 32, oy + 512)
    circuit.resistor("RC2", "ng2", "nb", "10k", at=(ox - 32, oy + 512))
    circuit.wire(ox + 64, oy + 512, ox + 144, oy + 512)
    circuit.wire(ox + 144, oy + 512, ox + 144, oy + 416)

    # linha na -> entrada inversora do estagio diferencial
    circuit.wire(ox + 144, oy + 64, ox + 208, oy + 64)
    circuit.resistor("RC3", "na", "nn", "10k", at=(ox + 208, oy + 64))
    circuit.wire(ox + 304, oy + 64, ox + 352, oy + 64)
    circuit.wire(ox + 352, oy + 64, ox + 352, oy + 288)
    circuit.wire(ox + 352, oy + 288, ox + 448, oy + 288)

    # linha nb -> entrada nao inversora (cruza a linha na sem juncao)
    circuit.wire(ox + 144, oy + 416, ox + 208, oy + 416)
    circuit.resistor("RC4", "nb", "np", "10k", at=(ox + 208, oy + 416))
    circuit.wire(ox + 304, oy + 416, ox + 400, oy + 416)
    circuit.wire(ox + 400, oy + 416, ox + 400, oy + 224)
    circuit.wire(ox + 400, oy + 224, ox + 448, oy + 224)

    # realimentacao do estagio diferencial (por cima do amp-op)
    circuit.wire(ox + 352, oy + 112, ox + 368, oy + 112)
    circuit.resistor("RC5", "nn", "out", "25k", at=(ox + 368, oy + 112))
    circuit.wire(ox + 464, oy + 112, ox + 592, oy + 112)
    circuit.wire(ox + 592, oy + 112, ox + 592, oy + 256)

    # divisor de referencia do estagio diferencial
    circuit.wire(ox + 400, oy + 416, ox + 400, oy + 432)
    circuit.resistor("RC6", "np", "0", "25k", at=(ox + 400, oy + 432), symbol="res_v")
    circuit.flag(ox + 400, oy + 528, "0")

    return ox + 592, oy + 256


def _finish_output(circuit, x, y, label):
    """Carga de 10k + iopin na saida."""
    circuit.wire(x, y, x + 112, y)
    circuit.resistor("RL", label, "0", "10k", at=(x + 64, y), symbol="res_v")
    circuit.flag(x + 64, y + 96, "0")
    circuit.iopin(x + 112, y, label, "Out")


def build_bloco_a(subckt=SUBCKT_IDEAL, include=INCLUDE_IDEAL):
    circuit = Circuit("RS2 bloco A: vout1 = -9*vin1 - 2.8*vin2 + 2.5*vin3 (21101175)")
    circuit.include(include)
    out_x, out_y = _draw_block_a(circuit, 64, 96, subckt, BLOCK_A_SRC)
    _finish_output(circuit, out_x, out_y, "vout1")
    _draw_rails(circuit, 1280)
    circuit.tran("0", "20m", "0", "10u")
    circuit.meas("TRAN", "vout1_max", "MAX V(vout1)")
    return circuit


def build_bloco_b(subckt=SUBCKT_IDEAL, include=INCLUDE_IDEAL):
    circuit = Circuit("RS2 bloco B: vout2 = 2*vin4 + 4*vin5 - 9*vin6 (21101175)")
    circuit.include(include)
    out_x, out_y = _draw_block_b(circuit, 64, 208, subckt, BLOCK_B_SRC)
    _finish_output(circuit, out_x, out_y, "vout2")
    _draw_rails(circuit, 1280)
    circuit.tran("0", "20m", "0", "10u")
    circuit.meas("TRAN", "vout2_max", "MAX V(vout2)")
    return circuit


def build_bloco_c(subckt=SUBCKT_IDEAL, include=INCLUDE_IDEAL):
    circuit = Circuit("RS2 bloco C: vout = 12.5*(vout2 - vout1), G=25 (21101175)")
    circuit.include(include)
    out_x, out_y = _draw_block_c(circuit, 384, 96, subckt)
    # fontes de teste: modo comum de 1 V + diferencial de 0.4 V de pico
    circuit.voltage("VN", "vout1", "0", "1", at=(96, 128))
    circuit.flag(96, 224, "0")
    circuit.wire(64, 128, 224, 128)
    circuit.iopin(64, 128, "vout1", "In")
    circuit.voltage("VP", "vout2", "0", "SINE(1 0.4 1k)", at=(96, 480))
    circuit.flag(96, 576, "0")
    circuit.wire(64, 480, 224, 480)
    circuit.iopin(64, 480, "vout2", "In")
    _finish_output(circuit, out_x, out_y, "out")
    _draw_rails(circuit, 1344)
    circuit.tran("0", "5m", "0", "5u")
    circuit.meas("TRAN", "gain_diff", "FIND V(out)/0.4 AT=2.25m")
    circuit.meas("TRAN", "vout_avg", "AVG V(out)")
    return circuit


def build_completo(sources=None, subckt=SUBCKT_IDEAL, include=INCLUDE_IDEAL):
    """Sistema completo A+B+C (7 amp-ops). Blocos ligados por rotulos de no."""
    sources = GLOBAL_SRC if sources is None else sources
    circuit = Circuit(f"RS2 completo (21101175, modelo {subckt})")
    circuit.include(include)
    ax, ay = _draw_block_a(circuit, 64, 96, subckt, sources)
    circuit.wire(ax, ay, ax + 64, ay)
    circuit.flag(ax + 64, ay, "vout1")
    bx, by = _draw_block_b(circuit, 64, 896, subckt, sources)
    circuit.wire(bx, by, bx + 64, by)
    circuit.flag(bx + 64, by, "vout2")
    cx, cy = _draw_block_c(circuit, 1280, 480, subckt)
    circuit.flag(1120, 512, "vout1")
    circuit.flag(1120, 864, "vout2")
    _finish_output(circuit, cx, cy, "out")
    _draw_rails(circuit, 2048)
    circuit.tran("0", "20m", "0", "10u")
    return circuit


def _per_input_netlist(n, subckt=SUBCKT_IDEAL, include=INCLUDE_IDEAL):
    """Somente vinN excitada (50 mV, 1 kHz); demais aterradas."""
    circuit = build_completo({f"in{n}": "SINE(0 50m 1k)"}, subckt, include)
    circuit.title = f"RS2 resposta individual vin{n} (21101175)"
    circuit.directives = [d for d in circuit.directives if not d.startswith(".tran")]
    circuit.tran("0", "5m", "0", "5u")
    # pico do seno em 2.25 ms e vale em 2.75 ms; a diferenca elimina o nivel
    # DC (-2.5 V na saida, vindo do termo constante do bloco A) e da o ganho
    # com sinal: g = (pico - vale) / (2 * 50 mV)
    circuit.meas("TRAN", "vout_pk", "FIND V(out) AT=2.25m")
    circuit.meas("TRAN", "vout_tr", "FIND V(out) AT=2.75m")
    circuit.meas("TRAN", f"g_out_vin{n}", "PARAM (vout_pk-vout_tr)/0.1")
    circuit.meas("TRAN", "v1_pk", "FIND V(vout1) AT=2.25m")
    circuit.meas("TRAN", "v1_tr", "FIND V(vout1) AT=2.75m")
    circuit.meas("TRAN", f"g_vout1_vin{n}", "PARAM (v1_pk-v1_tr)/0.1")
    circuit.meas("TRAN", "v2_pk", "FIND V(vout2) AT=2.25m")
    circuit.meas("TRAN", "v2_tr", "FIND V(vout2) AT=2.75m")
    circuit.meas("TRAN", f"g_vout2_vin{n}", "PARAM (v2_pk-v2_tr)/0.1")
    # media sobre ciclos inteiros: sobra so o nivel DC da saida
    circuit.meas("TRAN", "vout_dc", "AVG V(out)")
    return circuit


def _add_global_overlay(circuit):
    circuit.behavioral_voltage("BIDEAL", "ideal", "0", IDEAL_GLOBAL)
    circuit.meas("TRAN", "err_max", "MAX abs(V(out)-V(ideal))")
    circuit.meas("TRAN", "err_rms", "RMS (V(out)-V(ideal))")
    circuit.meas("TRAN", "vout_max", "MAX V(out)")
    circuit.meas("TRAN", "vout_min", "MIN V(out)")


def build(output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[2]
    shutil.copyfile(root / "models" / "lm741_level1.lib", output / "lm741_level1.lib")
    vendor = root / "models" / "vendor" / "lm741.lib"
    have_vendor = vendor.exists()
    if have_vendor:
        shutil.copyfile(vendor, output / "lm741_vendor.lib")

    results: dict[str, Path] = {}

    bloco_a = build_bloco_a()
    results["bloco_a_asc"] = bloco_a.write_asc(output / "rs2_bloco_a.asc")
    bloco_a.behavioral_voltage("BIDEAL1", "ideal1", "0", IDEAL_BLOCK_A)
    bloco_a.meas("TRAN", "err1_max", "MAX abs(V(vout1)-V(ideal1))")
    results["bloco_a_cir"] = bloco_a.write_netlist(output / "rs2_bloco_a.cir")

    bloco_b = build_bloco_b()
    results["bloco_b_asc"] = bloco_b.write_asc(output / "rs2_bloco_b.asc")
    bloco_b.behavioral_voltage("BIDEAL2", "ideal2", "0", IDEAL_BLOCK_B)
    bloco_b.meas("TRAN", "err2_max", "MAX abs(V(vout2)-V(ideal2))")
    results["bloco_b_cir"] = bloco_b.write_netlist(output / "rs2_bloco_b.cir")

    bloco_c = build_bloco_c()
    results["bloco_c_asc"] = bloco_c.write_asc(output / "rs2_bloco_c.asc")
    results["bloco_c_cir"] = bloco_c.write_netlist(output / "rs2_bloco_c.cir")

    completo = build_completo()
    results["completo_asc"] = completo.write_asc(output / "rs2_completo.asc")
    _add_global_overlay(completo)
    results["completo_cir"] = completo.write_netlist(output / "rs2_completo.cir")

    for n in range(1, 7):
        circuit = _per_input_netlist(n)
        results[f"vin{n}_cir"] = circuit.write_netlist(output / f"rs2_vin{n}.cir")

    if have_vendor:
        vendor_circuit = build_completo(subckt=SUBCKT_VENDOR, include=INCLUDE_VENDOR)
        vendor_circuit.title = "RS2 completo, macromodelo vendor LM741 (21101175)"
        # o macromodelo de Boyle oscila com o integrador trapezoidal nos
        # diodos do estagio de saida; Gear amortece e 10 ms cobre um periodo
        # completo do multi-tom (fundamental de 100 Hz)
        vendor_circuit.directives = [
            d for d in vendor_circuit.directives if not d.startswith(".tran")
        ]
        vendor_circuit.directive(".options method=Gear")
        # cshunt amortece as descontinuidades do modelo de Boyle; tolerancias
        # absolutas relaxadas evitam o colapso do passo de tempo
        vendor_circuit.directive(".options cshunt=10p abstol=1e-9 vntol=10u")
        vendor_circuit.tran("0", "10m", "0", "10u")
        _add_global_overlay(vendor_circuit)
        results["completo_vendor_cir"] = vendor_circuit.write_netlist(
            output / "rs2_completo_vendor.cir"
        )

    # Teste com AmpOp moderno: ADA4610 (JFET, 36 V, modelo embarcado no
    # LTspice), mesmo circuito completo e mesmas medidas do teste vendor.
    moderno_circuit = build_completo(subckt="ADA4610", include=None)
    moderno_circuit.includes = []
    moderno_circuit.title = "RS2 completo, AmpOp moderno ADA4610 (21101175)"
    moderno_circuit.directive(".lib ADA4610.lib")
    _add_global_overlay(moderno_circuit)
    results["completo_moderno_cir"] = moderno_circuit.write_netlist(
        output / "rs2_completo_moderno.cir"
    )

    return results


if __name__ == "__main__":
    print(build(Path(__file__).parent))
