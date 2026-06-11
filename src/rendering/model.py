# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    model.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:42 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 18:46:25 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain every model for the rendering."""

import os

import pygame

from .. import Connection, Hub
from ..model import DroneNetwork
from .settings import CELL_SIZE, OFFSET
from .sprite_converter import SpriteConverter


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
        self.name = name
        self.pos: tuple[int, int] = self.transform_pos(pos)
        self.image = sprite.copy()
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.copy_image = self.image.copy()
        self.rect = self.image.get_frect(topleft=self.pos)
        self.color_name = color
        self.hue = 0
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
    def transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """
        Transform the index position into a real position in the screen.

        Args:
            pos (tuple[int, int]):  Original position of the hub.
        Returns:
            tuple: The transformed position.
        """
        return pos[0] * (CELL_SIZE + OFFSET[0]), pos[1] * (
            CELL_SIZE + OFFSET[1]
        )

    def is_hovered(self, mouse_world: tuple[int, int]) -> bool:
        """
        Check if the mouse is in the hub.

        Args:
            mouse_world (tuple[int, int]): The position of the mouse.
        """
        world_x = self.pos[0]
        world_y = self.pos[1]

        world_rect = pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE)
        world_rect.topleft = (world_x, world_y)

        return world_rect.collidepoint(mouse_world)

    def update(self) -> None:
        """Update the color of the hub."""
        if self.color_name == "rainbow":
            self.color = pygame.Color(0, 0, 0)
            self.color.hsva = (self.hue, 100, 100, 100)
            if self.image:
                self.image = self._tint_sprite(
                    self.copy_image,
                    (self.color.r, self.color.g, self.color.b, self.color.a),
                )
            self.hue += 4
            if self.hue >= 360:
                self.hue = 0


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

        self.hub1, self.hub2 = hub1, hub2
        self.connection = connection

        self.width = abs(hub1.x - hub2.x)
        self.height = abs(hub1.y - hub2.y)

        self.original_pos = self.transform_pos((self.width, self.height))
        self.image = pygame.Surface(
            (
                self.original_pos[0] + 10,
                self.original_pos[1] + 10,
            )
        ).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        position = self.transform_pos(
            (
                min(self.hub1.x, self.hub2.x),
                min(self.hub1.y, self.hub2.y),
            )
        )
        self.rect = self.image.get_frect(
            topleft=(
                position[0] + CELL_SIZE // 2,
                position[1] + CELL_SIZE // 2,
            ),
        )

        self.draw_line()

    @staticmethod
    def transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """Transform the original position to match the screen."""
        return pos[0] * (OFFSET[0] + CELL_SIZE), pos[1] * (
            OFFSET[0] + CELL_SIZE
        )

    def draw_line(self) -> None:
        """Draw the Line that connect the two hub."""
        if self.image is not None:
            start_pos = (
                0 if self.hub1.x <= self.hub2.x else self.width,
                0 if self.hub1.y <= self.hub2.y else self.height,
            )
            end_pos = (
                0 if self.hub1.x >= self.hub2.x else self.width,
                0 if self.hub1.y >= self.hub2.y else self.height,
            )
            pygame.draw.line(
                self.image,
                (20, 20, 20, 150),
                self.transform_pos(end_pos),
                self.transform_pos(start_pos),
                self.connection.max_link_capacity * 4,
            )


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
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.frames = SpriteConverter().convert_sprite(
            pygame.image.load(os.path.join(base_dir, "assets", sprite_name)),
            (3, 3),
        )
        self.frame_size = self.frames[0].size
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            return
        self.image = pygame.Surface(
            (self.screen.size[0] - 192, 128)
        ).convert_alpha()
        self.image.fill((0, 0, 0, 10))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.fonts = os.path.join(base_dir, "assets", "JetBrainsMono.ttf")
        self.font = pygame.font.Font(self.fonts, 15)

        self.drone_network = drone_network
        self.heuristic_value = heuristic_value
        self.rect = self.image.get_frect(center=(self.screen.size[0] // 2, 68))
        self.build_info((self.screen.size[0] - 192, 128))

    def build_info(self, size: tuple[int, int]) -> None:
        """Build the info bubble sprite.

        Args:
            size: The size of the sprite.
        """
        if self.image is None:
            return
        for row in range(0, size[0], self.frame_size[0]):
            for col in range(0, size[1], self.frame_size[1]):
                if col == 0 and row == 0:
                    self.image.blit(self.frames[0], (row, col))
                elif row == 0 and col >= size[1] - self.frame_size[1]:
                    self.image.blit(self.frames[2], (row, col))
                elif (
                    col >= size[1] - self.frame_size[1]
                    and row >= size[0] - self.frame_size[0]
                ):
                    pass
                elif col == 0 and row >= size[0] - self.frame_size[0]:
                    pass
                elif col == 0:
                    self.image.blit(self.frames[3], (row, col))
                elif col >= size[1] - self.frame_size[1]:
                    self.image.blit(self.frames[5], (row, col))
                elif row == 0:
                    self.image.blit(self.frames[1], (row, col))
                elif row >= size[0] - self.frame_size[0]:
                    self.image.blit(self.frames[7], (row, col))
                else:
                    self.image.blit(self.frames[4], (row, col))
        # Always print the right one
        self.image.blit(
            self.frames[6], self.frames[6].get_frect(topright=(size[0], 0))
        )
        self.image.blit(
            self.frames[8], self.frames[8].get_frect(bottomright=(size))
        )

    def draw_hub_tooltip(self, hub: Hub | None) -> None:
        """Draw the information in the sprite.

        Args:
            hub: The hub to show.
        """
        if self.screen is None:
            return
        self.build_info((self.screen.size[0] - 192, 128))
        real_hub = hub
        if not real_hub:
            return
        connections = ", ".join(
            self.drone_network.connections.get(real_hub.name, {})
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
            f"Total drone: {self.drone_network.nb_drones}",
            f"Connected to: {connections}",
        ]

        text_surfaces = [
            self.font.render(line, True, (255, 255, 255)) for line in lines
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
        self.image.blit(text_surfaces[4], (position_x[2], position_y[0]))
        self.image.blit(text_surfaces[6], (position_x[2], position_y[1]))
        self.image.blit(text_surfaces[7], (position_x[0], position_y[2]))
