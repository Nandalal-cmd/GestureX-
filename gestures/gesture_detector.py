import math
from collections import Counter, deque

from gestures.gesture_types import GestureType
from tracking.landmarks import (
    INDEX_TIP,
    MIDDLE_MCP,
    PINKY_TIP,
    RING_TIP,
    THUMB_TIP,
    TIP_PIP_PAIRS,
    WRIST,
)
from utils.geometry import clamp

PINCH_RATIO = 0.35
PINCH_RATIO_RELEASE = 0.48
MIN_HAND_SCALE = 0.06


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def hand_scale(landmarks) -> float:
    """Palm length (wrist -> middle MCP); used to normalize all thresholds."""
    return max(_dist(landmarks[WRIST], landmarks[MIDDLE_MCP]), MIN_HAND_SCALE)


def _finger_extended(landmarks, tip_idx, pip_idx) -> bool:
    """Rotation-invariant: a finger is extended when its tip is farther from
    the wrist than its PIP joint (works at any hand orientation)."""
    wrist = landmarks[WRIST]
    return _dist(landmarks[tip_idx], wrist) > _dist(landmarks[pip_idx], wrist) * 1.08


def extended_fingers(landmarks) -> int:
    return sum(1 for tip, pip in TIP_PIP_PAIRS if _finger_extended(landmarks, tip, pip))


def pinch_distance(landmarks) -> float:
    t = landmarks[THUMB_TIP]
    i = landmarks[INDEX_TIP]
    return math.hypot(t.x - i.x, t.y - i.y)


def pinch_ratio(landmarks) -> float:
    """Pinch distance normalized by hand size — scale invariant."""
    return pinch_distance(landmarks) / hand_scale(landmarks)


def is_pinching(landmarks, sensitivity: float = 0.5) -> bool:
    return pinch_ratio(landmarks) < PINCH_RATIO * (1.5 - sensitivity)


def pinch_point(landmarks):
    t = landmarks[THUMB_TIP]
    i = landmarks[INDEX_TIP]
    return ((t.x + i.x) / 2.0, (t.y + i.y) / 2.0)


def fist_score(landmarks) -> float:
    wrist = landmarks[WRIST]
    tips = [landmarks[i] for i in (INDEX_TIP, 12, 16, PINKY_TIP)]
    avg = sum(_dist(t, wrist) for t in tips) / len(tips)
    return avg / hand_scale(landmarks)


FINGER_NAMES = ("THUMB", "INDEX", "MIDDLE", "RING", "PINKY")


def finger_states(landmarks) -> dict:
    """Return {finger_name: bool extended} for all five fingers."""
    wrist = landmarks[WRIST]
    thumb_tip, thumb_ip = landmarks[THUMB_TIP], landmarks[3]
    d_tip = _dist(thumb_tip, wrist)
    d_ip = _dist(thumb_ip, wrist)
    thumb_open = d_tip > d_ip * 1.15
    states = {"THUMB": thumb_open}
    for name, (tip, pip) in zip(FINGER_NAMES[1:], TIP_PIP_PAIRS):
        states[name] = _finger_extended(landmarks, tip, pip)
    return states


def detect_pose(landmarks, sensitivity: float = 0.5):
    """Return (GestureType, confidence) for the steady pose gestures."""
    if is_pinching(landmarks, sensitivity):
        ratio = pinch_ratio(landmarks)
        limit = PINCH_RATIO * (1.5 - sensitivity)
        return GestureType.PINCH, clamp(0.55 + 0.45 * (1.0 - ratio / limit))

    extended = extended_fingers(landmarks)
    if extended >= 3:
        return GestureType.OPEN_PALM, clamp(0.6 + 0.1 * extended)

    if extended <= 1:
        return GestureType.FIST, clamp(0.5 + 0.12 * (4 - extended))

    return GestureType.UNKNOWN, 0.3


class PoseStabilizer:
    """Temporal majority vote so poses don't flicker between frames.

    A new pose must win `switch_votes` of the last `window` frames before it
    replaces the settled one; the current pose gets hysteresis against noise.
    """

    def __init__(self, window: int = 7, switch_votes: int = 5):
        self.history = deque(maxlen=window)
        self.switch_votes = switch_votes
        self.current = GestureType.UNKNOWN
        self.confidence = 0.0

    def update(self, gesture, confidence: float):
        self.history.append(gesture)
        if not self.history:
            return self.current, self.confidence
        if gesture == self.current:
            self.confidence = max(self.confidence * 0.9, confidence)
            return self.current, self.confidence
        counts = Counter(self.history)
        top, top_n = counts.most_common(1)[0]
        if top != self.current and top_n >= self.switch_votes:
            self.current = top
            self.confidence = confidence
        return self.current, self.confidence

    def reset(self):
        self.history.clear()
        self.current = GestureType.UNKNOWN
        self.confidence = 0.0
