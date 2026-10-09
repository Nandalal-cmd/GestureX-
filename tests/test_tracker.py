from types import SimpleNamespace

from tracking.hand_tracker import HandTracker


def _raw(points):
    return [SimpleNamespace(x=x, y=y, z=0.0) for x, y in points]


def make_tracker():
    t = object.__new__(HandTracker)
    t._smoothed = {}
    t.landmark_smoothing = 0.5
    t.smoothing_factor = 0.5
    return t


def test_landmark_smoothing_holds_still_hand():
    t = make_tracker()
    pts = [(0.3 + i * 0.02, 0.5 + (i % 5) * 0.01) for i in range(21)]
    raw = _raw(pts)
    lms1, _ = t._smoothed_landmarks("Right", raw)
    lms2, _ = t._smoothed_landmarks("Right", raw)
    for a, b in zip(lms1, lms2):
        assert abs(a.x - b.x) < 1e-9
        assert abs(a.y - b.y) < 1e-9


def test_smoothing_tracks_state_by_handedness():
    t = make_tracker()
    left = _raw([(0.1, 0.1)] * 21)
    right = _raw([(0.8, 0.8)] * 21)
    t._smoothed_landmarks("Left", left)
    lms, _ = t._smoothed_landmarks("Right", right)
    assert abs(lms[0].x - 0.8) < 1e-9
    assert abs(lms[0].y - 0.8) < 1e-9
    # Left state is still independent from Right state
    lleft, _ = t._smoothed_landmarks("Left", left)
    assert abs(lleft[0].x - 0.1) < 1e-9