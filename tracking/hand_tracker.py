import logging

import cv2
import mediapipe as mp

from tracking.landmarks import palm_center
from utils.smoothing import smooth_point

logger = logging.getLogger(__name__)


class HandTracker:
    def __init__(self, smoothing_factor: float = 0.65, max_hands: int = 2):
        self.smoothing_factor = smoothing_factor
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._smoothed_palms = {}

    def process(self, frame_bgr):
        """Return list of (landmarks, palm_center_norm, handedness) per hand."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)
        if not results.multi_hand_landmarks:
            self._smoothed_palms = {}
            return []
        out = []
        active_ids = set()
        for i, hand in enumerate(results.multi_hand_landmarks):
            landmarks = hand.landmark
            center = palm_center(landmarks)
            prev = self._smoothed_palms.get(i)
            self._smoothed_palms[i] = center if prev is None else smooth_point(prev, center, self.smoothing_factor)
            active_ids.add(i)
            label = "Right"
            if results.multi_handedness and i < len(results.multi_handedness):
                label = results.multi_handedness[i].classification[0].label
            out.append((landmarks, self._smoothed_palms[i], label))
        self._smoothed_palms = {i: self._smoothed_palms[i] for i in active_ids}
        return out

    def close(self) -> None:
        self._hands.close()
