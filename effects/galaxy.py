import math
import random

import pygame

from gestures.gesture_types import GestureType

# name, semi-major orbit, eccentricity, size px, color, angular speed (rad/s),
# ring elevation, special — orbits use equal spacing (60 + 45 * index)
PLANET_DEFS = (
    ("Mercury", 60, 0.10, 4.5, (155, 150, 145), 2.04, 0.10, None),
    ("Venus", 105, 0.05, 9, (225, 195, 135), 1.27, 0.06, None),
    ("Earth", 150, 0.02, 10, (70, 130, 230), 1.00, 0.00, "earth"),
    ("Mars", 195, 0.07, 6.5, (205, 105, 75), 0.73, 0.05, None),
    ("Jupiter", 240, 0.04, 26, (215, 175, 135), 0.29, 0.03, "bands"),
    ("Saturn", 285, 0.05, 20, (225, 205, 155), 0.18, 0.08, "ring"),
)

BASE_SPEED = 0.45


def draw_glow(surface, pos, color, radius, alpha=200):
    d = int(radius * 2.6)
    if d < 4:
        d = 4
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha // 3), (d // 2, d // 2), d // 2)
    pygame.draw.circle(s, (*color, alpha), (d // 2, d // 2), max(1, int(radius * 0.55)))
    surface.blit(s, (int(pos[0]) - d // 2, int(pos[1]) - d // 2))


class _Planet:
    def __init__(self, name, orbit, ecc, size, color, speed, elev, special):
        self.name = name
        self.orbit = float(orbit)
        self.ecc = ecc
        self.size = size
        self.color = color
        self.speed = speed
        self.elev = elev
        self.special = special
        self.phase = 0.0
        self.moon_phase = 0.0
        self.screen = None
        self.scale = 1.0
        self.z = 0.0

    def radius_at(self, stretch, collapse):
        base = self.orbit * stretch * (1.0 - 0.85 * collapse)
        return base * (1.0 + self.ecc * math.cos(self.phase))


class Galaxy:
    FOCAL = 700.0

    def __init__(self):
        self.bodies = [_Planet(*defn) for defn in PLANET_DEFS]
        self.stretch = 1.0
        self.target_stretch = 1.0
        self.collapse = 0.0
        self.spin = 0.0
        self.tilt = 0.45
        self.grabbed = None
        self.grab_pos = None
        self.stars = [
            (random.random(), random.random(),
             random.uniform(0.7, 2.2), random.uniform(0, math.tau))
            for _ in range(150)
        ]

    def set_stretch(self, s):
        self.target_stretch = max(0.35, min(2.4, s))

    def fling(self, amount=3.5):
        self.spin += amount

    def update(self, dt, gesture):
        k = min(1.0, dt * 5.0)
        self.stretch += (self.target_stretch - self.stretch) * k
        want = 1.0 if gesture == GestureType.FIST else 0.0
        self.collapse += (want - self.collapse) * min(1.0, dt * 6.0)
        self.spin *= math.exp(-1.8 * dt)
        for b in self.bodies:
            if b is self.grabbed:
                continue
            drift = b.speed * BASE_SPEED * (1.0 - 0.35 * self.collapse)
            b.phase += (drift + self.spin * 0.6) * dt
            b.moon_phase += 2.2 * dt

    def _project(self, body, center):
        r = body.radius_at(self.stretch, self.collapse)
        p = body.phase
        x = math.cos(p) * r
        y = math.sin(p) * r
        e = body.elev
        y2 = y * math.cos(e)
        z2 = y * math.sin(e)
        Y = y2 * math.cos(self.tilt) - z2 * math.sin(self.tilt)
        Z = y2 * math.sin(self.tilt) + z2 * math.cos(self.tilt)
        scale = self.FOCAL / (self.FOCAL + Z)
        return center[0] + x * scale, center[1] + Y * scale, scale, Z

    def grab(self, pos):
        best, best_d = None, float("inf")
        for b in self.bodies:
            if b.screen is None:
                continue
            d = math.hypot(b.screen[0] - pos[0], b.screen[1] - pos[1])
            if d < best_d:
                best, best_d = b, d
        if best is not None and best_d < 95:
            self.grabbed = best
            self.grab_pos = pos
            return True
        return False

    def drag(self, pos):
        if self.grab_pos is not None:
            self.grab_pos = pos

    def release(self):
        self.grabbed = None
        self.grab_pos = None

    def _orbit_path(self, body, center):
        pts = []
        segments = 128
        for i in range(segments):
            phase = i * math.tau / segments
            r = body.orbit * self.stretch * (1.0 - 0.85 * self.collapse)
            r *= 1.0 + body.ecc * math.cos(phase)
            x = math.cos(phase) * r
            y = math.sin(phase) * r
            e = body.elev
            y2 = y * math.cos(e)
            z2 = y * math.sin(e)
            Y = y2 * math.cos(self.tilt) - z2 * math.sin(self.tilt)
            Z = y2 * math.sin(self.tilt) + z2 * math.cos(self.tilt)
            scale = self.FOCAL / (self.FOCAL + Z)
            pts.append((center[0] + x * scale, center[1] + Y * scale))
        return pts

    def _draw_planet(self, surface, body, x, y, scale):
        r = max(2, body.size * scale)
        d = int(r * 2) + 2
        tile = pygame.Surface((d, d), pygame.SRCALPHA)
        cx, cy = d // 2, d // 2
        dark = tuple(int(c * 0.55) for c in body.color)
        pygame.draw.circle(tile, dark, (cx, cy), int(r))
        light = tuple(min(255, int(c * 1.35)) for c in body.color)
        pygame.draw.circle(tile, light, (cx - int(r * 0.3), cy - int(r * 0.3)), int(r * 0.75))

        if body.special == "bands":
            band = tuple(int(c * 0.8) for c in body.color)
            for dy in (-0.55 * r, -0.15 * r, 0.3 * r):
                dx = math.sqrt(max(0.0, r * r - dy * dy)) * 0.95
                pygame.draw.line(tile, band, (cx - dx, cy + dy), (cx + dx, cy + dy), 2)
        elif body.special == "earth":
            pygame.draw.circle(tile, (90, 190, 110),
                               (cx - int(r * 0.3), cy + int(r * 0.2)), int(r * 0.4))
            pygame.draw.circle(tile, (90, 190, 110),
                               (cx + int(r * 0.35), cy - int(r * 0.35)), int(r * 0.3))
            pygame.draw.line(tile, (240, 245, 250),
                             (cx - int(r * 0.7), cy + int(r * 0.1)),
                             (cx + int(r * 0.6), cy + int(r * 0.05)), 2)

        surface.blit(tile, (int(x) - cx, int(y) - cy))

        if body.special == "ring":
            rx, ry = int(r * 1.9), int(r * 0.55)
            ring = pygame.Surface((rx * 2 + 4, ry * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(ring, (215, 195, 150, 220),
                                pygame.Rect(2, 2, rx * 2, ry * 2), 2)
            pygame.draw.ellipse(ring, (195, 175, 130, 150),
                                pygame.Rect(6, 6, rx * 2 - 8, ry * 2 - 8), 1)
            surface.blit(ring, (int(x) - rx - 2, int(y) - ry - 2))

    def _draw_sun(self, surface, center, time_s=0.0):
        pulse = 1.0 + 0.06 * math.sin(time_s * 2.0)
        flicker = 1.0 + 0.04 * math.sin(time_s * 7.3)
        r = (28 + 10 * self.collapse) * pulse * flicker
        draw_glow(surface, center, (255, 90, 30), r * 3.4, alpha=35)
        draw_glow(surface, center, (255, 140, 45), r * 2.5, alpha=55)
        draw_glow(surface, center, (255, 185, 70), r * 1.8, alpha=90)
        d = int(r * 2) + 2
        tile = pygame.Surface((d, d), pygame.SRCALPHA)
        cx, cy = d // 2, d // 2
        layers = (
            ((255, 130, 40), r),
            ((255, 175, 65), r * 0.88),
            ((255, 215, 105), r * 0.7),
            ((255, 240, 165), r * 0.48),
            ((255, 253, 238), r * 0.26),
        )
        for color, rad in layers:
            pygame.draw.circle(tile, color, (cx, cy), max(1, int(rad)))
        surface.blit(tile, (int(center[0]) - cx, int(center[1]) - cy))
        draw_glow(surface, center, (255, 245, 200), r * 1.15, alpha=80)

    def draw(self, surface, center, time_s=0.0):
        w, h = surface.get_size()
        for sx, sy, size, seed in self.stars:
            tw = 0.55 + 0.45 * math.sin(time_s * 1.6 + seed)
            c = int(150 + 105 * tw)
            pygame.draw.circle(surface, (c, c, c), (int(sx * w), int(sy * h)), max(1, int(size)))

        for b in self.bodies:
            x, y, scale, z = self._project(b, center)
            b.screen = (x, y)
            b.scale = scale
            b.z = z

        for b in self.bodies:
            pts = self._orbit_path(b, center)
            if len(pts) > 2:
                pygame.draw.lines(surface, (70, 80, 105), True, pts, 1)

        self._draw_sun(surface, center, time_s)

        ordered = sorted((b for b in self.bodies if b is not self.grabbed),
                         key=lambda b: b.z)
        for b in ordered:
            x, y = b.screen
            if b.special == "earth" and self.stretch * (1 - 0.85 * self.collapse) > 0.5:
                mr = 22.0 * b.scale
                mx = x + math.cos(b.moon_phase) * mr
                my = y + math.sin(b.moon_phase) * mr * 0.45
                ms = max(3, 3.5 * b.scale)
                pygame.draw.circle(surface, (185, 185, 180), (int(mx), int(my)), int(ms))
            self._draw_planet(surface, b, x, y, b.scale)

        if self.grabbed is not None and self.grab_pos is not None:
            self._draw_planet(surface, self.grabbed,
                              self.grab_pos[0], self.grab_pos[1], 1.4)
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(self.grab_pos[0]), int(self.grab_pos[1])),
                               max(5, int(self.grabbed.size * 1.4)), 2)
