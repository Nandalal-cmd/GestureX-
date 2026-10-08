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

FACTS = {
    "Mercury": "Diam: 4,879 km | Day: 58.6 d | Year: 88 d | Moons: 0",
    "Venus": "Diam: 12,104 km | Day: 243 d | Year: 225 d | Moons: 0",
    "Earth": "Diam: 12,742 km | Day: 24 h | Year: 365 d | Moons: 1",
    "Mars": "Diam: 6,779 km | Day: 24.6 h | Year: 687 d | Moons: 2",
    "Jupiter": "Diam: 139,820 km | Day: 9.9 h | Year: 11.9 y | Moons: 95",
    "Saturn": "Diam: 116,460 km | Day: 10.7 h | Year: 29.4 y | Moons: 146",
}

BELT_COUNT = 60
COMET_DEFS = (
    # semi-major, ecc, speed, phase offset, color
    (260, 0.62, 0.55, 1.0, (170, 230, 255)),
    (300, 0.68, 0.42, 3.7, (255, 220, 170)),
)


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
        random.seed(7)
        self.asteroids = [
            {"phase": random.uniform(0, math.tau),
             "orbit": random.uniform(214, 222),
             "speed": random.uniform(0.42, 0.55),
             "size": random.uniform(1.0, 2.6),
             "elev": random.uniform(-0.06, 0.06)}
            for _ in range(BELT_COUNT)
        ]
        self.comets = [
            {"a": a, "ecc": e, "speed": sp, "phase": off, "color": col,
             "screen": None, "z": 0.0}
            for (a, e, sp, off, col) in COMET_DEFS
        ]
        random.seed()
        self.stretch = 0.85
        self.target_stretch = 0.85
        self.collapse = 0.0
        self.spin = 0.0
        self.tilt = 0.45
        self.target_tilt = 0.45
        self.yaw = 0.0
        self.target_yaw = 0.0
        self.grabbed = None
        self.grab_pos = None
        self._font = None

    def set_orientation(self, yaw: float, tilt: float):
        self.target_yaw = max(-1.1, min(1.1, yaw))
        self.target_tilt = max(0.05, min(1.3, tilt))

    def set_stretch(self, s):
        self.target_stretch = max(0.35, min(2.4, s))

    def fling(self, amount=3.5):
        self.spin += amount

    def update(self, dt, gesture):
        k = min(1.0, dt * 5.0)
        self.stretch += (self.target_stretch - self.stretch) * k
        self.yaw += (self.target_yaw - self.yaw) * min(1.0, dt * 4.0)
        self.tilt += (self.target_tilt - self.tilt) * min(1.0, dt * 4.0)
        want = 1.0 if gesture == GestureType.FIST else 0.0
        self.collapse += (want - self.collapse) * min(1.0, dt * 6.0)
        self.spin *= math.exp(-1.8 * dt)
        for b in self.bodies:
            if b is self.grabbed:
                continue
            drift = b.speed * BASE_SPEED * (1.0 - 0.35 * self.collapse)
            b.phase += (drift + self.spin * 0.6) * dt
            b.moon_phase += 2.2 * dt
        for a in self.asteroids:
            a["phase"] += a["speed"] * BASE_SPEED * dt * (1.0 - 0.35 * self.collapse)
        for c in self.comets:
            c["phase"] += c["speed"] * dt * (1.0 - 0.35 * self.collapse)

    def _project_point(self, x, y, elev):
        y2 = y * math.cos(elev)
        z2 = y * math.sin(elev)
        Y = y2 * math.cos(self.tilt) - z2 * math.sin(self.tilt)
        Z = y2 * math.sin(self.tilt) + z2 * math.cos(self.tilt)
        x2 = x * math.cos(self.yaw) - Z * math.sin(self.yaw)
        Z2 = x * math.sin(self.yaw) + Z * math.cos(self.yaw)
        scale = self.FOCAL / (self.FOCAL + Z2)
        return x2 * scale, Y * scale, scale, Z2

    def _project(self, body, center):
        r = body.radius_at(self.stretch, self.collapse)
        x, y, scale, z = self._project_point(
            math.cos(body.phase) * r, math.sin(body.phase) * r, body.elev)
        return center[0] + x, center[1] + y, scale, z

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
        base_r = body.orbit * self.stretch * (1.0 - 0.85 * self.collapse)
        for i in range(segments):
            phase = i * math.tau / segments
            r = base_r * (1.0 + body.ecc * math.cos(phase))
            x, y, _, _ = self._project_point(
                math.cos(phase) * r, math.sin(phase) * r, body.elev)
            pts.append((center[0] + x, center[1] + y))
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
        if int(r) >= 3:
            pygame.draw.circle(surface, dark, (int(x), int(y)), int(r), 1)

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
        for b in self.bodies:
            x, y, scale, z = self._project(b, center)
            b.screen = (x, y)
            b.scale = scale
            b.z = z

        for b in self.bodies:
            pts = self._orbit_path(b, center)
            if len(pts) > 2:
                pygame.draw.lines(surface, (70, 80, 105), True, pts, 1)

        items = []

        stretch_k = self.stretch * (1.0 - 0.85 * self.collapse)
        for a in self.asteroids:
            r = a["orbit"] * stretch_k
            x, y, scale, z = self._project_point(
                math.cos(a["phase"]) * r, math.sin(a["phase"]) * r, a["elev"])
            pos = (center[0] + x, center[1] + y)
            sz = max(1, int(a["size"] * scale))
            items.append((z, self._draw_rock, surface, pos, sz))

        for c in self.comets:
            e = c["ecc"]
            r = c["a"] * (1.0 - e * e) / (1.0 + e * math.cos(c["phase"]))
            r *= stretch_k
            x, y, scale, z = self._project_point(
                math.cos(c["phase"]) * r, math.sin(c["phase"]) * r, 0.02)
            head = (center[0] + x, center[1] + y)
            c["screen"] = head
            c["z"] = z
            items.append((z, self._draw_comet, surface, c, head, scale,
                          stretch_k, center))

        for b in self.bodies:
            if b is not self.grabbed:
                items.append((b.z, self._draw_planet_body, surface, b))

        for z, fn, *args in sorted(items, key=lambda item: -item[0]):
            fn(*args)

        self._draw_sun(surface, center, time_s)
        self._draw_labels(surface)

        if self.grabbed is not None and self.grab_pos is not None:
            self._draw_planet(surface, self.grabbed,
                              self.grab_pos[0], self.grab_pos[1], 1.4)
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(self.grab_pos[0]), int(self.grab_pos[1])),
                               max(5, int(self.grabbed.size * 1.4)), 2)

    @staticmethod
    def _draw_rock(surface, pos, size):
        pygame.draw.circle(surface, (130, 128, 122),
                           (int(pos[0]), int(pos[1])), size)

    def _draw_planet_body(self, surface, b):
        x, y = b.screen
        if b.special == "earth" and self.stretch * (1.0 - 0.85 * self.collapse) > 0.5:
            mr = 22.0 * b.scale
            mx = x + math.cos(b.moon_phase) * mr
            my = y + math.sin(b.moon_phase) * mr * 0.45
            ms = max(3, int(3.5 * b.scale))
            pygame.draw.circle(surface, (185, 185, 180), (int(mx), int(my)), ms)
        self._draw_planet(surface, b, x, y, b.scale)

    def _draw_comet(self, surface, c, head, scale, stretch_k, center):
        e = c["ecc"]
        for k in range(14, 0, -1):
            phase = c["phase"] - k * 0.05
            r = c["a"] * (1.0 - e * e) / (1.0 + e * math.cos(phase))
            r *= stretch_k
            x, y, _, _ = self._project_point(
                math.cos(phase) * r, math.sin(phase) * r, 0.02)
            pos = (center[0] + x, center[1] + y)
            t = 1.0 - k / 14.0
            col = tuple(int(ch * (0.25 + 0.75 * t)) for ch in c["color"])
            sz = max(1, int(3 * scale * t))
            pygame.draw.circle(surface, col, (int(pos[0]), int(pos[1])), sz)
        pygame.draw.circle(surface, c["color"], (int(head[0]), int(head[1])),
                           max(2, int(3 * scale)))
        draw_glow(surface, head, c["color"], 7 * scale, alpha=170)

    def _draw_labels(self, surface):
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 14, bold=True)
        for b in self.bodies:
            if b.screen is None or b is self.grabbed:
                continue
            x, y = b.screen
            front = b.z <= 0
            color = (225, 230, 245) if front else (130, 135, 155)
            text = self._font.render(b.name, True, color)
            tw, th = text.get_size()
            px = int(x + b.size * b.scale + 8)
            py = int(y - th // 2)
            pill = pygame.Rect(px - 5, py - 3, tw + 10, th + 6)
            bg = (8, 10, 20, 150 if front else 90)
            pill_surf = pygame.Surface(pill.size, pygame.SRCALPHA)
            pygame.draw.rect(pill_surf, bg, pill_surf.get_rect(), border_radius=6)
            if front:
                pygame.draw.rect(pill_surf, (80, 100, 145, 180),
                                 pill_surf.get_rect(), 1, border_radius=6)
            surface.blit(pill_surf, pill.topleft)
            surface.blit(text, (px, py))
