"""Regression tests for review round 4: a through-hole whose rim is closer to the edge than the FeatureScript's
probe step must still be found and flagged.

The reference checker is the oracle; the FeatureScript (not compilable here) is pinned to the fixed logic.
"""
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "checker")]

import hole_edge  # noqa: E402

FS = (ROOT / "featurescript" / "HoleEdgeCheck.fs").read_text()


def plate_with_hole_almost_on_edge():
    # 60 x 40 x 2 plate (x 0..60). 5 mm hole centred at x=57.48: rim 0.02 mm from the right edge.
    return Pos(30, 20, 1) * Box(60, 40, 2) - Pos(57.48, 20, 1) * Cylinder(2.5, 4)


def test_checker_flags_hole_0_02_mm_from_edge():
    res = hole_edge.check(plate_with_hole_almost_on_edge(), thickness=2.0, factor=2.0)
    assert len(res) == 1
    assert abs(res[0].edge_distance - 0.02) < 1e-3


def test_featurescript_probes_inward_not_outward():
    # outward probe (p - centre) misses holes closer to the edge than eps = 0.01 r; inward probe cannot
    assert "circle.coordSystem.origin - p) * eps" in FS
    assert "normalize(p - circle.coordSystem.origin)" not in FS
    # a hole's inward probe is void (far from the face); the outer rim's lies on the face
    assert "distance < 0.5 * eps" in FS
