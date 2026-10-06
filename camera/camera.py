import cv2
import logging

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720):
        self.index = index
        self.width = width
        self.height = height
        self._cap = None

    def start(self) -> bool:
        self._cap = cv2.VideoCapture(self.index)
        if not self._cap.isOpened():
            logger.error("Camera unavailable at index %d.", self.index)
            self._cap = None
            return False
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        logger.info("Camera ACTIVE (index %d).", self.index)
        return True

    def read(self):
        if self._cap is None:
            return False, None
        ok, frame = self._cap.read()
        if not ok:
            return False, None
        return True, cv2.flip(frame, 1)

    def stop(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Camera stopped.")

    @property
    def active(self) -> bool:
        return self._cap is not None
