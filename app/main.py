import logging
import math
import random
import time

import pygame

from app import config
from camera.camera import Camera
from effects.galaxy import FACTS, Galaxy
from effects.lasers import LaserSystem
from effects.meteors import MeteorShower
from effects.shockwaves import Shockwaves
from effects.starfield import Starfield
from effects.trails import Trail
from gestures.gesture_detector import (
    PINCH_RATIO,
    PINCH_RATIO_RELEASE,
    PoseStabilizer,
    detect_pose,
    finger_states,
    hand_scale,
    pinch_point,
    pinch_ratio,
)
from gestures.gesture_types import GestureType
from gestures.motion_tracker import MotionTracker
from particles.particle_system import ParticleSystem
from rendering.renderer import Renderer
from tracking.hand_tracker import HandTracker
from tracking.landmarks import INDEX_MCP, INDEX_TIP, MIDDLE_MCP, PINKY_MCP, WRIST
from ui.main_window import UIState
from utils.logger import setup_logging
from utils.scores import BestScore
from utils.sounds import SoundKit

logger = logging.getLogger(__name__)

STRETCH_REF_PX = 430.0
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
    camera = Camera(config.CAMERA_INDEX, config.CAMERA_WIDTH,
                    config.CAMERA_HEIGHT)
    state.camera_active = camera.start()

    tracker = HandTracker(config.SMOOTHING_FACTOR, max_hands=2,
                          process_width=config.HAND_PROCESS_WIDTH,
                          min_detection_confidence=config.HAND_MIN_DETECTION_CONFIDENCE,
                          min_tracking_confidence=config.HAND_MIN_TRACKING_CONFIDENCE,
                          landmark_smoothing=config.HAND_LANDMARK_SMOOTHING,
                          enhance_contrast=config.HAND_ENHANCE_CONTRAST)
    motions = [MotionTracker(config.SMOOTHING_FACTOR),
               MotionTracker(config.SMOOTHING_FACTOR)]
    trails = [Trail(config.TRAIL_LENGTH), Trail(config.TRAIL_LENGTH)]
    stabs = [PoseStabilizer(), PoseStabilizer()]
    galaxy = Galaxy()
    renderer = Renderer(1280, 720)
    starfield = Starfield(renderer.width, renderer.height)
    lasers = LaserSystem(config.LASER_SPEED, config.LASER_COOLDOWN)
    shower = MeteorShower()
    debris = ParticleSystem(400)
    shockwaves = Shockwaves()
    sounds = SoundKit(config.SOUND_ENABLED)
    score = 0
    best = BestScore()
    best_banner_until = 0.0
    best_persist_until = 0.0
    comets_destroyed = 0
    streak = 0
    streak_until = 0.0
    shake = 0.0
    clock = pygame.time.Clock()

    w, h = renderer.width, renderer.height
    swipe_display = None
    swipe_display_until = 0.0
    start_time = time.monotonic()

    while state.running:
        dt = max(clock.tick(config.TARGET_FPS) / 1000.0, 1e-3)
        elapsed = time.monotonic() - start_time
        fps = 1.0 / dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.running = False

        hands = []
        last_frame = None
        if camera.active:
            ok, frame = camera.read()
            if ok:
                last_frame = frame
                hands = tracker.process(frame)[:2]
            else:
                logger.warning("Frame grab failed.")

        best_gesture = GestureType.UNKNOWN
        best_confidence = 0.0
        palm_screen = None
        per_hand = []

        for i, hand in enumerate(hands):
            if i >= len(stabs):
                break
            landmarks, palm, label = hand
            raw_g, raw_c = detect_pose(landmarks, config.GESTURE_SENSITIVITY)
            g, c = stabs[i].update(raw_g, raw_c)
            open_count = sum(1 for open_ in finger_states(landmarks).values() if open_)
            swipe = motions[i].update(palm)
            if swipe is not None:
                swipe_display = swipe
                swipe_display_until = time.monotonic() + 0.6
                galaxy.fling(3.5)
            trails[i].push(palm)
            if g == GestureType.POINT:
                tip = landmarks[INDEX_TIP]
                base = landmarks[6]
                angle = math.atan2(tip.y - base.y, tip.x - base.x)
                if lasers.fire((tip.x * w, tip.y * h), angle, time.monotonic()):
                    sounds.shoot()
            per_hand.append((landmarks, palm, g, c, open_count, label))
            if g != GestureType.UNKNOWN and (best_gesture == GestureType.UNKNOWN
                                              or c > best_confidence):
                best_gesture, best_confidence = g, c

        for i in range(2):
            if i >= len(hands):
                motions[i].reset()
                stabs[i].reset()
                while trails[i].points:
                    trails[i].points.pop(0)

        hand1 = per_hand[0] if len(per_hand) >= 1 else None
        hand2 = per_hand[1] if len(per_hand) >= 2 else None

        if hand1 is not None:
            landmarks1, palm1, label1 = hand1[0], hand1[1], hand1[5]
            yaw, tilt = hand_orientation(landmarks1, label1)
            galaxy.set_orientation(yaw, tilt)
            galaxy.set_zoom(0.75 + (hand_scale(landmarks1) - 0.06) * 2.6)
            palm_screen = (palm1[0] * w, palm1[1] * h)
        else:
            galaxy.set_orientation(DEFAULT_YAW, DEFAULT_TILT)
            galaxy.set_zoom(1.0)

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
                ratio = pinch_ratio(landmarks2)
                limit = (PINCH_RATIO_RELEASE if galaxy.grabbed is not None
                         else PINCH_RATIO)
                if ratio < limit:
                    if galaxy.grabbed is None:
                        if galaxy.grab(pp_screen):
                            sounds.grab()
                            shockwaves.spawn(pp_screen[0], pp_screen[1],
                                             (130, 255, 180), growth=340,
                                             life=0.35)
                    else:
                        galaxy.drag(pp_screen)
                else:
                    galaxy.release()
            else:
                galaxy.release()
                galaxy.set_stretch(0.85)

        galaxy_anchor = (w / 2.0, h / 2.0)
        warping = any(entry[2] == GestureType.GUN for entry in per_hand)
        speed_k = config.TIME_WARP_FACTOR if warping else 1.0
        world_dt = dt * speed_k
        galaxy.update(world_dt, effective_gesture)
        starfield.update(dt)
        shower.update(world_dt, w, h)
        if shower.just_started:
            sounds.shower()
            shower.just_started = False
        shake *= math.exp(-7.0 * dt)
        if shake < 0.3:
            shake = 0.0

        renderer.draw_frame(last_frame, dim=140)
        starfield.draw(renderer.surface, galaxy.yaw)
        if shake > 0.0:
            ox = random.uniform(-shake, shake)
            oy = random.uniform(-shake, shake)
            galaxy.draw(renderer.surface, (galaxy_anchor[0] + ox,
                                           galaxy_anchor[1] + oy), elapsed)
        else:
            galaxy.draw(renderer.surface, galaxy_anchor, elapsed)
        lasers.update(world_dt)
        now = time.monotonic()
        hit_any = False
        for shot in lasers.shots:
            hits = galaxy.blast((shot["x"], shot["y"]))
            asteroids_hit = hits["asteroids"]
            comets_hit = hits["comets"]
            if not asteroids_hit and not comets_hit:
                continue
            hit_any = True
            if streak <= 0 or now > streak_until:
                streak = 1
            else:
                streak = min(streak + 1, 20)
            streak_until = now + 3.0
            debris.spawn_one(shot["x"], shot["y"], vx=0, vy=0, size=18,
                             max_life=0.16, color=(255, 250, 210))
            for a in asteroids_hit:
                sx, sy = a.get("screen", (shot["x"], shot["y"]))
                score += streak
                shockwaves.spawn(sx, sy, (255, 215, 140), growth=380)
                for _ in range(18):
                    ang = random.uniform(0, math.tau)
                    sp = random.uniform(30, 220)
                    debris.spawn_one(
                        sx, sy, vx=math.cos(ang) * sp, vy=math.sin(ang) * sp,
                        size=random.uniform(1.5, 3.5),
                        max_life=random.uniform(0.4, 0.9),
                        color=(215, 155, 95))
            for c in comets_hit:
                sx, sy = c.get("screen", (shot["x"], shot["y"]))
                comets_destroyed += 1
                score += 5 + streak
                shake = max(shake, 8.0)
                renderer.cue_flash(90, (150, 215, 255))
                sounds.comet()
                shockwaves.spawn(sx, sy, (140, 225, 255), growth=700, life=0.55)
                debris.spawn_one(sx, sy, vx=0, vy=0, size=26,
                                 max_life=0.25, color=(255, 255, 240))
                for _ in range(40):
                    ang = random.uniform(0, math.tau)
                    sp = random.uniform(40, 300)
                    debris.spawn_one(
                        sx, sy, vx=math.cos(ang) * sp, vy=math.sin(ang) * sp,
                        size=random.uniform(1.0, 3.0),
                        max_life=random.uniform(0.5, 1.1),
                        color=(160, 225, 255))
        if hit_any:
            sounds.hit()
            renderer.cue_flash(34, (255, 220, 150))
        for shot in lasers.shots:
            meteors_hit = shower.hit((shot["x"], shot["y"]))
            if meteors_hit:
                sounds.hit()
                renderer.cue_flash(40, (255, 230, 180))
                for m in meteors_hit:
                    score += 2
                    shockwaves.spawn(m["x"], m["y"], (255, 170, 110), growth=320)
                    debris.spawn_one(m["x"], m["y"], vx=0, vy=0, size=14,
                                     max_life=0.15, color=(255, 245, 220))
                    for _ in range(14):
                        ang = random.uniform(0, math.tau)
                        sp = random.uniform(25, 180)
                        debris.spawn_one(
                            m["x"], m["y"], vx=math.cos(ang) * sp,
                            vy=math.sin(ang) * sp,
                            size=random.uniform(1.5, 3.0),
                            max_life=random.uniform(0.3, 0.7),
                            color=(255, 180, 120))
        lasers.draw(renderer.surface)
        shower.draw(renderer.surface)
        shockwaves.update(world_dt)
        shockwaves.draw(renderer.surface)
        if score > best.value and now >= best_persist_until:
            if best.update(score):
                best_banner_until = now + 4.0
            best_persist_until = now + 1.0
        renderer.draw_particles(debris)
        debris.update(world_dt)
        renderer.decay_flash(dt)

        gesture_colors = {
            "OPEN_PALM": (120, 230, 160),
            "FIST": (255, 150, 110),
            "PINCH": (255, 215, 120),
            "POINT": (130, 230, 255),
            "GUN": (150, 140, 255),
            "UNKNOWN": (175, 185, 205),
        }
        gcolor = gesture_colors.get(state.gesture, (150, 195, 255))
        rows = [
            ("kv", "Gesture", state.gesture, gcolor),
            ("bar", "Confidence", state.confidence, (80, 145, 255)),
            ("kv", "Time", f"{(1.0 if not warping else config.TIME_WARP_FACTOR):.2f}x", (160, 150, 255)),
            ("kv", "Stretch", f"{galaxy.stretch:.2f}x", (205, 215, 240)),
            ("kv", "Zoom", f"{galaxy.zoom:.2f}x", (180, 215, 130)),
            ("kv", "Score", f"{score}", (255, 200, 130)),
            ("kv", "Best", f"{best.value}", (255, 225, 160)),
            ("kv", "Comets", f"{comets_destroyed}", (150, 215, 255)) if comets_destroyed
            else None,
            ("kv", "FPS", f"{fps:.0f} / {config.TARGET_FPS}", (140, 190, 160)),
        ]
        if streak >= 2 and now <= streak_until:
            rows.append(("header", f"STREAK x{streak}", (255, 120, 90)))
        if shower.active > 0:
            rows.append(("header", "METEOR SHOWER!", (255, 165, 90)))
        if warping:
            rows.append(("header", "TIME WARP", (150, 140, 255)))
        if now < best_banner_until:
            rows.append(("header", "NEW BEST!", (255, 225, 140)))
        rows = [r for r in rows if r is not None]
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
            rows.append(("header",
                         "CAMERA OFFLINE" if not camera.active else "NO HAND DETECTED",
                         (255, 170, 110)))
            rows.append(("small",
                         "Camera is disconnected" if not camera.active
                         else "Show a hand to the camera", (170, 180, 200)))
        hint = ("POINT = SHOOT   |   GUN = TIME WARP   |   PINCH = GRAB   |   "
                "TWO HANDS = STRETCH   |   HAND CLOSER = ZOOM   |   TWIST = ROTATE   |   "
                "SWIPE = FLING   |   FIST = COLLAPSE")
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
