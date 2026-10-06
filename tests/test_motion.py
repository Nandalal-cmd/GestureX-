from gestures.motion_tracker import MotionTracker


def test_swipe_right_detected():
    mt = MotionTracker(smoothing_factor=0.0)
    result = None
    for i in range(6):
        result = result or mt.update((0.2 + i * 0.05, 0.5), now=float(i) * 0.05)
    assert result == "SWIPE_RIGHT"


def test_no_swipe_when_stationary():
    mt = MotionTracker(smoothing_factor=0.0)
    result = None
    for i in range(6):
        result = mt.update((0.5, 0.5), now=float(i) * 0.05)
    assert result is None


def test_swipe_up_detected():
    mt = MotionTracker(smoothing_factor=0.0)
    result = None
    for i in range(6):
        result = result or mt.update((0.5, 0.8 - i * 0.05), now=float(i) * 0.05)
    assert result == "SWIPE_UP"
