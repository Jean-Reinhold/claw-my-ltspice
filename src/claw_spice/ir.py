from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from claw_spice.schematic_model import schematic_content_bounds


@dataclass
class Layout:
    x: int | None = None
    y: int | None = None
    rotation: str = "R0"


@dataclass
class Wire:
    x1: int
    y1: int
    x2: int
    y2: int


@dataclass
class Flag:
    x: int
    y: int
    label: str
    direction: str | None = None


@dataclass
class SchematicText:
    x: int
    y: int
    text: str
    size: int = 2


@dataclass
class Component:
    ref: str
    kind: str
    nodes: tuple[str, ...]
    value: str
    model: str | None = None
    symbol: str | None = None
    params: dict[str, str] = field(default_factory=dict)
    layout: Layout = field(default_factory=Layout)

    def netlist_line(self) -> str:
        node_text = " ".join(self.nodes)
        if self.model:
            base = f"{self.ref} {node_text} {self.model}"
            if self.value:
                base = f"{base} {self.value}"
        else:
            base = f"{self.ref} {node_text} {self.value}"
        if self.params:
            param_text = " ".join(f"{key}={value}" for key, value in self.params.items())
            return f"{base} {param_text}"
        return base


class Circuit:
    def __init__(self, title: str) -> None:
        self.title = title
        self.components: list[Component] = []
        self.wires: list[Wire] = []
        self.flags: list[Flag] = []
        self.texts: list[SchematicText] = []
        self.directives: list[str] = []
        self.includes: list[str] = []

    def add(
        self,
        ref: str,
        kind: str,
        nodes: tuple[str, ...],
        value: str,
        *,
        model: str | None = None,
        symbol: str | None = None,
        params: dict[str, str] | None = None,
        at: tuple[int, int] | None = None,
        rotation: str = "R0",
    ) -> Component:
        component = Component(
            ref=ref,
            kind=kind,
            nodes=nodes,
            value=value,
            model=model,
            symbol=symbol,
            params=params or {},
            layout=Layout(*(at or (None, None)), rotation=rotation),
        )
        self.components.append(component)
        return component

    def resistor(self, ref: str, node_a: str, node_b: str, value: str, **layout: object) -> Component:
        return self.add(ref, "res", (node_a, node_b), value, **layout)

    def capacitor(self, ref: str, node_a: str, node_b: str, value: str, **layout: object) -> Component:
        return self.add(ref, "cap", (node_a, node_b), value, **layout)

    def inductor(self, ref: str, node_a: str, node_b: str, value: str, **layout: object) -> Component:
        return self.add(ref, "ind", (node_a, node_b), value, **layout)

    def voltage(self, ref: str, node_p: str, node_n: str, value: str, **layout: object) -> Component:
        return self.add(ref, "voltage", (node_p, node_n), value, **layout)

    def behavioral_voltage(
        self,
        ref: str,
        node_p: str,
        node_n: str,
        expression: str,
        **layout: object,
    ) -> Component:
        value = expression if expression.strip().upper().startswith("V=") else f"V={expression}"
        return self.add(ref, "bv", (node_p, node_n), value, **layout)

    def current(self, ref: str, node_p: str, node_n: str, value: str, **layout: object) -> Component:
        return self.add(ref, "current", (node_p, node_n), value, **layout)

    def diode(self, ref: str, anode: str, cathode: str, model: str, **layout: object) -> Component:
        return self.add(ref, "diode", (anode, cathode), "", model=model, **layout)

    def bjt(
        self,
        ref: str,
        collector: str,
        base: str,
        emitter: str,
        model: str,
        **layout: object,
    ) -> Component:
        kind = "npn" if ref.upper().startswith("Q") else "bjt"
        return self.add(ref, kind, (collector, base, emitter), "", model=model, **layout)

    def mosfet(
        self,
        ref: str,
        drain: str,
        gate: str,
        source: str,
        bulk: str,
        model: str,
        **layout: object,
    ) -> Component:
        return self.add(ref, "nmos", (drain, gate, source, bulk), "", model=model, **layout)

    def subcircuit(
        self,
        ref: str,
        kind: str,
        nodes: tuple[str, ...],
        name: str,
        **layout: object,
    ) -> Component:
        return self.add(ref, kind, nodes, name, **layout)

    def opamp(
        self,
        ref: str,
        non_inverting: str,
        inverting: str,
        vcc: str,
        vee: str,
        output: str,
        subckt: str = "CLAW_IDEAL_OPAMP",
        **layout: object,
    ) -> Component:
        return self.subcircuit(
            ref,
            "opamp",
            (non_inverting, inverting, vcc, vee, output),
            subckt,
            **layout,
        )

    def include(self, path: str) -> None:
        self.includes.append(path)

    def wire(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.wires.append(Wire(x1, y1, x2, y2))

    def flag(self, x: int, y: int, label: str) -> None:
        self.flags.append(Flag(x, y, label))

    def opamp_supply_flags(
        self,
        x: int,
        y: int,
        *,
        vcc: str = "vcc",
        vee: str = "vee",
        stub: int = 48,
    ) -> None:
        """Place op-amp supply flags on short stubs clear of the symbol body."""
        pin_x = x + 48
        vcc_y = y - stub
        vee_y = y + 128 + stub
        self.wire(pin_x, y, pin_x, vcc_y)
        self.flag(pin_x, vcc_y, vcc)
        self.wire(pin_x, y + 128, pin_x, vee_y)
        self.flag(pin_x, vee_y, vee)

    def iopin(self, x: int, y: int, label: str, direction: str) -> None:
        self.flags.append(Flag(x, y, label, direction))

    def text(self, x: int, y: int, text: str, *, size: int = 2) -> None:
        self.texts.append(SchematicText(x, y, text, size))

    def directive(self, text: str) -> None:
        self.directives.append(text if text.startswith(".") else f".{text}")

    def tran(self, *args: str, startup: bool = False, uic: bool = False, maxstep: str | None = None) -> None:
        values = list(args)
        if maxstep and len(values) < 4:
            while len(values) < 3:
                values.append("0")
            values.append(maxstep)
        extras = []
        if startup:
            extras.append("startup")
        if uic:
            extras.append("UIC")
        self.directive(" ".join([".tran", *values, *extras]))

    def meas(self, analysis: str, name: str, expression: str) -> None:
        self.directive(f".meas {analysis} {name} {expression}")

    def to_netlist(self) -> str:
        lines = [f"* {self.title}"]
        lines.extend(f".include {item}" for item in self.includes)
        lines.extend(component.netlist_line() for component in self.components)
        lines.extend(self.directives)
        lines.append(".end")
        return "\n".join(lines) + "\n"

    def write_netlist(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.to_netlist())
        return output

    def to_asc(self) -> str:
        return AscExporter(self).render()

    def write_asc(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.to_asc())
        return output


class AscExporter:
    SYMBOLS = {
        "res": "res",
        "cap": "cap",
        "ind": "ind",
        "voltage": "voltage",
        "bv": "bv",
        "current": "current",
        "diode": "diode",
        "npn": "npn",
        "bjt": "npn",
        "nmos": "nmos",
        "opamp": "opamp2",
    }

    def __init__(self, circuit: Circuit) -> None:
        self.circuit = circuit

    def render(self) -> str:
        lines = ["Version 4", self._sheet_line()]
        for wire in self.circuit.wires:
            lines.append(f"WIRE {wire.x1} {wire.y1} {wire.x2} {wire.y2}")

        explicit_flags = bool(self.circuit.flags)
        y = 96
        for index, component in enumerate(self.circuit.components):
            x = component.layout.x if component.layout.x is not None else 128 + index * 176
            cy = component.layout.y if component.layout.y is not None else y
            symbol = component.symbol or self.SYMBOLS.get(component.kind, "res")
            rotation = component.layout.rotation
            lines.append(f"SYMBOL {symbol} {x} {cy} {rotation}")
            lines.append(f"SYMATTR InstName {component.ref}")
            value = component.model or component.value
            if value:
                lines.append(f"SYMATTR Value {value}")
            if component.model and component.value:
                lines.append(f"SYMATTR SpiceLine {component.value}")
            if not explicit_flags:
                self._append_node_labels(lines, component, x, cy, symbol)

        for flag in self.circuit.flags:
            lines.append(f"FLAG {flag.x} {flag.y} {flag.label}")
            if flag.direction:
                lines.append(f"IOPIN {flag.x} {flag.y} {flag.direction}")

        for text in self.circuit.texts:
            lines.append(f"TEXT {text.x} {text.y} Left {text.size} {text.text}")

        text_y = self._directive_y()
        for directive in [*self.circuit.includes_as_directives(), *self.circuit.directives]:
            lines.append(f"TEXT 64 {text_y} Left 1 !{directive}")
            text_y += 32
        return "\n".join(lines) + "\n"

    def _sheet_line(self) -> str:
        body = self._body_without_sheet_or_directives()
        bounds = schematic_content_bounds(body, include_directives=False)
        width = max(1200, int(bounds.x2 + 192))
        height = max(800, int(bounds.y2 + 256 + len(self.circuit.directives) * 32))
        return f"SHEET 1 {width} {height}"

    def _body_without_sheet_or_directives(self) -> str:
        lines: list[str] = []
        for wire in self.circuit.wires:
            lines.append(f"WIRE {wire.x1} {wire.y1} {wire.x2} {wire.y2}")
        for index, component in enumerate(self.circuit.components):
            x = component.layout.x if component.layout.x is not None else 128 + index * 176
            cy = component.layout.y if component.layout.y is not None else 96
            symbol = component.symbol or self.SYMBOLS.get(component.kind, "res")
            lines.append(f"SYMBOL {symbol} {x} {cy} {component.layout.rotation}")
            lines.append(f"SYMATTR InstName {component.ref}")
            value = component.model or component.value
            if value:
                lines.append(f"SYMATTR Value {value}")
        for flag in self.circuit.flags:
            lines.append(f"FLAG {flag.x} {flag.y} {flag.label}")
        for text in self.circuit.texts:
            lines.append(f"TEXT {text.x} {text.y} Left {text.size} {text.text}")
        return "\n".join(lines)

    def _directive_y(self) -> int:
        ys: list[int] = []
        ys.extend(y for wire in self.circuit.wires for y in (wire.y1, wire.y2))
        ys.extend(flag.y for flag in self.circuit.flags)
        ys.extend(text.y for text in self.circuit.texts)
        ys.extend(component.layout.y for component in self.circuit.components if component.layout.y is not None)
        return max(ys, default=224) + 112

    def _append_node_labels(self, lines: list[str], component: Component, x: int, y: int, symbol: str) -> None:
        # These pin label coordinates are intentionally conservative and used for
        # generated schematic readability. LTspice-compatible routing can be
        # refined through layout hints as the generator matures.
        offsets = _node_offsets(component.kind, len(component.nodes), component.layout.rotation, symbol)
        for node, (dx, dy) in zip(component.nodes, offsets, strict=False):
            label = "0" if node in {"0", "GND", "gnd"} else node
            lines.append(f"FLAG {x + dx} {y + dy} {label}")


def _node_offsets(kind: str, count: int, rotation: str = "R0", symbol: str | None = None) -> list[tuple[int, int]]:
    if symbol in {"res_v", "ind_v"}:
        return [(0, 0), (0, 96)]
    if symbol == "diode_v":
        return [(0, 0), (0, 96)]
    if symbol == "cap_h":
        return [(0, 0), (96, 0)]
    vertical = rotation in {"R90", "M90", "R270", "M270"}
    if kind in {"res", "ind"}:
        return [(0, 0), (0, 96)] if vertical else [(0, 0), (96, 0)]
    if kind == "cap":
        return [(0, 0), (96, 0)] if vertical else [(0, 0), (0, 96)]
    if kind in {"voltage", "current"}:
        return [(0, 0), (0, 96)]
    if kind == "diode":
        return [(0, 0), (96, 0)]
    if kind in {"npn", "bjt"}:
        return [(48, 0), (0, 32), (48, 96)]
    if kind == "nmos":
        return [(48, 0), (0, 80), (48, 96), (80, 96)]
    if kind == "opamp":
        return [(0, 32), (0, 96), (48, 0), (48, 128), (144, 64)]
    return [(index * 48, 0) for index in range(count)]


def _includes_as_directives(self: Circuit) -> list[str]:
    return [f".include {item}" for item in self.includes]


Circuit.includes_as_directives = _includes_as_directives  # type: ignore[attr-defined]
