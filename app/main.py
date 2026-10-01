"""Application entry point for GestureFX."""

from __future__ import annotations

import importlib.util
import logging
import sys
from argparse import ArgumentParser

from app.config import AppConfig
from camera.camera import Camera
from gestures.gesture_detector import GestureDetector
from gestures.motion_tracker import MotionTracker
from tracking.hand_tracker import HandTracker
from utils.logger import configure_logging

REQUIRED_PACKAGES = ("cv2", "mediapipe", "numpy", "pygame")


def missing_dependencies() -> list[str]:
    """Return import names that are not installed in the active environment."""
    return [name for name in REQUIRED_PACKAGES if importlib.util.find_spec(name) is None]


def run_preview(config: AppConfig) -> int:
    """Run a temporary OpenCV preview for Milestones 1–3; press Q or Escape to close."""
    import cv2

    camera = Camera(config)
    tracker = HandTracker(config)
    detector = GestureDetector(config)
    motion = MotionTracker()
    if not camera.start():
        logging.getLogger(__name__).error("Camera unavailable. Please connect or enable a webcam.")
        return 1
    if not tracker.start():
        camera.stop()
        return 1

    logger = logging.getLogger(__name__)
    logger.info("Camera preview active. Press Q or Escape to stop.")
    try:
        while True:
            frame = camera.read()
            if frame is None:
                break
            hand = tracker.process(frame)
            result = motion.update(hand.interaction_point if hand else None) or detector.detect(hand)
            label = f"{result.gesture.value} ({result.confidence:.0%})"
            cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 220, 120), 2)
            if hand:
                for x, y in hand.points:
                    cv2.circle(frame, (round(x * frame.shape[1]), round(y * frame.shape[0])), 3, (0, 220, 255), -1)
            cv2.imshow("GestureFX — Camera Preview", cv2.flip(frame, 1))
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
    except Exception:
        logger.exception("Camera preview stopped after a recoverable error")
        return 1
    finally:
        tracker.close()
        camera.stop()
        cv2.destroyAllWindows()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Validate dependencies or start the optional early-milestone camera preview."""
    configure_logging()
    logger = logging.getLogger(__name__)
    config = AppConfig()
    parser = ArgumentParser(description="GestureFX")
    parser.add_argument("--preview", action="store_true", help="open the webcam tracking preview")
    args = parser.parse_args(argv)
    missing = missing_dependencies()

    if missing:
        logger.error("Missing dependencies: %s", ", ".join(missing))
        logger.error("Create a virtual environment and run: python -m pip install -r requirements.txt")
        return 1

    logger.info("GestureFX project setup is ready.")
    logger.info("Target FPS: %s | Default particles: %s", config.target_fps, config.default_particles)
    if args.preview:
        return run_preview(config)
    logger.info("Run `python -m app.main --preview` to test the camera and hand tracking.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
