# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 10:38:23 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 15:51:59 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the drons sprite."""

import math
import pygame
import random

from .sprite_converter import SpriteConverter

from .settings import CELL_SIZE, OFFSET


def grid_to_px(
    gx: int, gy: int, offset: tuple[int, int] = (0, 0)
) -> tuple[float, float]:
    """
    Tranform the grid position into a pixel position.

    Args:
        gx (int): Grid position in x.
        gy (int): Grid position in y.
        offset (tuple[int, int]): offset of the sprite for uniformity.

    Returns:
        tuple: The position of the drone as pixel.
    """
    return (
        gx * CELL_SIZE + CELL_SIZE // 2 + OFFSET[0] * gx + offset[0],
        gy * CELL_SIZE + CELL_SIZE // 2 + OFFSET[1] * gy + offset[1],
    )


class Drone(pygame.sprite.Sprite):
    """Drone Class for rendering."""

    def __init__(
        self,
        id: int,
        position: tuple[int, int],
        sprite: pygame.Surface,
        color: tuple[int, int, int] | None = None,
        offset: tuple[int, int] = (0, 0),
    ):
        """
        Everything starts here.

        Args:
            id (int): The ID of the drone.
            position (tuple[int, int]): The position of the drone.
            sprite (pygame.Surface): The sprite of the drone.
            color (tuple[int): The color of the drone.
            offset (tuple[int): The offset of the drone.
        """
        super().__init__()
        self.drone_id = id
        self.grid_pos = position
        self.pixel_offset = offset

        self._frames = SpriteConverter().convert_sprite(sprite, (2, 1))
        if color is not None:
            self._frames = [
                self._tint_sprite(frame, color) for frame in self._frames
            ]

        self.px, self.py = grid_to_px(*position, self.pixel_offset)
        self.anim_speed: float = 0.25
        self._anim_active: bool = False
        self._anim_start: tuple[float, float] = (self.px, self.py)
        self._anim_end: tuple[float, float] = (self.px, self.py)
        self._anim_elapsed: float = 0.0
        self._angle: float = 0.0
        self._frame_index: int = 0
        self._frame_elapsed: float = 0.0
        self.frame_speed: float = random.uniform(0.1, 0.4)
        self.image = self._build_image(self._frame_index)
        self.rect = self.image.get_frect(center=(self.px, self.py))

    @staticmethod
    def _tint_sprite(
        sprite: pygame.Surface, color: tuple[int, int, int]
    ) -> pygame.Surface:
        """Apply a light color tint to the drone sprite."""
        image = sprite.copy()
        tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint.fill((*color, 255))
        image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    def _build_image(self, frame_index: int) -> pygame.Surface:
        """Build the current drone image from the selected frame and angle."""
        frame = self._frames[frame_index % len(self._frames)]
        if self._angle != 0.0:
            return pygame.transform.rotate(frame, -self._angle)
        return frame.copy()

    def _sync_sprite(self, frame_index: int | None = None) -> None:
        """Keep `image` and `rect` aligned with the current pixel position."""
        if frame_index is not None:
            self._frame_index = frame_index % len(self._frames)
        center = self.rect.center if self.rect else (self.px, self.py)
        self.image = self._build_image(self._frame_index)
        self.rect = self.image.get_frect(center=center)

    @property
    def position(self) -> tuple[int, int]:
        """Get the position of the drone."""
        return self.grid_pos

    @position.setter
    def position(self, new_pos: tuple[int, int]) -> None:
        """
        Get the position of the drone.

        Args:
            new_pos (tuple[int, int]): The new position of the drone.
        """
        self.grid_pos = new_pos
        self.px, self.py = grid_to_px(*new_pos, self.pixel_offset)
        self._anim_active = False
        self._sync_sprite()

    def move_to(self, dest: tuple[int, int]) -> None:
        """
        Move the drone to a specific destination.

        Args:
            dest (tuple[int, int]): The destination of the drone.
        """
        # If it is already in it's position, don't do anything
        if dest == self.grid_pos and not self._anim_active:
            return

        dx = dest[0] - self.grid_pos[0]
        dy = dest[1] - self.grid_pos[1]

        # To rotate the drone
        if dx != 0 or dy != 0:
            self._angle = math.degrees(math.atan2(dx, -dy))

        self._anim_start = (self.px, self.py)
        self._anim_end = grid_to_px(*dest, self.pixel_offset)
        self._anim_elapsed = 0.0
        self._anim_active = True
        self.grid_pos = dest
        self._sync_sprite()

    def update(self, dt: float) -> None:
        """
        Update the state of the drone.

        Args:
            dt (float): delta time.
        """
        # Animate the drone
        self._frame_elapsed += dt
        if self._frame_elapsed >= self.frame_speed:
            self._frame_elapsed %= self.frame_speed
            self._sync_sprite(self._frame_index + 1)

        if not self._anim_active:
            return

        self._anim_elapsed += dt
        t = min(self._anim_elapsed / self.anim_speed, 1.0)

        frame_index = 0 if t < 0.5 else 1
        if frame_index != self._frame_index:
            self._sync_sprite(frame_index)

        sx, sy = self._anim_start
        ex, ey = self._anim_end
        self.px = sx + (ex - sx) * t
        self.py = sy + (ey - sy) * t
        if self.rect and self.rect.center:
            self.rect.center = (self.px, self.py)

            if self._anim_elapsed >= self.anim_speed:
                self.px, self.py = self._anim_end
                self._anim_active = False
                self.rect.center = self._anim_end

    @property
    def is_moving(self) -> bool:
        """Check if the drone is moving."""
        return self._anim_active
