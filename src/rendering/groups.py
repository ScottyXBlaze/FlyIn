import sys

import pygame

WINDOWWIDTH, WINDOWHEIGHT = 800, 600


class AllSprite(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        if self.display_surface is None:
            sys.exit(1)

    def draw(
        self,
        target_pos,
    ):
        self.offset.x = -(target_pos[0] - WINDOWWIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOWHEIGHT / 2)

        self.hub_layout = [
            sprite for sprite in self if not hasattr(sprite, "hub")
        ]

        if self.display_surface is None:
            sys.exit(1)

        for layout in [self.hub_layout]:
            for sprite in sorted(
                layout, key=lambda sprite: sprite.rect.centery
            ):
                self.display_surface.blit(
                    sprite.image, sprite.rect.topleft + self.offset
                )
