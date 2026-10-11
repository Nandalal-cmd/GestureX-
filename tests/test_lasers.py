from effects.lasers import LaserSystem


def test_fire_respects_cooldown():
    las = LaserSystem(speed=100.0, cooldown=0.1, life=2.0)
    assert las.fire((0.0, 0.0), 0.0, 0.0) is True
    assert las.fire((0.0, 0.0), 0.0, 0.0) is False
    assert las.fire((0.0, 0.0), 0.0, 0.2) is True
    assert len(las.shots) == 2


def test_update_moves_and_expires_shots():
    las = LaserSystem(speed=100.0, cooldown=0.0, life=2.0)
    las.fire((0.0, 0.0), 0.0, 0.0)
    las.fire((0.0, 0.0), 1.5708, 0.05)
    las.update(1.0)
    assert abs(las.shots[0]["x"] - 100.0) < 1e-6
    assert abs(las.shots[1]["y"] - 100.0) < 1e-6
    las.update(2.0)
    assert las.shots == []


def test_reset_clears():
    las = LaserSystem(cooldown=0.0)
    las.fire((0.0, 0.0), 0.0, 0.0)
    las.reset()
    assert las.shots == []