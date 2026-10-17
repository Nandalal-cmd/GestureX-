from utils.scores import BestScore, Leaderboard


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


def test_leaderboard_keeps_top_n_sorted(tmp_path):
    lb = Leaderboard(tmp_path / "lb.json", size=3)
    assert lb.add(10) is True
    assert lb.add(30) is True
    assert lb.add(20) is True
    assert lb.entries == [30, 20, 10]
    assert lb.add(5) is False
    assert lb.entries == [30, 20, 10]


def test_leaderboard_persists(tmp_path):
    p = tmp_path / "lb.json"
    lb = Leaderboard(p, size=3)
    lb.add(12)
    lb.add(7)
    reloaded = Leaderboard(p, size=3)
    assert reloaded.entries == [12, 7]
    assert reloaded.best() == 12


def test_leaderboard_rank(tmp_path):
    lb = Leaderboard(tmp_path / "lb.json", size=3)
    lb.add(50)
    lb.add(20)
    assert lb.rank_of(100) == 1
    assert lb.rank_of(25) == 2
    assert lb.rank_of(1) == 3
    assert lb.rank_of(0) == 0


def test_leaderboard_ignores_nonpositive(tmp_path):
    lb = Leaderboard(tmp_path / "lb.json", size=3)
    assert lb.add(0) is False
    assert lb.add(-4) is False
    assert lb.entries == []