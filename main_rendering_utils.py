# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    rendering_utils.py                                :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:47 by nyramana         #+#    #+#              #
#    Updated: 2026/06/19 14:17:59 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain some static variable."""

import pygame
from abc import ABC, abstractmethod


class GlobalParameters:
    WINDOWWIDTH, WINDOWHEIGHT = 1400, 800
    CELL_SIZE = 50
    OFFSET = (20, 20)


class SpriteConverter:
    """Sprite utilities for the rendering system."""

    def convert_sprite(
        self, image: pygame.Surface, frames: tuple[int, int]
    ) -> list[pygame.Surface]:
        """
        Convert a tile into a list of frame.

        Args:
            image (pygame.Surface): The original image to convert.
            frames (tuple[int, int]): The number of frame (x, y).
        Returns:
            list: the list of all the frames.
        """
        image_size = image.get_size()

        frame_size: tuple[int, int] = (
            image_size[0] // frames[0],
            image_size[1] // frames[1],
        )

        frame_list: list[pygame.Surface] = []

        for x in range(frames[0]):
            for y in range(frames[1]):
                frame_rect = pygame.Rect(
                    x * frame_size[0],
                    y * frame_size[1],
                    frame_size[0],
                    frame_size[1],
                )
                tile = image.subsurface(frame_rect)
                frame_list.append(tile)

        return frame_list


class State(ABC):
    """Base state class for every screen or display."""

    @abstractmethod
    def run(self, dt: float) -> int:
        """Run the program and return some signal."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the program if needed."""
        pass
