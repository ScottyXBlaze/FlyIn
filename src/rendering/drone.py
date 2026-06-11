# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 10:38:23 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 12:07:28 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import math
import pygame


CELL = 50
MARGIN = 50


def grid_to_px(gx: int, gy: int) -> tuple[float, float]:
    """Centre pixel d'une case de la grille."""
    return (MARGIN + gx * CELL + CELL // 2, MARGIN + gy * CELL + CELL // 2)


def _ease_in_out(t: float) -> float:
    """Courbe ease-in-out cubique (0 → 1)."""
    return t * t * (3 - 2 * t)


class Drone(pygame.sprite.Sprite):
    def __init__(
        self,
        id: int,
        position: tuple[int, int],
        sprite: pygame.Surface,
    ):
        super().__init__()
        self.drone_id = id
        self.grid_pos = position

        self._base_image = sprite.copy()

        self.px, self.py = grid_to_px(*position)
        self.anim_speed: float = 0.25
        self._anim_active: bool = False
        self._anim_start: tuple[float, float] = (self.px, self.py)
        self._anim_end: tuple[float, float] = (self.py, self.py)
        self._anim_elapsed: float = 0.0
        self._angle: float = 0.0
        self.image = self._base_image.copy()
        self.rect = self.image.get_frect(center=(self.px, self.py))

    @property
    def position(self) -> tuple[int, int]:
        return self.grid_pos

    @position.setter
    def position(self, new_pos: tuple[int, int]) -> None:
        self.grid_pos = new_pos
        self.px, self.py = grid_to_px(*new_pos)
        self._anim_active = False
        self._sync_sprite()

    def _sync_sprite(self) -> None:
        """Keep `image` and `rect` aligned with the current pixel position."""
        if self._angle != 0.0:
            self.image = pygame.transform.rotate(self._base_image, -self._angle)
        else:
            self.image = self._base_image.copy()
        self.rect = self.image.get_frect(center=(self.px, self.py))

    def move_to(self, dest: tuple[int, int]):
        # If it is already in it's position, don't do anything
        if dest == self.grid_pos and not self._anim_active:
            return

        dx = dest[0] - self.grid_pos[0]
        dy = dest[1] - self.grid_pos[1]

        # To rotate the drone
        if dx != 0 or dy != 0:
            self._angle = math.degrees(math.atan2(dx, -dy))
            self._sync_sprite()

        self._anim_start = (self.px, self.py)
        self._anim_end = grid_to_px(*dest)
        self._anim_elapsed = 0.0
        self._anim_active = True
        self.grid_pos = dest

    def update(self, dt: float):
        if not self._anim_active:
            return

        self._anim_elapsed += dt
        t = min(self._anim_elapsed / self.anim_speed, 1.0)
        t = _ease_in_out(t)

        sx, sy = self._anim_start
        ex, ey = self._anim_end
        self.px = sx + (ex - sx) * t
        self.py = sy + (ey - sy) * t
        self.rect.center = (self.px, self.py)

        if self._anim_elapsed >= self.anim_speed:
            self.px, self.py = self._anim_end
            self._anim_active = False
            self.rect.center = self._anim_end

    @property
    def is_moving(self) -> bool:
        return self._anim_active
