from types import SimpleNamespace

from gestures.gesture_detector import detect_pose, pinch_point
from gestures.gesture_types import GestureType


def make_landmarks(points):
    return [SimpleNamespace(x=x, y=y, z=0.0) for x, y in points]


def open_palm():
    pts = [(0.5, 0.85)] * 21
    pts[0] = (0.5, 0.85)      # wrist
    pts[4] = (0.30, 0.45)     # thumb tip
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        pts[pip] = (0.5, 0.55)
        pts[tip] = (0.5, 0.30)
        pts[pip - 1] = (0.5, 0.65)
    return make_landmarks(pts)


def fist():
    pts = [(0.5, 0.80)] * 21
    pts[0] = (0.5, 0.80)
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        pts[pip] = (0.5, 0.74)
        pts[tip] = (0.5, 0.78)
    pts[4] = (0.35, 0.75)
    return make_landmarks(pts)


def pinch():
    pts = fist()
    raw = [(p.x, p.y) for p in pts]
    raw[4] = (0.40, 0.40)
    raw[8] = (0.42, 0.41)
    raw[6] = (0.5, 0.45)
    return make_landmarks(raw)


def test_open_palm_detected():
    gesture, conf = detect_pose(open_palm())
    assert gesture == GestureType.OPEN_PALM
    assert 0.0 <= conf <= 1.0


def test_fist_detected():
    gesture, conf = detect_pose(fist())
    assert gesture == GestureType.FIST
    assert 0.0 <= conf <= 1.0


def test_pinch_detected():
    gesture, conf = detect_pose(pinch())
    assert gesture == GestureType.PINCH
    assert 0.0 <= conf <= 1.0


def test_pinch_point_midpoint():
    pp = pinch_point(pinch())
    assert abs(pp[0] - 0.41) < 1e-6
    assert abs(pp[1] - 0.405) < 1e-6
