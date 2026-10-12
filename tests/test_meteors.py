from effects.meteors import MeteorShower


def test_shower_starts_after_delay():
    m = MeteorShower(interval_min=10, interval_max=10, first_delay=1.0, burst=7)
    assert m.meteors == []
    for _ in range(11):
        m.update(0.1, 640, 360)
    assert m.just_started is True
    m.just_started = False
    assert m.active > 0


def test_shower_spawns_burst():
    m = MeteorShower(burst=7)
    m._spawn_shower(640, 360)
    assert len(m.meteors) == 7


def test_meteors_cross_screen_and_expire():
    m = MeteorShower(first_delay=0.0, burst=1, speed=800.0)
    w, h = 640, 360
    m._spawn_shower(w, h)
    assert len(m.meteors) == 1
    for _ in range(120):
        m.update(0.016, w, h)
    assert len(m.meteors) == 0


def test_hit_removes_meteor():
    m = MeteorShower(first_delay=0.0, burst=1)
    m._spawn_shower(640, 360)
    m.update(0.01, 640, 360)
    target = m.meteors[0]
    hits = m.hit((target["x"], target["y"]), radius=7.0)
    assert len(hits) == 1
    assert target not in m.meteors
    assert m.hit((target["x"], target["y"])) == []