from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Bounds:
    x1: float
    y1: float
    x2: float
    y2: float

    def expand(self, amount: float) -> Bounds:
        return Bounds(self.x1 - amount, self.y1 - amount, self.x2 + amount, self.y2 + amount)

    def union(self, other: Bounds) -> Bounds:
        return Bounds(
            min(self.x1, other.x1),
            min(self.y1, other.y1),
            max(self.x2, other.x2),
            max(self.y2, other.y2),
        )

    def intersects(self, other: Bounds) -> bool:
        return self.x1 < other.x2 and self.x2 > other.x1 and self.y1 < other.y2 and self.y2 > other.y1


@dataclass(frozen=True)
class TextWindow:
    x: float
    y: float
    align: str = "left"


@dataclass(frozen=True)
class SymbolModel:
    name: str
    body: Bounds
    pins: tuple[tuple[float, float], ...]
    reference: TextWindow
    value: TextWindow | None
    text_padding: float = 4.0

    def component_bounds(
        self,
        x: float,
        y: float,
        rotation: str,
        reference: str,
        value: str | None,
        *,
        include_text: bool = True,
    ) -> Bounds:
        bounds = _transform_bounds(self.body, x, y, rotation)
        if include_text:
            bounds = bounds.union(_text_bounds(self.reference, reference, x, y, rotation, self.text_padding))
            if value and self.value:
                bounds = bounds.union(_text_bounds(self.value, value, x, y, rotation, self.text_padding))
        return bounds


@dataclass(frozen=True)
class SchematicComponent:
    symbol: str
    x: int
    y: int
    rotation: str
    reference: str
    value: str | None
    bounds: Bounds


@dataclass(frozen=True)
class ComponentCollision:
    first: SchematicComponent
    second: SchematicComponent


SYMBOL_MODELS: dict[str, SymbolModel] = {
    "res": SymbolModel(
        "res",
        Bounds(0, -18, 96, 18),
        ((0, 0), (96, 0)),
        TextWindow(48, -36, "center"),
        TextWindow(48, 24, "center"),
    ),
    "res_v": SymbolModel(
        "res_v",
        Bounds(-18, 0, 18, 96),
        ((0, 0), (0, 96)),
        TextWindow(28, 20, "left"),
        TextWindow(28, 58, "left"),
    ),
    "cap": SymbolModel(
        "cap",
        Bounds(-26, 0, 26, 96),
        ((0, 0), (0, 96)),
        TextWindow(34, 26, "left"),
        TextWindow(34, 62, "left"),
    ),
    "cap_h": SymbolModel(
        "cap_h",
        Bounds(0, -26, 96, 26),
        ((0, 0), (96, 0)),
        TextWindow(48, -42, "center"),
        TextWindow(48, 30, "center"),
    ),
    "ind": SymbolModel(
        "ind",
        Bounds(0, -26, 96, 26),
        ((0, 0), (96, 0)),
        TextWindow(48, -42, "center"),
        TextWindow(48, 32, "center"),
    ),
    "ind_v": SymbolModel(
        "ind_v",
        Bounds(-26, 0, 26, 96),
        ((0, 0), (0, 96)),
        TextWindow(34, 24, "left"),
        TextWindow(34, 62, "left"),
    ),
    "diode": SymbolModel(
        "diode",
        Bounds(0, -28, 96, 28),
        ((0, 0), (96, 0)),
        TextWindow(48, -46, "center"),
        TextWindow(48, 34, "center"),
    ),
    "diode_v": SymbolModel(
        "diode_v",
        Bounds(-28, 0, 28, 96),
        ((0, 0), (0, 96)),
        TextWindow(36, 24, "left"),
        TextWindow(36, 62, "left"),
    ),
    "voltage": SymbolModel(
        "voltage",
        Bounds(-28, 0, 28, 96),
        ((0, 0), (0, 96)),
        TextWindow(40, 18, "left"),
        TextWindow(0, 122, "center"),
    ),
    "current": SymbolModel(
        "current",
        Bounds(-28, 0, 28, 96),
        ((0, 0), (0, 96)),
        TextWindow(40, 18, "left"),
        TextWindow(0, 122, "center"),
    ),
    "opamp2": SymbolModel(
        "opamp2",
        Bounds(0, 0, 144, 128),
        ((0, 32), (0, 96), (48, 0), (48, 128), (144, 64)),
        TextWindow(72, 18, "center"),
        None,
    ),
}


def parse_schematic_components(asc_text: str) -> list[SchematicComponent]:
    components: list[SchematicComponent] = []
    current: dict[str, object] | None = None
    for line in asc_text.splitlines():
        parts = line.split(maxsplit=4)
        if line.startswith("SYMBOL "):
            if current:
                components.append(_component_from_record(current))
            current = {
                "symbol": parts[1],
                "x": int(parts[2]),
                "y": int(parts[3]),
                "rotation": parts[4] if len(parts) > 4 else "R0",
                "reference": "",
                "value": None,
            }
        elif current and line.startswith("SYMATTR InstName "):
            current["reference"] = line.removeprefix("SYMATTR InstName ").strip()
        elif current and line.startswith("SYMATTR Value "):
            current["value"] = line.removeprefix("SYMATTR Value ").strip()
    if current:
        components.append(_component_from_record(current))
    return components


def component_collisions(asc_text: str, *, clearance: float = 10.0) -> list[ComponentCollision]:
    components = parse_schematic_components(asc_text)
    collisions: list[ComponentCollision] = []
    for index, first in enumerate(components):
        first_bounds = first.bounds.expand(clearance)
        for second in components[index + 1 :]:
            if first_bounds.intersects(second.bounds.expand(clearance)):
                collisions.append(ComponentCollision(first, second))
    return collisions


def schematic_content_bounds(asc_text: str, *, include_directives: bool = True) -> Bounds:
    bounds: Bounds | None = None

    def include(item: Bounds) -> None:
        nonlocal bounds
        bounds = item if bounds is None else bounds.union(item)

    for component in parse_schematic_components(asc_text):
        include(component.bounds)
    for line in asc_text.splitlines():
        parts = line.split(maxsplit=5)
        if line.startswith("WIRE ") and len(parts) >= 5:
            x1, y1, x2, y2 = (int(value) for value in parts[1:5])
            include(Bounds(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
        elif line.startswith("FLAG ") and len(parts) >= 4:
            x, y = int(parts[1]), int(parts[2])
            label = parts[3]
            include(_text_box(x, y - 10, label, "left", 4.0))
        elif include_directives and line.startswith("TEXT ") and len(parts) >= 6:
            x, y = int(parts[1]), int(parts[2])
            include(_text_box(x, y - 12, parts[5].lstrip("!"), "left", 4.0))
    return bounds or Bounds(0, 0, 0, 0)


def load_schematic_components(path: str | Path) -> list[SchematicComponent]:
    return parse_schematic_components(Path(path).read_text())


def _component_from_record(record: dict[str, object]) -> SchematicComponent:
    symbol = str(record["symbol"])
    model = SYMBOL_MODELS.get(symbol, SYMBOL_MODELS["res"])
    x = int(record["x"])
    y = int(record["y"])
    rotation = str(record["rotation"])
    reference = str(record["reference"])
    value = record["value"] if record["value"] is None else str(record["value"])
    bounds = model.component_bounds(x, y, rotation, reference, value)
    return SchematicComponent(symbol, x, y, rotation, reference, value, bounds)


def _transform_bounds(bounds: Bounds, x: float, y: float, rotation: str) -> Bounds:
    points = [
        _transform_point(bounds.x1, bounds.y1, rotation),
        _transform_point(bounds.x1, bounds.y2, rotation),
        _transform_point(bounds.x2, bounds.y1, rotation),
        _transform_point(bounds.x2, bounds.y2, rotation),
    ]
    xs = [point[0] + x for point in points]
    ys = [point[1] + y for point in points]
    return Bounds(min(xs), min(ys), max(xs), max(ys))


def _text_bounds(window: TextWindow, text: str, x: float, y: float, rotation: str, padding: float) -> Bounds:
    wx, wy = _transform_point(window.x, window.y, rotation)
    return _text_box(x + wx, y + wy, text, window.align, padding)


def _text_box(x: float, y: float, text: str, align: str, padding: float) -> Bounds:
    width = max(18.0, len(text) * 7.0) + padding * 2.0
    height = 18.0 + padding * 2.0
    if align.lower() == "center":
        return Bounds(x - width / 2.0, y - height / 2.0, x + width / 2.0, y + height / 2.0)
    if align.lower() == "right":
        return Bounds(x - width, y - height / 2.0, x, y + height / 2.0)
    return Bounds(x, y - height / 2.0, x + width, y + height / 2.0)


def _transform_point(x: float, y: float, rotation: str) -> tuple[float, float]:
    if rotation == "R90":
        return -y, x
    if rotation == "R180":
        return -x, -y
    if rotation == "R270":
        return y, -x
    if rotation == "M0":
        return -x, y
    if rotation == "M90":
        return -y, -x
    if rotation == "M180":
        return x, -y
    if rotation == "M270":
        return y, x
    return x, y
