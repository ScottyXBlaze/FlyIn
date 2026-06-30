# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    info.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:28:39 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:43:49 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the Info model to use for the rendering."""

import os

import pygame

from ...models import DroneNetwork, Hub
from ..utils import GlobalParameters, SpriteConverter


class InfoSprite(pygame.sprite.Sprite):
    """Basic Information sprite.

    Attributes:
        frames: Every frame of the image.
        frame_size: The size of each frame.
        screen: The screen size.
        image: The actual sprite.
        drone_network: The DroneNetwork class.
        rect: The rect of the sprite
    """

    def __init__(
        self,
        sprite_name: str,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
    ) -> None:
        """Everything starts here.

        Args:
            sprite_name: The name of the sprite file.
            drone_network: The DroneNetwork class.
        """
        super().__init__()
        self._frames = SpriteConverter().convert_sprite(
            pygame.image.load(sprite_name),
            (3, 3),
        )
        self._frame_size = self._frames[0].size
        self._screen = pygame.display.get_surface()
        if self._screen is None:
            return
        self.image = pygame.Surface(
            (self._screen.size[0] - 192, 128)
        ).convert_alpha()
        self.image.fill((0, 0, 0, 10))

        self._font_name = os.path.join(
            GlobalParameters.PATH, "assets", "font", "JetBrainsMono.ttf"
        )
        self._font = pygame.font.Font(self._font_name, 15)

        self._drone_network = drone_network
        self._heuristic_value = heuristic_value
        self.rect = self.image.get_frect(
            center=(self._screen.size[0] // 2, 68)
        )
        self._build_info((self._screen.size[0] - 192, 128))

    def _build_info(self, size: tuple[int, int]) -> None:
        """Build the info bubble sprite.

        Args:
            size: The size of the sprite.
        """
        if self.image is None:
            return
        for row in range(0, size[0], self._frame_size[0]):
            for col in range(0, size[1], self._frame_size[1]):
                if col == 0 and row == 0:
                    self.image.blit(self._frames[0], (row, col))
                elif row == 0 and col >= size[1] - self._frame_size[1]:
                    self.image.blit(self._frames[2], (row, col))
                elif (
                    col >= size[1] - self._frame_size[1]
                    and row >= size[0] - self._frame_size[0]
                ):
                    pass
                elif col == 0 and row >= size[0] - self._frame_size[0]:
                    pass
                elif col == 0:
                    self.image.blit(self._frames[3], (row, col))
                elif col >= size[1] - self._frame_size[1]:
                    self.image.blit(self._frames[5], (row, col))
                elif row == 0:
                    self.image.blit(self._frames[1], (row, col))
                elif row >= size[0] - self._frame_size[0]:
                    self.image.blit(self._frames[7], (row, col))
                else:
                    self.image.blit(self._frames[4], (row, col))
        # Always print the right one
        self.image.blit(
            self._frames[6], self._frames[6].get_frect(topright=(size[0], 0))
        )
        self.image.blit(
            self._frames[8], self._frames[8].get_frect(bottomright=(size))
        )

    def draw_hub_tooltip(self, hub: Hub | None) -> None:
        """Draw the information in the sprite.

        Args:
            hub: The hub to show.
        """
        if self._screen is None:
            return
        self._build_info((self._screen.size[0] - 192, 128))
        real_hub = hub
        if not real_hub:
            return
        connections = ", ".join(
            self._drone_network.connections.get(real_hub.name, {})
        )
        if len(connections) > 88:
            connections = "Too much to show..."
        lines = [
            f"Name: {real_hub.name}",
            f"Pos: x:{real_hub.x} y:{real_hub.y}",
            f"ZoneType: {real_hub.metadata.zone.name.capitalize()}",
            f"Color: {real_hub.metadata.color.capitalize()}",
            f"Max Drone for hub: {real_hub.metadata.max_drones}",
            f"Current Drone: {real_hub.current_drone}",
            f"Total drone: {self._drone_network.nb_drones}",
            f"Connected to: {connections}",
            f"H value: {self._heuristic_value.get(real_hub.name)}",
        ]

        text_surfaces = [
            self._font.render(line, True, (255, 255, 255)) for line in lines
        ]
        if self.image is None:
            return
        image_size = self.image.get_size()
        position_x = [i for i in range(25, image_size[0], image_size[0] // 3)]
        position_y = [i for i in range(20, image_size[1], image_size[1] // 4)]

        # Print every text in their position
        self.image.blit(text_surfaces[0], (position_x[0], position_y[0]))
        self.image.blit(text_surfaces[1], (position_x[0], position_y[1]))
        self.image.blit(text_surfaces[2], (position_x[1], position_y[0]))
        self.image.blit(text_surfaces[3], (position_x[1], position_y[1]))
        self.image.blit(text_surfaces[4], (position_x[2], position_y[1]))
        self.image.blit(text_surfaces[6], (position_x[2], position_y[0]))
        self.image.blit(text_surfaces[7], (position_x[0], position_y[2]))
