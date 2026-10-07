import logging
import math
import time

import pygame

from app import config
from camera.camera import Camera
from effects.galaxy import FACTS, Galaxy
from effects.trails import Trail
from gestures.gesture_detector import detect_pose, finger_states, pinch_distance, pinch_point
from gestures.gesture_types import GestureType
from gestures.motion_tracker import MotionTracker
from rendering.renderer import Renderer
from tracking.hand_tracker import HandTracker
from tracking.landmarks import INDEX_MCP, MIDDLE_MCP, PINKY_MCP, WRIST
from ui.main_window import UIState
from utils.logger import setup_logging

logger = logging.getLogger(__name__)

STRETCH_REF_PX = 430.0
GRAB_PINCH_THRESHOLD = 0.055
DEFAULT_YAW = 0.0
DEFAULT_TILT = 0.45


def hand_orientation(landmarks, handedness: str = "Right"):
    """Return (yaw, tilt) from wrist orientation of an upright hand."""
    index = landmarks[INDEX_MCP]
    pinky = landmarks[PINKY_MCP]
    wrist = landmarks[WRIST]
    middle = landmarks[MIDDLE_MCP]

    roll = math.atan2(pinky.y - index.y, pinky.x - index.x)
    base = 0.0 if handedness == "Right" else math.pi
    yaw = (roll - base + math.pi) % math.tau - math.pi
    yaw = max(-1.1, min(1.1, yaw))

    dy = wrist.y - middle.y
    tilt = max(0.05, min(1.3, DEFAULT_TILT + (dy - 0.35) * 1.5))
    return yaw, tilt


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
            landmarks, palm, label = hand
            g, c = detect_pose(landmarks, config.GESTURE_SENSITIVITY)
            open_count = sum(1 for open_ in finger_states(landmarks).values() if open_)
            swipe = motions[i].update(palm)
            if swipe is not None:
                swipe_display = swipe
                swipe_display_until = time.monotonic() + 0.6
                galaxy.fling(3.5)
            trails[i].push(palm)
            per_hand.append((landmarks, palm, g, c, open_count, label))
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
            landmarks1, palm1, label1 = hand1[0], hand1[1], hand1[5]
            yaw, tilt = hand_orientation(landmarks1, label1)
            galaxy.set_orientation(yaw, tilt)
            palm_screen = (palm1[0] * w, palm1[1] * h)
        else:
            galaxy.set_orientation(DEFAULT_YAW, DEFAULT_TILT)

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
                galaxy.set_stretch(0.85)

        galaxy_anchor = (w / 2.0, h / 2.0)
        galaxy.update(dt, effective_gesture)

        renderer.draw_frame(last_frame, dim=140)
        galaxy.draw(renderer.surface, galaxy_anchor, elapsed)

        gesture_colors = {
            "OPEN_PALM": (120, 230, 160),
            "FIST": (255, 150, 110),
            "PINCH": (255, 215, 120),
            "UNKNOWN": (175, 185, 205),
        }
        gcolor = gesture_colors.get(state.gesture, (150, 195, 255))
        rows = [
            ("kv", "Gesture", state.gesture, gcolor),
            ("bar", "Confidence", state.confidence, (80, 145, 255)),
            ("kv", "Stretch", f"{galaxy.stretch:.2f}x", (205, 215, 240)),
        ]
        if galaxy.grabbed is not None:
            rows.append(("kv", "Planet", galaxy.grabbed.name, (255, 222, 145)))
            rows.append(("small", FACTS.get(galaxy.grabbed.name, ""), (150, 175, 215)))
        for i, entry in enumerate(per_hand):
            landmarks, palm, g, c, open_count, label = entry
            renderer.draw_hand_outline(landmarks)
            renderer.draw_trail(trails[i].render_points(w, h))
            rows.append(("header", f"HAND {i + 1} - {label.upper()}", (120, 200, 255)))
            rows.append(("fingers", "Fingers", open_count, 5))
            hg = gesture_colors.get(g.value, (150, 195, 255))
            rows.append(("kv", "Pose", g.value, hg))
        if not per_hand:
            rows.append(("header", "NO HAND DETECTED", (255, 170, 110)))
            rows.append(("small", "Show a hand to the camera", (170, 180, 200)))
        renderer.render_hud(rows)
        hint = ("TWIST WRIST = ROTATE   |   TWO HANDS = STRETCH   |   "
                "PINCH HAND 2 = GRAB   |   SWIPE = FLING   |   FIST = COLLAPSE")
        hint_surf = renderer.small_font.render(hint, True, (185, 198, 225))
        hw = hint_surf.get_width()
        hs = pygame.Surface((hw + 28, 30), pygame.SRCALPHA)
        pygame.draw.rect(hs, (8, 10, 20, 170), hs.get_rect(), border_radius=8)
        hs.blit(hint_surf, (14, 6))
        renderer.surface.blit(hs, ((renderer.width - hw - 28) // 2,
                                   renderer.height - 42))
        renderer.present()

    camera.stop()
    tracker.close()
    renderer.quit()
    logger.info("GestureFX closed cleanly.")


if __name__ == "__main__":
    main()
