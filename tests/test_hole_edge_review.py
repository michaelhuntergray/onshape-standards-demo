"""Regression tests for the review findings: round plates, blind pockets, and the empty-result gate."""
import sys
from pathlib import Path

import pytest
from build123d import Box, Cylinder, Pos, export_step

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "checker")]

import hole_edge  # noqa: E402


def round_plate_with_center_hole():
    return Cylinder(30, 2) - Cylinder(3, 4)


def plate_with_blind_pocket():
    # 60 x 40 x 2 plate. Small 1 mm deep pocket 1.5 mm from the right edge in the bottom face; a larger pocket in
    # the top face (elsewhere) makes the bottom the larger face, so the checker picks the bottom.
    part = Pos(30, 20, 1) * Box(60, 40, 2)
    part -= Pos(56, 20, 0.5) * Cylinder(2.5, 1)
    return part - Pos(20, 20, 1.5) * Cylinder(6, 1)


def test_round_plate_rim_is_not_a_hole():
    res = hole_edge.check(round_plate_with_center_hole(), thickness=2.0, factor=2.0)
    assert len(res) == 1
    assert round(res[0].diameter, 3) == 6.0
    assert round(res[0].edge_distance, 3) == 27.0
    assert res[0].ok


def test_blind_pocket_is_ignored():
    assert hole_edge.check(plate_with_blind_pocket(), thickness=2.0, factor=2.0) == []


def test_blind_pocket_does_not_hide_a_real_hole():
    part = plate_with_blind_pocket() - Pos(10, 20, 1) * Cylinder(2.5, 4)
    res = hole_edge.check(part, thickness=2.0, factor=2.0)
    assert [round(h.center[0]) for h in res] == [10]


def test_cli_fails_when_nothing_was_checked(tmp_path, capsys):
    step = tmp_path / "solid.step"
    export_step(Pos(30, 20, 1) * Box(60, 40, 2), str(step))
    assert hole_edge.main([str(step), "--thickness", "2"]) == 2
    assert "no through-holes" in capsys.readouterr().err


def test_cli_fails_on_blind_pocket_only_part(tmp_path):
    step = tmp_path / "pocket.step"
    export_step(plate_with_blind_pocket(), str(step))
    assert hole_edge.main([str(step), "--thickness", "2"]) == 2


@pytest.mark.parametrize("flag", [["--thickness", "-2"], ["--thickness", "2", "--factor", "0"]])
def test_cli_rejects_non_positive_limits(flag):
    with pytest.raises(SystemExit) as e:
        hole_edge.main([str(ROOT / "examples" / "plate.step"), *flag])
    assert e.value.code == 2


def test_no_personal_name_in_build_log():
    assert "Michael" not in (ROOT / "HOW-IT-WAS-BUILT.md").read_text()
