# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    connection.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:23:07 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:43:49 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the Connection model to use for the rendering."""

import pygame

from ...models import Hub, Connection
from ..utils import GlobalParameters


class ConnectionSprite(pygame.sprite.Sprite):
    """Sprite model for every connection."""

    def __init__(self, hub1: Hub, hub2: Hub, connection: Connection) -> None:
        """
        Every initialization starts here.

        Args:
            hub1 (Hub): The first hub for the connection.
            hub2 (Hub): The second hub for the connection.
            connection (Connection): The connection class for the two hubs.
        """
        super().__init__()

        self._hub1, self._hub2 = hub1, hub2
        self._connection = connection

        self._width = abs(hub1.x - hub2.x)
        self._height = abs(hub1.y - hub2.y)

        self._original_pos = self._transform_pos((self._width, self._height))
        self.image = pygame.Surface(
            (
                self._original_pos[0] + 10,
                self._original_pos[1] + 10,
            )
        ).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        position = self._transform_pos(
            (
                min(self._hub1.x, self._hub2.x),
                min(self._hub1.y, self._hub2.y),
            )
        )
        self.rect = self.image.get_frect(
            topleft=(
                position[0] + GlobalParameters.CELL_SIZE // 2,
                position[1] + GlobalParameters.CELL_SIZE // 2,
            ),
        )

        self._draw_line()

    @staticmethod
    def _transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """Transform the original position to match the screen."""
        return pos[0] * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        ), pos[1] * (GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE)

    def _draw_line(self) -> None:
        """Draw the Line that connect the two hub."""
        if self.image is not None:
            start_pos = (
                0 if self._hub1.x <= self._hub2.x else self._width,
                0 if self._hub1.y <= self._hub2.y else self._height,
            )
            end_pos = (
                0 if self._hub1.x >= self._hub2.x else self._width,
                0 if self._hub1.y >= self._hub2.y else self._height,
            )
            pygame.draw.line(
                self.image,
                (
                    (50 * self._connection.max_link_capacity) % 256,
                    (30 * self._connection.max_link_capacity) % 256,
                    (20 * self._connection.max_link_capacity) % 256,
                    255,
                ),
                self._transform_pos(end_pos),
                self._transform_pos(start_pos),
                self._connection.max_link_capacity * 4,
            )
