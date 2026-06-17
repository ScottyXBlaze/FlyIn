# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    groups.py                                         :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:40 by nyramana         #+#    #+#              #
#    Updated: 2026/06/16 10:55:41 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the class to easily have a camera."""

import sys
from typing import Any

import pygame

from .drone import Drone
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
            sprite
            for sprite in self
            if not hasattr(sprite, "connection")
            and not hasattr(sprite, "drone_id")
        ]
        self.connection_layout = [
            sprite
            for sprite in self
            if hasattr(sprite, "connection")
            and not hasattr(sprite, "drone_id")
        ]

        self.drone_layout = [
            sprite for sprite in self if hasattr(sprite, "drone_id")
        ]

        if self.display_surface is None:
            sys.exit(1)

        for layout in [
            self.connection_layout,
            self.hub_layout,
            self.drone_layout,
        ]:
            for sprite in layout:
                if isinstance(
                    sprite.rect, pygame.Rect | pygame.FRect
                ) and isinstance(sprite.image, pygame.Surface):
                    draw_rect = sprite.rect.move(self.offset.x, self.offset.y)
                    self.display_surface.blit(
                        sprite.image,
                        (int(draw_rect.x), int(draw_rect.y)),
                    )

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update sprites while passing delta time only to drones."""
        dt = args[0] if args else kwargs.get("dt")
        for sprite in self.sprites():
            if isinstance(sprite, Drone):
                sprite.update(dt if dt is not None else 0.0)
            else:
                sprite.update()
