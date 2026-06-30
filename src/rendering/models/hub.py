# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    hub.py                                            :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:27:20 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:43:50 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the Hub model to use for the rendering."""

import pygame
from ..utils import GlobalParameters


class HubSprite(pygame.sprite.Sprite):
    """Sprite model for everu hub."""

    def __init__(
        self,
        pos: tuple[int, int],
        color: str,
        name: str,
        sprite: pygame.Surface,
    ) -> None:
        """
        Every initialization.

        Args:
            pos (tuple[int, int]): Position of the hub.
            color (str): Color of the hub.
            name (str): Name of the Hub.
        """
        super().__init__()
        self._name = name
        self._pos: tuple[int, int] = self._transform_pos(pos)
        self.image = sprite.copy()
        self.image = pygame.transform.scale(
            self.image,
            (GlobalParameters.CELL_SIZE, GlobalParameters.CELL_SIZE),
        )
        self.rect = self.image.get_frect(topleft=self._pos)
        self._color_name = color
        self._hue = 0
        if color != "rainbow":
            self.image = self._tint_sprite(
                self.image,
                pygame.color.THECOLORS.get(color.lower(), (0, 0, 0, 0)),
            )

    @staticmethod
    def _tint_sprite(
        sprite: pygame.Surface, color: tuple[int, int, int, int]
    ) -> pygame.Surface:
        """Apply a light color tint to the drone sprite."""
        image = sprite.copy()
        tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint.fill(color)
        image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    @staticmethod
    def _transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """
        Transform the index position into a real position in the screen.

        Args:
            pos (tuple[int, int]):  Original position of the hub.
        Returns:
            tuple: The transformed position.
        """
        return pos[0] * (
            GlobalParameters.CELL_SIZE + GlobalParameters.OFFSET[0]
        ), pos[1] * (GlobalParameters.CELL_SIZE + GlobalParameters.OFFSET[1])

    def is_hovered(self, mouse_world: tuple[int, int]) -> bool:
        """
        Check if the mouse is in the hub.

        Args:
            mouse_world (tuple[int, int]): The position of the mouse.
        """
        world_x = self._pos[0]
        world_y = self._pos[1]

        world_rect = pygame.Rect(
            0, 0, GlobalParameters.CELL_SIZE, GlobalParameters.CELL_SIZE
        )
        world_rect.topleft = (world_x, world_y)

        return world_rect.collidepoint(mouse_world)

    def update(self) -> None:
        """Update the color of the hub."""
        if self._color_name == "rainbow":
            self.color = pygame.Color(0, 0, 0)
            self.color.hsva = (self._hue, 100, 100, 100)
            if self.image:
                self.image = self._tint_sprite(
                    self.image,
                    (self.color.r, self.color.g, self.color.b, self.color.a),
                )
            self._hue += 4
            if self._hue >= 360:
                self._hue = 0
