# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    button.py                                         :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:22:47 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:41:27 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the Button model to use for the rendering."""

import pygame


class Button(pygame.sprite.Sprite):
    """Button class for every class."""

    def __init__(
        self,
        pos: tuple[int, int],
        frames: list[pygame.Surface],
        sound: pygame.Sound,
    ) -> None:
        """
        Everything starts here.

        Args:
            pos (tuple[int, int]): Position of the button.
            frames (list[pygame.Surface]): The sprites
            for the button.
        """
        super().__init__()
        self._frames = frames
        self.image = self._frames[0]
        self.rect = self.image.get_frect(topleft=pos)

        self._frame_index = 0
        self._animation_time = 0.017
        self._current_time = 0.0
        self._is_working = False

        self._sound = sound

    def _animate(self) -> None:
        """Animate the button when called."""
        self._frame_index += 1
        self.image = self._frames[self._frame_index % len(self._frames)]

    def _time_animation(self, dt: float) -> bool:
        """
        Handle the time of the animation.

        Args:
            dt (float): Delta time.
        Returns:
            bool: True if it can animate.
        """
        self._current_time += dt
        if self._current_time >= self._animation_time:
            self._current_time = 0
            return True
        return False

    def reset(self) -> None:
        """Reset the button state like frame and time."""
        self._current_time = 0.0
        self._frame_index = 0
        self._is_working = False
        self.image = self._frames[0]

    def check_hovered(self) -> None:
        """Check if the button is hovered by the mouse."""
        if not self.rect:
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if not self._is_working:
                self._sound.play()
            self._is_working = True
        else:
            if self._is_working:
                self.reset()

    def update_sprite(self, dt: float, signal: int) -> int | None:
        """
        Update the sprite status (should be called every frame).

        Args:
            dt (float): Delta time.
            signal (int): Signal to return if True.
        Returns:
            int: The signal.
        """
        if pygame.mouse.get_pressed()[0]:
            self.check_hovered()

        if self._is_working and self._time_animation(dt):
            if self._frame_index == 3:
                return signal
            self._animate()
        return 0
