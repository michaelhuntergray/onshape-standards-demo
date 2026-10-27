import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "checker"), str(ROOT / "examples")]

import hole_edge  # noqa: E402
import make_plate  # noqa: E402


@pytest.fixture(scope="module")
def results():
    return sorted(hole_edge.check(make_plate.build(), thickness=2.0, factor=2.0), key=lambda h: h.center[0])


def test_finds_three_holes(results):
    assert [round(h.diameter, 3) for h in results] == [5.0, 4.0, 5.0]


def test_distances_match_hand_calc(results):
    assert [round(h.edge_distance, 3) for h in results] == [7.5, 4.0, 1.5]


def test_verdicts(results):
    assert [h.ok for h in results] == [True, True, False]


def test_cli_on_step_exits_1_on_a_failure(tmp_path, capsys):
    step = tmp_path / "plate.step"
    from build123d import export_step
    export_step(make_plate.build(), str(step))
    assert hole_edge.main([str(step), "--thickness", "2"]) == 1
    assert "3 holes, 1 fail" in capsys.readouterr().out


def test_looser_factor_passes_everything():
    assert all(h.ok for h in hole_edge.check(make_plate.build(), thickness=2.0, factor=0.5))
