# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    groups.py                                         :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:40 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:53:40 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the class to easily have a camera."""

import sys

import pygame

from .settings import WINDOWHEIGHT, WINDOWWIDTH


class AllSprite(pygame.sprite.Group[pygame.sprite.Sprite]):
    """Sprite Group for every sprite."""

    def __init__(self) -> None:
        """Everything starts here."""
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw_sprite(self, target_pos: tuple[int | float, int | float]) -> None:
        """
        Draw every sprite in the screen.

        Args:
            target_pos (tuple[int, int]): The position of
            where to draw every sprite.
        """
        self.offset.x = -(target_pos[0] - WINDOWWIDTH // 2)
        self.offset.y = -(target_pos[1] - WINDOWHEIGHT // 2)

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
