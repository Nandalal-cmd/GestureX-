import math

import cv2
import numpy as np
import pygame

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
)


class Renderer:
    def __init__(self, width: int = 1280, height: int = 720):
        pygame.init()
        self.width = width
        self.height = height
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GestureFX")
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.label_font = pygame.font.SysFont("consolas", 17)
        self._flash_alpha = 0.0
        self._flash_color = (255, 255, 255)

    def draw_frame(self, frame_bgr, dim: int = 0):
        if frame_bgr is None:
            self.surface.fill((8, 10, 18))
            return
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (self.width, self.height))
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        self.surface.blit(surf, (0, 0))
        if dim > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, dim))
            self.surface.blit(overlay, (0, 0))

    def clear(self):
        self.surface.fill((8, 10, 18))

    def draw_particles(self, particles):
        for p in particles.alive_particles():
            color = (p.color[0], p.color[1], p.color[2], p.opacity)
            s = max(2, p.size * 2)
            spark = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.circle(spark, color, (s // 2, s // 2), s // 2)
            self.surface.blit(spark, (int(p.x) - s // 2, int(p.y) - s // 2))

    def draw_trail(self, points):
        n = len(points)
        for i, pt in enumerate(points):
            t = (i + 1) / max(n, 1)
            r = max(1, int(11 * t * t + 2))
            alpha = int(200 * t * t)
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (130, 210, 255, alpha), (r, r), r)
            if r > 4:
                pygame.draw.circle(dot, (210, 240, 255, min(255, alpha + 60)),
                                   (r, r), max(1, r // 3))
            self.surface.blit(dot, (pt[0] - r, pt[1] - r))

    def draw_hand_outline(self, landmarks):
        if landmarks is None:
            return
        pts = [(int(lm.x * self.width), int(lm.y * self.height)) for lm in landmarks]
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for a, b in HAND_CONNECTIONS:
            pygame.draw.line(glow, (70, 255, 160, 80), pts[a], pts[b], 6)
            pygame.draw.line(glow, (190, 255, 220, 235), pts[a], pts[b], 2)
        for pt in pts:
            pygame.draw.circle(glow, (70, 255, 160, 90), pt, 7)
            pygame.draw.circle(glow, (240, 255, 248, 255), pt, 3)
        self.surface.blit(glow, (0, 0))

    def render_hud(self, rows, x: int = 16, y: int = 16, width: int = 340):
        return None
    def cue_flash(self, alpha: int, color=(255, 255, 255)):
        self._flash_alpha = max(self._flash_alpha, float(alpha))
        self._flash_color = color

    def decay_flash(self, dt: float):
        self._flash_alpha *= math.exp(-14.0 * dt)
        if self._flash_alpha < 1.0:
            self._flash_alpha = 0.0

    def draw_flash(self):
        a = int(self._flash_alpha)
        if a <= 0:
            return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*self._flash_color, a))
        self.surface.blit(overlay, (0, 0))

    def present(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()
