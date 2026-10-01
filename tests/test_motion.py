from gestures.gesture_types import GestureType
from gestures.motion_tracker import MotionTracker


def test_motion_tracker_emits_right_swipe_event() -> None:
    tracker = MotionTracker(minimum_distance=0.1, cooldown=0.0)
    assert tracker.update((0.1, 0.5), timestamp=1.0) is None
    event = tracker.update((0.3, 0.5), timestamp=1.1)
    assert event is not None
    assert event.gesture is GestureType.SWIPE_RIGHT
