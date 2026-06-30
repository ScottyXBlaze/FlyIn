# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:27:51 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:43:49 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the Drone model to use for the rendering."""

import random

import pygame

from ..utils import GlobalParameters, SpriteConverter


class DroneSprite(pygame.sprite.Sprite):
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
            color (tuple[int, int]): The color of the drone.
            offset (tuple[int, int]): The offset of the drone.
        """
        super().__init__()
        # Base attribute for each drone.
        self._drone_id = id
        self._grid_pos = position
        self._pixel_offset = offset

        # frame of the drone
        self._frames = SpriteConverter().convert_sprite(sprite, (2, 1))
        if color is not None:
            self._frames = [
                self._tint_sprite(frame, color) for frame in self._frames
            ]

        self._px, self._py = self._grid_to_px(*position, self._pixel_offset)

        # Animation variable
        self._anim_speed: float = 0.3
        self._anim_active: bool = False
        self._anim_elapsed: float = 0.0

        # Animation speed
        self._frame_index: int = 0
        self._frame_elapsed: float = 0.0
        self._frame_speed: float = random.uniform(0.05, 0.2)

        # Position end to start
        self._anim_start: tuple[float, float] = (self._px, self._py)
        self._anim_end: tuple[float, float] = (self._px, self._py)

        # Image and rect of the sprite
        self.image = self._frames[self._frame_index]
        self.rect = self.image.get_frect(center=(self._px, self._py))

    def _grid_to_px(
        self, gx: int, gy: int, offset: tuple[int, int] = (0, 0)
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
            gx * GlobalParameters.CELL_SIZE
            + GlobalParameters.CELL_SIZE // 2
            + GlobalParameters.OFFSET[0] * gx
            + offset[0],
            gy * GlobalParameters.CELL_SIZE
            + GlobalParameters.CELL_SIZE // 2
            + GlobalParameters.OFFSET[1] * gy
            + offset[1],
        )

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

    def _sync_sprite(self) -> None:
        """Keep `image` and `rect` aligned with the current pixel position."""
        self._frame_index += 1
        self._frame_index %= len(self._frames)
        self.image = self._frames[self._frame_index]

    @property
    def position(self) -> tuple[int, int]:
        """Get the position of the drone."""
        return self._grid_pos

    @position.setter
    def position(self, new_pos: tuple[int, int]) -> None:
        """
        Get the position of the drone.

        Args:
            new_pos (tuple[int, int]): The new position of the drone.
        """
        self._grid_pos = new_pos
        self._px, self._py = self._grid_to_px(*new_pos, self._pixel_offset)
        self._anim_active = False

    def _move_to(self, dest: tuple[int, int]) -> None:
        """
        Move the drone to a specific destination.

        Args:
            dest (tuple[int, int]): The destination of the drone.
        """
        # If it is already in it's position, don't do anything
        if dest == self._grid_pos and not self._anim_active:
            return

        self._anim_start = (self._px, self._py)
        self._anim_end = self._grid_to_px(*dest, self._pixel_offset)
        self._anim_elapsed = 0.0
        self._anim_active = True
        self._grid_pos = dest

    def update(self, dt: float) -> None:
        """
        Update the state of the drone.

        Args:
            dt (float): delta time.
        """
        # Animate the drone sprite all the time, movement only when needed.
        self._frame_elapsed += dt
        if self._frame_elapsed >= self._frame_speed:
            self._frame_elapsed %= self._frame_speed
            self._sync_sprite()

        if not self.rect:
            return

        if not self._anim_active:
            self.rect.center = (self._px, self._py)
            return

        self._anim_elapsed += dt
        t = min(self._anim_elapsed / self._anim_speed, 1.0)

        sx, sy = self._anim_start
        ex, ey = self._anim_end
        self._px = sx + (ex - sx) * t
        self._py = sy + (ey - sy) * t
        self.rect.center = (self._px, self._py)

        if self._anim_elapsed >= self._anim_speed:
            self._px, self._py = self._anim_end
            self._anim_active = False
            self.rect.center = self._anim_end

    @property
    def is_moving(self) -> bool:
        """Check if the drone is moving."""
        return self._anim_active
