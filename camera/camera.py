"""Safe OpenCV webcam capture isolated from tracking and rendering."""

from __future__ import annotations

import logging

from app.config import AppConfig


class Camera:
    """Own an OpenCV camera capture device and release it deterministically."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._capture = None
        self._logger = logging.getLogger(__name__)

    @property
    def is_active(self) -> bool:
        return self._capture is not None and self._capture.isOpened()

    def start(self) -> bool:
        """Open the configured camera, returning False rather than crashing on failure."""
        if self.is_active:
            return True

        try:
            import cv2

            self._capture = cv2.VideoCapture(self.config.camera_index)
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
        except Exception:
            self._logger.exception("Unable to initialize camera %s", self.config.camera_index)
            self.stop()
            return False

        if not self.is_active:
            self._logger.warning("Camera %s is unavailable", self.config.camera_index)
            self.stop()
            return False
        return True

    def read(self):
        """Return the next BGR camera frame, or None if a frame cannot be read."""
        if not self.is_active:
            return None
        success, frame = self._capture.read()
        if not success:
            self._logger.warning("Camera frame read failed")
            return None
        return frame

    def stop(self) -> None:
        """Release camera resources safely."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "Camera":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()
