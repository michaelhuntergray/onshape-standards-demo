"""Regression tests for review round 3: slots are not part edges, counterbores are not through-holes.

The reference checker is the oracle; the FeatureScript (not compilable here) must match it, so the last two tests
pin the FeatureScript's structure to the fixed logic.
"""
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, SlotOverall, extrude, Plane

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "checker")]

import hole_edge  # noqa: E402

FS = (ROOT / "featurescript" / "HoleEdgeCheck.fs").read_text()


def plate_with_slot_and_hole():
    # 100 x 60 x 2 plate (x 0..100, y 0..60). Slot centred at x=50; through-hole 3 mm from the slot's end,
    # 10+ mm from every outside edge.
    part = Pos(50, 30, 1) * Box(100, 60, 2)
    slot = Pos(50, 30, 1) * extrude(SlotOverall(20, 6), 4, dir=(0, 0, 1)).moved(Pos(0, 0, -2))
    part -= slot
    return part - Pos(50 + 10 + 3 + 2, 30, 1) * Cylinder(2, 4)  # rim 3 mm from the slot end (x=60)


def plate_with_counterbore_near_edge():
    # 60 x 40 x 2 plate. 5 mm dia counterbore 1 mm deep, rim 1.5 mm from the right edge, with a 2 mm dia
    # through-hole in its floor. A bigger pocket on the other face makes the pocketed face the larger one.
    part = Pos(30, 20, 1) * Box(60, 40, 2)
    part -= Pos(60 - 1.5 - 2.5, 20, 0.5) * Cylinder(2.5, 1)
    part -= Pos(60 - 1.5 - 2.5, 20, 1) * Cylinder(1, 4)
    return part - Pos(20, 20, 1.5) * Cylinder(6, 1)


def test_slot_is_not_a_part_edge():
    res = hole_edge.check(plate_with_slot_and_hole(), thickness=2.0, factor=2.0)
    assert len(res) == 1
    assert res[0].edge_distance > 8.0  # far from the outside edge; the 3 mm slot gap must not count
    assert res[0].ok


def test_counterbore_rim_is_not_a_through_hole():
    res = hole_edge.check(plate_with_counterbore_near_edge(), thickness=2.0, factor=2.0)
    assert res == []  # the 5 mm counterbore only reaches half way, so it is not a through-hole (and would FAIL at 1.5 mm)


def test_featurescript_outer_boundary_is_the_largest_loop():
    assert "evBox3d" in FS and "outerLoop" in FS


def test_featurescript_through_test_compares_wall_depth_to_part_depth():
    assert "partDepth" in FS and "wallDepth" in FS
    assert "== 1" not in FS  # the lone-disc floor heuristic is gone
