# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    sprite_converter.py                               :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:49 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:53:55 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain a basic sprite utilities."""

import pygame


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
