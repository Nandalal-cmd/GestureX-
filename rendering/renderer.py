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
        """rows: list of tuples describing the HUD content:
        ("header", text, color)
        ("kv", label, value, value_color)
        ("bar", label, pct, color)
        ("fingers", label, open_count, total)
        ("small", text, color)
        """
        pad = 14
        inner_w = width - pad * 2
        row_h = {"header": 30, "kv": 26, "bar": 34, "fingers": 30, "small": 19}
        title_h = 46
        height = title_h + sum(row_h[r[0]] for r in rows) + pad

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 14, 26, 220), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (66, 84, 124, 230), panel.get_rect(), 1, border_radius=12)
        pygame.draw.rect(panel, (70, 130, 255, 255), (0, 0, width, 3), border_radius=1)

        title = self.title_font.render("GESTURE FX", True, (235, 240, 250))
        panel.blit(title, (pad, 10))
        sub = self.small_font.render("solar system controller", True, (110, 150, 220))
        panel.blit(sub, (width - pad - sub.get_width(), 16))
        pygame.draw.line(panel, (58, 74, 110), (pad, title_h - 6),
                         (width - pad, title_h - 6), 1)

        cy = title_h
        for row in rows:
            kind = row[0]
            if kind == "header":
                _, text, color = row
                panel.blit(self.label_font.render(text, True, color), (pad, cy + 4))
                pygame.draw.line(panel, (50, 62, 92), (pad, cy + 26),
                                 (width - pad, cy + 26), 1)
                cy += row_h[kind]
            elif kind == "kv":
                _, label, value, color = row
                panel.blit(self.label_font.render(label, True, (150, 160, 185)), (pad, cy + 3))
                v = self.font.render(str(value), True, color)
                panel.blit(v, (width - pad - v.get_width(), cy + 1))
                cy += row_h[kind]
            elif kind == "bar":
                _, label, pct, color = row
                panel.blit(self.label_font.render(label, True, (150, 160, 185)), (pad, cy + 4))
                bx, by, bw, bh = pad + 110, cy + 8, inner_w - 110 - 44, 12
                pygame.draw.rect(panel, (30, 38, 58), (bx, by, bw, bh), border_radius=6)
                fill_w = int(bw * max(0.0, min(1.0, pct)))
                if fill_w > 0:
                    pygame.draw.rect(panel, color, (bx, by, fill_w, bh), border_radius=6)
                pct_txt = self.small_font.render(f"{int(pct * 100)}%", True, (210, 218, 235))
                panel.blit(pct_txt, (width - pad - pct_txt.get_width(), cy + 4))
                cy += row_h[kind]
            elif kind == "fingers":
                _, label, open_count, total = row
                panel.blit(self.label_font.render(label, True, (150, 160, 185)), (pad, cy + 5))
                dx = pad + 110
                for i in range(total):
                    filled = i < open_count
                    color = (90, 220, 150) if filled else (44, 54, 78)
                    pygame.draw.circle(panel, color, (dx + i * 20, cy + 13), 7)
                    if filled:
                        pygame.draw.circle(panel, (220, 255, 238),
                                           (dx + i * 20, cy + 13), 7, 1)
                cnt = self.label_font.render(f"{open_count}/{total}", True, (220, 228, 245))
                panel.blit(cnt, (width - pad - cnt.get_width(), cy + 5))
                cy += row_h[kind]
            elif kind == "small":
                _, text, color = row
                panel.blit(self.small_font.render(text, True, color), (pad, cy + 3))
                cy += row_h[kind]

        self.surface.blit(panel, (x, y))

    def present(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()
