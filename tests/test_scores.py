from utils.scores import BestScore


def test_defaults_to_zero(tmp_path):
    best = BestScore(tmp_path / "best.json")
    assert best.value == 0


def test_update_persists_and_reports_new_best(tmp_path):
    p = tmp_path / "best.json"
    best = BestScore(p)
    assert best.update(5) is True
    assert best.value == 5
    assert best.update(5) is False
    assert best.update(7) is True
    assert best.value == 7
    reloaded = BestScore(p)
    assert reloaded.value == 7


def test_missing_file_ignored(tmp_path):
    assert BestScore(tmp_path / "nope.json").value == 0