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
            r = max(1, int(8 * t))
            alpha = int(180 * t)
            dot = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (120, 200, 255, alpha), (r, r), r)
            self.surface.blit(dot, (pt[0] - r, pt[1] - r))

    def draw_hand_outline(self, landmarks):
        if landmarks is None:
            return
        pts = [(int(lm.x * self.width), int(lm.y * self.height)) for lm in landmarks]
        for a, b in HAND_CONNECTIONS:
            pygame.draw.line(self.surface, (90, 255, 160), pts[a], pts[b], 2)
        for pt in pts:
            pygame.draw.circle(self.surface, (230, 255, 240), pt, 3)

    def draw_hud(self, lines):
        x, y = 20, 20
        self.surface.blit(self.big_font.render("GestureFX", True, (230, 235, 245)), (x, y))
        y += 40
        for line in lines:
            self.surface.blit(self.font.render(line, True, (170, 180, 200)), (x, y))
            y += 24

    def present(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()
