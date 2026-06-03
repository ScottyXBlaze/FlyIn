"""Module that contain every model for the rendering."""

import pygame

from ..parsers.model import Connection, Hub


class HubSprite(pygame.sprite.Sprite):
    """Sprite model for everu hub."""

    def __init__(self, pos: tuple[int, int], color: str, name: str) -> None:
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
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_frect(topleft=self.pos)
        self.image.fill(color)

    @staticmethod
    def transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """
        Transform the index position into a real position in the screen.

        Args:
            pos (tuple[int, int]):  Original position of the hub.
        Returns:
            tuple: The transformed position.
        """
        return pos[0] * 50, pos[1] * 50

    def is_hovered(self, mouse_world: tuple[int, int]) -> bool:
        """
        Check if the mouse is in the hub.

        Args:
            mouse_world (tuple[int, int]): The position of the mouse.
        """
        world_x = self.pos[0]
        world_y = self.pos[1]

        world_rect = pygame.Rect(0, 0, 30, 30)
        world_rect.topleft = (world_x, world_y)

        return world_rect.collidepoint(mouse_world)


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
                position[0] + 12,
                position[1] + 12,
            ),
        )

        self.draw_line()

    @staticmethod
    def transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """Transform the original position to match the screen."""
        return pos[0] * 50, pos[1] * 50

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
