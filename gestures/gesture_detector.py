import math

from gestures.gesture_types import GestureType
from tracking.landmarks import (
    INDEX_TIP,
    PINKY_TIP,
    RING_TIP,
    THUMB_TIP,
    TIP_PIP_PAIRS,
    WRIST,
)
from utils.geometry import clamp

PINCH_THRESHOLD = 0.055
FIST_THRESHOLD = 0.16


def _finger_extended(landmarks, tip_idx, pip_idx) -> bool:
    return landmarks[tip_idx].y < landmarks[pip_idx].y


def extended_fingers(landmarks) -> int:
    return sum(1 for tip, pip in TIP_PIP_PAIRS if _finger_extended(landmarks, tip, pip))


def pinch_distance(landmarks) -> float:
    t = landmarks[THUMB_TIP]
    i = landmarks[INDEX_TIP]
    return math.hypot(t.x - i.x, t.y - i.y)


def pinch_point(landmarks):
    t = landmarks[THUMB_TIP]
    i = landmarks[INDEX_TIP]
    return ((t.x + i.x) / 2.0, (t.y + i.y) / 2.0)


def fist_score(landmarks) -> float:
    wrist = landmarks[WRIST]
    tips = [landmarks[i] for i in (INDEX_TIP, 12, 16, PINKY_TIP)]
    avg = sum(math.hypot(t.x - wrist.x, t.y - wrist.y) for t in tips) / len(tips)
    return avg


FINGER_NAMES = ("THUMB", "INDEX", "MIDDLE", "RING", "PINKY")


def finger_states(landmarks) -> dict:
    """Return {finger_name: bool extended} for all five fingers."""
    import math

    wrist = landmarks[WRIST]
    thumb_tip, thumb_ip = landmarks[THUMB_TIP], landmarks[3]
    d_tip = math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y)
    d_ip = math.hypot(thumb_ip.x - wrist.x, thumb_ip.y - wrist.y)
    thumb_open = d_tip > d_ip * 1.15
    states = {"THUMB": thumb_open}
    for name, (tip, pip) in zip(FINGER_NAMES[1:], TIP_PIP_PAIRS):
        states[name] = _finger_extended(landmarks, tip, pip)
    return states


def detect_pose(landmarks, sensitivity: float = 0.5):
    """Return (GestureType, confidence) for the steady pose gestures."""
    pinch_thresh = PINCH_THRESHOLD * (1.5 - sensitivity)
    pd = pinch_distance(landmarks)
    if pd < pinch_thresh:
        confidence = clamp(1.0 - pd / pinch_thresh)
        return GestureType.PINCH, confidence

    extended = extended_fingers(landmarks)
    if extended >= 3:
        confidence = clamp(0.6 + 0.1 * extended)
        return GestureType.OPEN_PALM, confidence

    if fist_score(landmarks) < FIST_THRESHOLD * (0.6 + sensitivity):
        confidence = clamp(1.0 - fist_score(landmarks) / (FIST_THRESHOLD * (0.6 + sensitivity)))
        return GestureType.FIST, confidence

    if extended <= 1:
        return GestureType.FIST, 0.5
    return GestureType.UNKNOWN, 0.3
