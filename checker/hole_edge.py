"""Hole-to-edge DFM check on a flat part (STEP in, one line per hole out).

Reference implementation of the rule in rules/hole-edge.json, the same check featurescript/HoleEdgeCheck.fs
runs inside Onshape. The plate face is the largest planar face; its inner wires that are circles are the holes.
For each hole, the distance from the hole's rim to the outer wire is compared with factor x thickness.

    uv run python checker/hole_edge.py examples/plate.step --thickness 2
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from build123d import GeomType, Shape, import_step

RULE = Path(__file__).resolve().parent.parent / "rules" / "hole-edge.json"


@dataclass
class HoleResult:
    center: tuple[float, float, float]
    diameter: float
    edge_distance: float
    required: float

    @property
    def ok(self) -> bool:
        return self.edge_distance + 1e-6 >= self.required


def plate_face(part: Shape):
    planar = [f for f in part.faces() if f.geom_type == GeomType.PLANE]
    if not planar:
        raise ValueError("no planar face found: this check is for flat parts")
    return max(planar, key=lambda f: f.area)


def _span(shape: Shape, n) -> float:
    """Extent of a shape's vertices along direction n."""
    ds = [v.X * n.X + v.Y * n.Y + v.Z * n.Z for v in shape.vertices()]
    return max(ds) - min(ds)


def _is_through(part: Shape, edge, n, tol: float = 1e-4) -> bool:
    """True when the hole wall (cylinder face containing this rim) runs the full depth of the part."""
    r, c = edge.radius, edge.arc_center
    for f in part.faces():
        if f.geom_type != GeomType.CYLINDER:
            continue
        for e in f.edges():
            if e.geom_type == GeomType.CIRCLE and abs(e.radius - r) < tol and (e.arc_center - c).length < tol:
                return _span(f, n) >= _span(part, n) - tol
    return False


def check(part: Shape, thickness: float, factor: float) -> list[HoleResult]:
    face = plate_face(part)
    n = face.normal_at()
    outer = face.outer_wire()
    required = factor * thickness
    results = []
    for wire in face.inner_wires():
        edges = wire.edges()
        if not edges or any(e.geom_type != GeomType.CIRCLE for e in edges):
            continue  # a slot or cut-out, not a round hole
        if not _is_through(part, edges[0], n):
            continue  # blind pocket: out of scope, the rule is for through-holes
        r = edges[0].radius
        c = edges[0].arc_center
        results.append(HoleResult((c.X, c.Y, c.Z), 2 * r, wire.distance_to(outer), required))
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step", type=Path)
    ap.add_argument("--thickness", type=float, required=True, help="material thickness, mm")
    ap.add_argument("--factor", type=float, help="override the rule's factor (default from rules/hole-edge.json)")
    a = ap.parse_args(argv)
    rule = json.loads(RULE.read_text())
    factor = a.factor if a.factor is not None else rule["limit"]["factor"]
    results = check(import_step(a.step), a.thickness, factor)
    print(f"rule: {rule['title']}: rim-to-edge >= {factor:g} x {a.thickness:g} mm = {factor * a.thickness:g} mm")
    for i, h in enumerate(results, 1):
        x, y, _ = h.center
        print(f"hole {i}: dia {h.diameter:.2f} at ({x:.1f}, {y:.1f}) rim-to-edge {h.edge_distance:.2f} mm "
              f"{'PASS' if h.ok else 'FAIL'}")
    bad = sum(not h.ok for h in results)
    print(f"{len(results)} holes, {bad} fail")
    if not results:
        print("error: no through-holes found, nothing was checked", file=sys.stderr)
        return 2
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
