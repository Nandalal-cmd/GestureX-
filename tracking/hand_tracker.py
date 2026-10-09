import logging
from types import SimpleNamespace

import cv2
import mediapipe as mp

from tracking.landmarks import palm_center
from utils.smoothing import smooth_point

logger = logging.getLogger(__name__)


class HandTracker:
    def __init__(self, smoothing_factor: float = 0.65, max_hands: int = 2,
                 process_width: int = 360,
                 min_detection_confidence: float = 0.4,
                 min_tracking_confidence: float = 0.4,
                 landmark_smoothing: float = 0.55,
                 enhance_contrast: bool = True):
        self.smoothing_factor = smoothing_factor
        self.landmark_smoothing = landmark_smoothing
        self.process_width = process_width
        self.enhance_contrast = enhance_contrast
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._smoothed = {}

    def _enhance(self, rgb):
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l = clahe.apply(l)
        return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)

    def _smoothed_landmarks(self, label, raw):
        prev = self._smoothed.get(label)
        if prev is None:
            lms = [SimpleNamespace(x=lm.x, y=lm.y, z=lm.z) for lm in raw]
            palm = palm_center(lms)
            return lms, palm
        prev_lms, prev_palm = prev
        k = self.landmark_smoothing
        lms = []
        for old, cur in zip(prev_lms, raw):
            lms.append(SimpleNamespace(
                x=old.x + (cur.x - old.x) * (1.0 - k),
                y=old.y + (cur.y - old.y) * (1.0 - k),
                z=old.z + (cur.z - old.z) * (1.0 - k),
            ))
        palm = smooth_point(prev_palm, palm_center(lms), self.smoothing_factor)
        return lms, palm

    def process(self, frame_bgr):
        """Return list of (landmarks, palm_center_norm, handedness) per hand."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        if self.enhance_contrast:
            rgb = self._enhance(rgb)
        h, w = rgb.shape[:2]
        if w > self.process_width:
            nh = max(1, int(h * self.process_width / w))
            rgb = cv2.resize(rgb, (self.process_width, nh),
                             interpolation=cv2.INTER_AREA)
        results = self._hands.process(rgb)
        if not results.multi_hand_landmarks:
            self._smoothed = {}
            return []
        out = []
        active = set()
        for i, hand in enumerate(results.multi_hand_landmarks):
            label = "Right"
            if results.multi_handedness and i < len(results.multi_handedness):
                label = results.multi_handedness[i].classification[0].label
            lms, palm = self._smoothed_landmarks(label, hand.landmark)
            self._smoothed[label] = (lms, palm)
            active.add(label)
            out.append((lms, palm, label))
        self._smoothed = {k: v for k, v in self._smoothed.items() if k in active}
        return out

    def close(self) -> None:
        self._hands.close()