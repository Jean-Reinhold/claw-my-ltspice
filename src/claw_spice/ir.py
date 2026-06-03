from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Layout:
    x: int | None = None
    y: int | None = None
    rotation: str = "R0"


@dataclass
class Component:
    ref: str
    kind: str
    nodes: tuple[str, ...]
    value: str
    model: str | None = None
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

    def include(self, path: str) -> None:
        self.includes.append(path)

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
        "current": "current",
        "diode": "diode",
        "npn": "npn",
        "bjt": "npn",
        "nmos": "nmos",
    }

    def __init__(self, circuit: Circuit) -> None:
        self.circuit = circuit

    def render(self) -> str:
        lines = ["Version 4", "SHEET 1 1200 800"]
        y = 96
        for index, component in enumerate(self.circuit.components):
            x = component.layout.x if component.layout.x is not None else 128 + index * 176
            cy = component.layout.y if component.layout.y is not None else y
            symbol = self.SYMBOLS.get(component.kind, "res")
            rotation = component.layout.rotation
            if component.kind in {"res", "ind"} and component.layout.rotation == "R0":
                rotation = "R90"
            lines.append(f"SYMBOL {symbol} {x} {cy} {rotation}")
            lines.append(f"SYMATTR InstName {component.ref}")
            value = component.model or component.value
            if value:
                lines.append(f"SYMATTR Value {value}")
            if component.model and component.value:
                lines.append(f"SYMATTR SpiceLine {component.value}")
            self._append_node_labels(lines, component, x, cy)

        text_y = 320
        for directive in [*self.circuit.includes_as_directives(), *self.circuit.directives]:
            lines.append(f"TEXT 64 {text_y} Left 2 !{directive}")
            text_y += 32
        return "\n".join(lines) + "\n"

    def _append_node_labels(self, lines: list[str], component: Component, x: int, y: int) -> None:
        # These pin label coordinates are intentionally conservative and used for
        # generated schematic readability. LTspice-compatible routing can be
        # refined through layout hints as the generator matures.
        offsets = _node_offsets(component.kind, len(component.nodes))
        for node, (dx, dy) in zip(component.nodes, offsets, strict=False):
            label = "0" if node in {"0", "GND", "gnd"} else node
            lines.append(f"FLAG {x + dx} {y + dy} {label}")


def _node_offsets(kind: str, count: int) -> list[tuple[int, int]]:
    if kind in {"res", "ind"}:
        return [(0, 0), (64, 0)]
    if kind == "cap":
        return [(16, 0), (16, 64)]
    if kind in {"voltage", "current"}:
        return [(0, 16), (0, 96)]
    if kind == "diode":
        return [(0, 0), (64, 0)]
    if kind in {"npn", "bjt"}:
        return [(48, 0), (0, 32), (48, 96)]
    if kind == "nmos":
        return [(48, 0), (0, 80), (48, 96), (80, 96)]
    return [(index * 48, 0) for index in range(count)]


def _includes_as_directives(self: Circuit) -> list[str]:
    return [f".include {item}" for item in self.includes]


Circuit.includes_as_directives = _includes_as_directives  # type: ignore[attr-defined]
