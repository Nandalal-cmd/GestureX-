"""Pygame renderer drawing the camera feed, flame particles, and a status HUD."""

from __future__ import annotations

import logging

from effects.fire_effect import flame_color
from utils.geometry import normalized_to_screen

WINDOW_TITLE = "GestureFX — Fire"
BACKGROUND_DIM = 90
BACKGROUND_ALPHA = 1.0 - BACKGROUND_DIM / 255.0
HUD_FONT_SIZE = 20
HUD_LINE_HEIGHT = 26
HUD_MARGIN = 18


class Renderer:
    """Own the Pygame window and draw frames with additive flame particles."""

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        self._logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self._screen = None
        self._clock = None
        self._font = None
        self._overlay = None

    def start(self) -> bool:
        """Open the window, returning False instead of crashing when display setup fails."""
        try:
            import pygame

            pygame.init()
            pygame.display.set_caption(WINDOW_TITLE)
            self._screen = pygame.display.set_mode((self.width, self.height))
            self._overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self._font = pygame.font.SysFont("consolas", HUD_FONT_SIZE)
            self._clock = pygame.time.Clock()
        except Exception:
            self._logger.exception("Unable to open the render window")
            self.stop()
            return False
        return True

    @property
    def is_running(self) -> bool:
        """Return True while the window is open and no exit event has been received."""
        if self._screen is None:
            return False
        import pygame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                return False
        return True

    def draw(self, frame, system, gesture_label: str, fps: float) -> None:
        """Draw one frame: dimmed camera feed, flame particles, then the HUD."""
        import pygame

        if self._screen is None:
            return
        self._screen.blit(self._to_surface(frame), (0, 0))
        self._draw_particles(system)
        self._draw_hud(gesture_label, fps, system.active_count)

    def tick(self, target_fps: int) -> float:
        """Limit the frame rate and return the elapsed seconds for physics."""
        if self._clock is None:
            return 1.0 / max(1, target_fps)
        return self._clock.tick(target_fps) / 1000.0

    def stop(self) -> None:
        """Release Pygame resources safely."""
        try:
            import pygame

            if pygame.get_init():
                pygame.quit()
        except Exception:
            self._logger.exception("Error while shutting down the renderer")
        finally:
            self._screen = None
            self._overlay = None
            self._font = None
            self._clock = None

    def _to_surface(self, frame):
        """Convert a BGR OpenCV frame into a mirrored, dimmed Pygame surface.

        Resizing is skipped when the camera already matches the window, and the
        dim is folded into the colour conversion because a per-surface blend on a
        full-screen surface costs roughly six times as much.
        """
        import cv2
        import pygame

        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(frame, (self.width, self.height))
        mirrored = cv2.flip(frame, 1)
        dimmed = cv2.cvtColor(mirrored, cv2.COLOR_BGR2RGB)
        dimmed = cv2.convertScaleAbs(dimmed, alpha=BACKGROUND_ALPHA)
        return pygame.image.frombuffer(dimmed.tobytes(), (self.width, self.height), "RGB")

    def _draw_particles(self, system) -> None:
        """Composite live particles additively so overlapping flames glow."""
        import pygame

        if self._overlay is None:
            return
        self._overlay.fill((0, 0, 0, 0))
        drawn = 0
        for particle in system.particles:
            if not particle.is_alive:
                continue
            x, y = normalized_to_screen(particle.position, self.width, self.height, mirror=False)
            radius = max(1, round(particle.size))
            alpha = round(min(1.0, particle.opacity) * 255)
            pygame.draw.circle(self._overlay, (*flame_color(particle.life_ratio), alpha), (x, y), radius)
            drawn += 1
        if drawn:
            self._screen.blit(self._overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _draw_hud(self, gesture_label: str, fps: float, particle_count: int) -> None:
        if self._font is None or self._screen is None:
            return
        lines = (
            gesture_label,
            f"FPS: {fps:5.1f}",
            f"Particles: {particle_count}",
            f"Mode: FIRE",
            "Q or ESC to quit",
        )
        for index, text in enumerate(lines):
            surface = self._font.render(text, True, (255, 255, 255))
            self._screen.blit(surface, (HUD_MARGIN, HUD_MARGIN + index * HUD_LINE_HEIGHT))

    def __enter__(self) -> "Renderer":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()