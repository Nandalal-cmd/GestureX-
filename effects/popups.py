import pygame


class Popups:
    """Floating score/feedback text that rises and fades."""

    def __init__(self, max_items: int = 48):
        self._items = []
        self.max_items = max_items
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 22, bold=True)
        return self._font

    def spawn(self, x, y, text, color=(255, 220, 150)):
        if len(self._items) >= self.max_items:
            self._items.pop(0)
        self._items.append({
            "x": float(x), "y": float(y), "text": str(text),
            "color": color, "life": 0.9, "age": 0.0,
        })

    def update(self, dt):
        for it in self._items:
            it["age"] += dt
            it["y"] -= 46.0 * dt
        self._items = [it for it in self._items if it["age"] < it["life"]]

    def draw(self, surface):
        if not self._items:
            return
        font = self._get_font()
        for it in self._items:
            k = max(0.0, 1.0 - it["age"] / it["life"])
            alpha = int(255 * k)
            text = font.render(it["text"], True, it["color"])
            text.set_alpha(alpha)
            surface.blit(text, (int(it["x"]) - text.get_width() // 2,
                                int(it["y"])))

    def reset(self):
        self._items = []
