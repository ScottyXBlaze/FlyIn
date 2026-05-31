import sys

import pygame

WINDOWWIDTH, WINDOWHEIGHT = 800, 600


class AllSprite(pygame.sprite.Group[pygame.sprite.Sprite]):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(
        self,
        surface: pygame.Surface,
        bgd: pygame.Surface | None = None,
        special_flags: int = 0,
    ) -> list[pygame.FRect | pygame.Rect]:
        return super().draw(surface, bgd, special_flags)

    def draw_sprite(self, target_pos: tuple[int | float, int | float]) -> None:
        self.offset.x = -(target_pos[0] - WINDOWWIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOWHEIGHT / 2)

        self.hub_layout = [
            sprite for sprite in self if not hasattr(sprite, "connection")
        ]
        self.connection_layout = [
            sprite for sprite in self if hasattr(sprite, "connection")
        ]

        if self.display_surface is None:
            sys.exit(1)

        for layout in [self.connection_layout, self.hub_layout]:
            for sprite in sorted(
                layout,
                key=lambda sprite: (
                    sprite.rect.centery
                    if isinstance(sprite.rect, pygame.Rect | pygame.FRect)
                    else (0, 0)
                ),
            ):
                if isinstance(
                    sprite.rect, pygame.Rect | pygame.FRect
                ) and isinstance(sprite.image, pygame.Surface):
                    self.display_surface.blit(
                        sprite.image, sprite.rect.topleft + self.offset
                    )
