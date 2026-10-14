import math

import numpy as np
import pygame


class SoundKit:
    """Tiny synthesized one-shot sound effects (no audio assets needed)."""

    SAMPLE_RATE = 44100

    def __init__(self, enabled: bool = True):
        self.enabled = False
        if enabled:
            if self._init_mixer():
                try:
                    self._build()
                    self.enabled = True
                except Exception:
                    self.enabled = False

    def _init_mixer(self) -> bool:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.quit()
                pygame.mixer.init(self.SAMPLE_RATE, -16, 1, 512)
            return True
        except Exception:
            return False

    def _tone(self, f0, f1, dur, vol=0.35, shape="sine"):
        n = int(self.SAMPLE_RATE * dur)
        t = np.arange(n) / self.SAMPLE_RATE
        freq = np.linspace(f0, f1, n)
        phase = np.cumsum(2 * math.pi * freq / self.SAMPLE_RATE)
        if shape == "sine":
            wave = np.sin(phase)
        elif shape == "square":
            wave = np.sign(np.sin(phase))
        else:
            wave = np.clip(np.sin(phase) * 1.6, -1.0, 1.0)
        fade = np.minimum(t / 0.01, (dur - t) / 0.01).clip(0, 1)
        wave = (wave * fade * vol)
        return wave.astype(np.float32)

    def _build(self):
        self._shoot = pygame.sndarray.make_sound(
            np.asarray(self._tone(1200, 900, 0.06, 0.25, "square") * 32000,
                       dtype=np.int16))
        self._hit = pygame.sndarray.make_sound(
            np.asarray(self._tone(620, 160, 0.14, 0.4, "saw") * 32000,
                       dtype=np.int16))
        self._grab = pygame.sndarray.make_sound(
            np.asarray(self._tone(740, 1180, 0.16, 0.3, "sine") * 32000,
                       dtype=np.int16))
        self._comet = pygame.sndarray.make_sound(
            np.asarray(self._tone(420, 140, 0.3, 0.45, "sine") * 32000,
                       dtype=np.int16))
        self._shower = pygame.sndarray.make_sound(
            np.asarray(self._tone(220, 1500, 0.8, 0.16, "saw") * 32000,
                       dtype=np.int16))

    def shoot(self):
        if self.enabled and hasattr(self, "_shoot"):
            self._shoot.play()

    def hit(self):
        if self.enabled and hasattr(self, "_hit"):
            self._hit.play()

    def grab(self):
        if self.enabled and hasattr(self, "_grab"):
            self._grab.play()

    def comet(self):
        if self.enabled and hasattr(self, "_comet"):
            self._comet.play()

    def shower(self):
        if self.enabled and hasattr(self, "_shower"):
            self._shower.play()
