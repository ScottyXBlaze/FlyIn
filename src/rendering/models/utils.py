# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    utils.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:29:35 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:43:47 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contains utility class to use for the rendering."""

import sys

import pygame

from typing import Any, override
from ..utils import GlobalParameters
from ...models import Hub
from . import DroneSprite


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
        self.offset.x = -(target_pos[0] - GlobalParameters.WINDOWWIDTH // 2)
        self.offset.y = -(target_pos[1] - GlobalParameters.WINDOWHEIGHT // 2)

        hub_layout = [
            sprite
            for sprite in self
            if not hasattr(sprite, "_connection")
            and not hasattr(sprite, "drone_id")
        ]
        connection_layout = [
            sprite
            for sprite in self
            if hasattr(sprite, "_connection")
            and not hasattr(sprite, "drone_id")
        ]

        drone_layout = [
            sprite for sprite in self if hasattr(sprite, "drone_id")
        ]

        if self.display_surface is None:
            sys.exit(1)

        for layout in [
            connection_layout,
            hub_layout,
            drone_layout,
        ]:
            for sprite in layout:
                if isinstance(
                    sprite.rect, pygame.Rect | pygame.FRect
                ) and isinstance(sprite.image, pygame.Surface):
                    draw_rect = sprite.rect.move(self.offset.x, self.offset.y)
                    _ = self.display_surface.blit(
                        sprite.image,
                        (int(draw_rect.x), int(draw_rect.y)),
                    )

    @override
    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update sprites while passing delta time only to drones."""
        dt = args[0] if args else kwargs.get("dt")
        for sprite in self.sprites():
            if isinstance(sprite, DroneSprite):
                sprite.update(dt if dt is not None else 0.0)
            else:
                sprite.update()


class Camera:
    """Handle the camera for the screen."""

    def __init__(self) -> None:
        """Everything starts here."""
        # Position
        self._camera_x = 0
        self._camera_y = 0

        # Usefull variable
        self._draging = False
        self._last_mouse_pos = (0, 0)
        self._bound = [0, 0, 0, 0]

    def handle_camera(self) -> None:
        """Handle camera to not go too far."""
        self._camera_y = min(self._bound[1], self._camera_y)
        self._camera_y = max(self._bound[3], self._camera_y)
        self._camera_x = min(self._bound[0], self._camera_x)
        self._camera_x = max(self._bound[2], self._camera_x)

    def check_bound(self, hubs: dict[str, Hub]) -> list[int]:
        """
        Check the limit of the camera to no go too to far.

        Args:
            hubs (dict[str): hubs to see their coordonates.
            Hub (Any): Description of Hub.

        Returns:
            list: Maximum and Minimum value for the camera.
        """
        minimum_x = min(hubs.values(), key=lambda x: x.x).x * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        )
        minimum_y = min(hubs.values(), key=lambda x: x.y).y * (
            GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE
        )
        maximum_x = max(hubs.values(), key=lambda x: x.x).x * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        )
        maximum_y = max(hubs.values(), key=lambda x: x.y).y * (
            GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE
        )

        return [maximum_x, maximum_y, minimum_x, minimum_y]
