from app.config import AppConfig
from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import GestureType
from tracking.landmarks import (
    INDEX_PIP, INDEX_TIP, MIDDLE_PIP, MIDDLE_TIP, PINKY_PIP, PINKY_TIP,
    RING_PIP, RING_TIP, THUMB_TIP, HandLandmarks,
)


def make_hand(*, extended: bool, pinch: bool = False) -> HandLandmarks:
    points = [(0.5, 0.5)] * 21
    for tip, pip in ((INDEX_TIP, INDEX_PIP), (MIDDLE_TIP, MIDDLE_PIP), (RING_TIP, RING_PIP), (PINKY_TIP, PINKY_PIP)):
        points[pip] = (0.5, 0.5)
        points[tip] = (0.5, 0.3 if extended else 0.7)
    points[THUMB_TIP] = (0.51, 0.3) if pinch else (0.1, 0.5)
    return HandLandmarks(tuple(points))


def test_detects_open_palm_fist_and_pinch() -> None:
    detector = GestureDetector(AppConfig())
    assert detector.detect(make_hand(extended=True)).gesture is GestureType.OPEN_PALM
    assert detector.detect(make_hand(extended=False)).gesture is GestureType.FIST
    assert detector.detect(make_hand(extended=True, pinch=True)).gesture is GestureType.PINCH
