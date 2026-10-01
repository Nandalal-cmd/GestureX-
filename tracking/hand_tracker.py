"""MediaPipe hand tracking adapter."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from app.config import AppConfig
from tracking.landmarks import HandLandmarks, from_mediapipe
from utils.smoothing import smooth_point


class HandTracker:
    """Detect one hand and provide normalized landmarks plus a smoothed palm point."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._hands = None
        self._previous_palm = None
        self._logger = logging.getLogger(__name__)

    def start(self) -> bool:
        try:
            cache_dir = Path(__file__).resolve().parents[1] / ".cache" / "matplotlib"
            cache_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
            import mediapipe as mp

            self._hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                model_complexity=0,
                min_detection_confidence=self.config.gesture_sensitivity,
                min_tracking_confidence=self.config.gesture_sensitivity,
            )
            return True
        except Exception:
            self._logger.exception("MediaPipe hand tracking could not be initialized")
            self.close()
            return False

    def process(self, bgr_frame) -> HandLandmarks | None:
        """Process a BGR OpenCV frame and return the first detected hand, if any."""
        if self._hands is None and not self.start():
            return None

        import cv2

        result = self._hands.process(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
        if not result.multi_hand_landmarks:
            self._previous_palm = None
            return None

        label = result.multi_handedness[0].classification[0].label if result.multi_handedness else "Unknown"
        hand = from_mediapipe(result.multi_hand_landmarks[0], label)
        smoothed_palm = smooth_point(self._previous_palm, hand.palm_center, self.config.smoothing_factor)
        self._previous_palm = smoothed_palm
        return HandLandmarks(hand.points, hand.handedness, smoothed_palm)

    def close(self) -> None:
        if self._hands is not None:
            self._hands.close()
            self._hands = None
        self._previous_palm = None
