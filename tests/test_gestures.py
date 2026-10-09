import math
from types import SimpleNamespace

from gestures.gesture_detector import (
    PoseStabilizer,
    detect_pose,
    extended_fingers,
    pinch_point,
    pinch_ratio,
)
from gestures.gesture_types import GestureType


def make_landmarks(points):
    return [SimpleNamespace(x=x, y=y, z=0.0) for x, y in points]


def open_palm():
    pts = [(0.5, 0.85)] * 21
    pts[0] = (0.5, 0.85)      # wrist
    pts[9] = (0.5, 0.55)      # middle MCP
    pts[4] = (0.30, 0.45)     # thumb tip
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        pts[pip] = (0.5, 0.55)
        pts[tip] = (0.5, 0.30)
        pts[pip - 1] = (0.5, 0.65)
    return make_landmarks(pts)


def fist():
    pts = [(0.5, 0.80)] * 21
    pts[0] = (0.5, 0.80)
    pts[9] = (0.5, 0.62)
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


def _transform(pts, fn):
    return [SimpleNamespace(x=fn(p.x, p.y)[0], y=fn(p.x, p.y)[1], z=0.0)
            for p in pts]


def _rotate(pts, degrees):
    a = math.radians(degrees)
    ca, sa = math.cos(a), math.sin(a)
    return _transform(pts, lambda x, y: (
        0.5 + (x - 0.5) * ca - (y - 0.5) * sa,
        0.5 + (x - 0.5) * sa + (y - 0.5) * ca,
    ))


def _scale(pts, f):
    return _transform(pts, lambda x, y: (x * f, y * f))


def test_balled_hand_with_mixed_fingers_is_fist():
    pts = [(0.5, 0.80)] * 21
    pts[0] = (0.5, 0.80)
    pts[9] = (0.5, 0.60)
    pts[6] = (0.5, 0.70)
    pts[8] = (0.5, 0.64)
    pts[10] = (0.5, 0.71)
    pts[12] = (0.5, 0.65)
    pts[14] = (0.5, 0.72)
    pts[16] = (0.5, 0.75)
    pts[18] = (0.5, 0.73)
    pts[20] = (0.5, 0.76)
    gesture, conf = detect_pose(make_landmarks(pts))
    assert extended_fingers(make_landmarks(pts)) == 2
    assert gesture == GestureType.FIST
    assert 0.0 <= conf <= 1.0


def test_peace_sign_is_not_fist():
    pts = [(0.5, 0.80)] * 21
    pts[0] = (0.5, 0.80)
    pts[9] = (0.5, 0.55)
    pts[6] = (0.5, 0.62)
    pts[8] = (0.5, 0.25)
    pts[10] = (0.5, 0.63)
    pts[12] = (0.5, 0.27)
    pts[14] = (0.5, 0.72)
    pts[16] = (0.5, 0.76)
    pts[18] = (0.5, 0.73)
    pts[20] = (0.5, 0.76)
    gesture, conf = detect_pose(make_landmarks(pts))
    assert gesture == GestureType.UNKNOWN
    assert 0.0 <= conf <= 1.0


def test_extension_is_rotation_invariant():
    for angle in (0, 45, 90, 135, 180, -60):
        assert extended_fingers(_rotate(open_palm(), angle)) == 4, angle
        assert extended_fingers(_rotate(fist(), angle)) == 0, angle
        gesture, _ = detect_pose(_rotate(open_palm(), angle))
        assert gesture == GestureType.OPEN_PALM, angle
        gesture, _ = detect_pose(_rotate(fist(), angle))
        assert gesture == GestureType.FIST, angle


def test_far_hand_does_not_false_pinch():
    far_palm = _scale(open_palm(), 0.2)
    gesture, _ = detect_pose(far_palm)
    assert gesture == GestureType.OPEN_PALM
    assert pinch_ratio(far_palm) > 0.35


def test_pinch_recognized_at_any_distance():
    for f in (0.3, 0.6, 1.0, 1.8):
        gesture, conf = detect_pose(_scale(pinch(), f))
        assert gesture == GestureType.PINCH, f
        assert 0.0 <= conf <= 1.0


def test_stabilizer_rejects_flicker():
    s = PoseStabilizer()
    for _ in range(5):
        s.update(GestureType.OPEN_PALM, 0.9)
    assert s.current == GestureType.OPEN_PALM
    for _ in range(4):
        s.update(GestureType.FIST, 0.8)
    assert s.current == GestureType.OPEN_PALM
    s.update(GestureType.FIST, 0.8)
    assert s.current == GestureType.FIST


def test_stabilizer_reset():
    s = PoseStabilizer()
    for _ in range(5):
        s.update(GestureType.FIST, 0.9)
    assert s.current == GestureType.FIST
    s.reset()
    assert s.current == GestureType.UNKNOWN
    assert not s.history
