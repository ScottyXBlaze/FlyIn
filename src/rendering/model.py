import pygame


class Drone(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.pos: list[int] = [0, 0]
        self.image = pygame.Surface((20, 20))
        self.rect = self.image.get_frect()
