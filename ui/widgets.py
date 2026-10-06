import pygame


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def draw(self, surface, font, active=False):
        bg = (50, 90, 160) if active else (40, 46, 60)
        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, (90, 100, 130), self.rect, 1, border_radius=6)
        text = font.render(self.label, True, (235, 238, 245))
        surface.blit(text, text.get_rect(center=self.rect.center))

    def hit(self, pos) -> bool:
        return self.rect.collidepoint(pos)
