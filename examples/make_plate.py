"""Builds examples/plate.step: a 60 x 40 x 2 mm plate with three holes, chosen to straddle the 2T = 4 mm rule.

    hole 1: dia 5 at (10, 20)  rim 7.5 mm from the left edge  -> pass
    hole 2: dia 5 at (56, 20)  rim 1.5 mm from the right edge -> fail
    hole 3: dia 4 at (30, 34)  rim 4.0 mm from the top edge   -> pass (exactly at the limit)
"""
from pathlib import Path

from build123d import Box, Cylinder, Pos, export_step

HOLES = [((10, 20), 5.0), ((56, 20), 5.0), ((30, 34), 4.0)]


def build():
    part = Pos(30, 20, 1) * Box(60, 40, 2)
    for (x, y), d in HOLES:
        part -= Pos(x, y, 1) * Cylinder(d / 2, 4)
    return part


if __name__ == "__main__":
    out = Path(__file__).with_name("plate.step")
    export_step(build(), str(out))
    print(out)
