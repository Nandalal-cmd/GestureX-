import logging
import math
import time

import pygame

from app import config
from camera.camera import Camera
from effects.galaxy import Galaxy
from effects.trails import Trail
from gestures.gesture_detector import detect_pose, finger_states, pinch_distance, pinch_point
from gestures.gesture_types import GestureType
from gestures.motion_tracker import MotionTracker
from rendering.renderer import Renderer
from tracking.hand_tracker import HandTracker
from ui.main_window import UIState
from utils.logger import setup_logging

logger = logging.getLogger(__name__)

STRETCH_REF_PX = 430.0
GRAB_PINCH_THRESHOLD = 0.055


def main() -> None:
    setup_logging()
    state = UIState()
    camera = Camera(config.CAMERA_INDEX)
    state.camera_active = camera.start()

    tracker = HandTracker(config.SMOOTHING_FACTOR, max_hands=2)
    motions = [MotionTracker(config.SMOOTHING_FACTOR),
               MotionTracker(config.SMOOTHING_FACTOR)]
    trails = [Trail(config.TRAIL_LENGTH), Trail(config.TRAIL_LENGTH)]
    galaxy = Galaxy()
    renderer = Renderer(1280, 720)
    clock = pygame.time.Clock()

    w, h = renderer.width, renderer.height
    swipe_display = None
    swipe_display_until = 0.0
    start_time = time.monotonic()

    while state.running:
        dt = max(clock.tick(config.TARGET_FPS) / 1000.0, 1e-3)
        elapsed = time.monotonic() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False

        hands = []
        last_frame = None
        if camera.active:
            ok, frame = camera.read()
            if ok:
                last_frame = frame
                hands = tracker.process(frame)
            else:
                logger.warning("Frame grab failed.")

        best_gesture = GestureType.UNKNOWN
        best_confidence = 0.0
        palm_screen = None
        per_hand = []

        for i, hand in enumerate(hands):
            landmarks, palm = hand
            g, c = detect_pose(landmarks, config.GESTURE_SENSITIVITY)
            open_count = sum(1 for open_ in finger_states(landmarks).values() if open_)
            swipe = motions[i].update(palm)
            if swipe is not None:
                swipe_display = swipe
                swipe_display_until = time.monotonic() + 0.6
                galaxy.fling(3.5)
            trails[i].push(palm)
            per_hand.append((landmarks, palm, g, c, open_count))
            if g != GestureType.UNKNOWN and (best_gesture == GestureType.UNKNOWN
                                              or c > best_confidence):
                best_gesture, best_confidence = g, c

        for i in range(2):
            if i >= len(hands):
                motions[i].reset()
                while trails[i].points:
                    trails[i].points.pop(0)

        hand1 = per_hand[0] if len(per_hand) >= 1 else None
        hand2 = per_hand[1] if len(per_hand) >= 2 else None

        if hand1 is not None:
            palm_screen = (hand1[1][0] * w, hand1[1][1] * h)

        if swipe_display is not None and time.monotonic() < swipe_display_until:
            state.gesture = swipe_display
            effective_gesture = GestureType(swipe_display)
        else:
            swipe_display = None
            state.gesture = best_gesture.value
            effective_gesture = best_gesture
        state.confidence = best_confidence

        if hand1 is not None and palm_screen is not None:
            if hand2 is not None:
                palm1, palm2 = hand1[1], hand2[1]
                dist = math.hypot((palm2[0] - palm1[0]) * w,
                                  (palm2[1] - palm1[1]) * h)
                galaxy.set_stretch(dist / STRETCH_REF_PX)
                landmarks2 = hand2[0]
                pp = pinch_point(landmarks2)
                pp_screen = (pp[0] * w, pp[1] * h)
                if pinch_distance(landmarks2) < GRAB_PINCH_THRESHOLD:
                    if galaxy.grabbed is None:
                        galaxy.grab(pp_screen)
                    else:
                        galaxy.drag(pp_screen)
                else:
                    galaxy.release()
            else:
                galaxy.release()
                galaxy.set_stretch(1.0)

        galaxy_anchor = (w / 2.0, h / 2.0)
        galaxy.update(dt, effective_gesture)

        renderer.draw_frame(last_frame, dim=140)
        galaxy.draw(renderer.surface, galaxy_anchor, elapsed)
        hud = [
            f"Gesture: {state.gesture}",
            f"Confidence: {state.confidence:.0%}",
            f"Stretch: {galaxy.stretch:.2f}x",
        ]
        if galaxy.grabbed is not None:
            hud.append(f"Grabbed: {galaxy.grabbed['name']}")
        for i, entry in enumerate(per_hand):
            landmarks, palm, g, c, open_count = entry
            renderer.draw_hand_outline(landmarks)
            renderer.draw_trail(trails[i].render_points(w, h))
            hud.append(f"Hand {i + 1}: {g.value} ({c:.0%}) - {open_count}/5 up")
        renderer.draw_hud(hud)
        renderer.present()

    camera.stop()
    tracker.close()
    renderer.quit()
    logger.info("GestureFX closed cleanly.")


if __name__ == "__main__":
    main()
