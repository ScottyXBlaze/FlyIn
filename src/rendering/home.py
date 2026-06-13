# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    home.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:51:36 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 11:12:00 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the home program."""

import pygame
import os
from .base_state import State
from .settings import WINDOWWIDTH
from .sprite_converter import SpriteConverter


class Button(pygame.sprite.Sprite):
    """Button class for every class."""

    def __init__(
        self,
        pos: tuple[int, int],
        frames: list[pygame.Surface],
    ) -> None:
        """
        Everything starts here.

        Args:
            pos (tuple[int, int]): Position of the button.
            frames (list[pygame.Surface]): The sprites for the button.
        """
        super().__init__()
        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft=pos)

        self.frame_index = 0
        self.animation_time = 0.02
        self.current_time = 0.0
        self.is_animated = False

    def animate(self) -> None:
        """Animate the button when called."""
        self.frame_index += 1
        self.image = self.frames[self.frame_index % len(self.frames)]

    def time_animation(self, dt: float) -> bool:
        """
        Handle the time of the animation.

        Args:
            dt (float): Delta time.
        Returns:
            bool: True if it can animate.
        """
        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            return True
        return False

    def reset(self) -> None:
        """Reset the button state like frame and time."""
        self.current_time = 0.0
        self.frame_index = 0
        self.is_animated = False
        self.image = self.frames[0]

    def check_hovered(self) -> None:
        """Check if the button is hovered by the mouse."""
        if not self.rect:
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            self.is_animated = True
        else:
            if self.is_animated:
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

        if self.is_animated and self.time_animation(dt):
            if self.frame_index == 3:
                return signal
            self.animate()
        return 0


class Home(State):
    """Home screen for the rendering."""

    def __init__(self) -> None:
        """Everything starts here."""
        self.running = True
        self.sprites: dict[str, pygame.Surface] = {}
        self.frames: dict[str, list[pygame.Surface]] = {}
        self.signal = 0
        self.screen = pygame.display.get_surface()
        self.init_sprites()

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )

        self.button_start = Button(
            (WINDOWWIDTH - 500, 50),
            self.frames["start"],
        )

        self.button_end = Button(
            (WINDOWWIDTH - 500, 180),
            self.frames["exit"],
        )
        self.all_sprites.add(self.button_start, self.button_end)

        if self.screen:
            self.back = self.screen.copy()
            self.background = pygame.Surface(
                self.screen.get_frect().size
            ).convert_alpha()
            self.background.fill((2, 62, 138))

    def init_sprites(self) -> None:
        """Initialize every sprite for the screen."""
        sprites = {
            "logo": "logo.png",
            "exit": "ButtonExit.png",
            "start": "ButtonStart.png",
        }
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for name, path in sprites.items():
            self.sprites[name] = pygame.image.load(
                os.path.join(base_dir, "assets", path)
            )
        for name, sprite in self.sprites.items():
            self.sprites[name] = pygame.transform.scale2x(sprite)

        for name, sprite in self.sprites.items():
            if name == "logo":
                continue
            self.frames[name] = SpriteConverter().convert_sprite(
                sprite, (1, 3)
            )

    def check_event(self) -> None:
        """Check different event and handle them."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.signal = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.signal = 2

    def render(self) -> None:
        """Render surface in the screen."""
        if not self.screen:
            return
        if self.back:
            self.screen.blit(self.back)
            self.screen.blit(self.background)
        self.screen.blit(self.sprites["logo"], (50, 50))
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def reset(self) -> None:
        """Reset some state of the screen."""
        self.signal = 0
        self.button_start.reset()
        self.button_end.reset()

    def run(self, dt: float) -> int:
        """Run the home program (should be called every frame)."""
        signal = self.button_end.update_sprite(dt, 1)
        if not signal:
            signal = 0
            signal = self.button_start.update_sprite(dt, 2)
            if not signal:
                self.signal = 0
            else:
                self.signal = 2
        else:
            self.signal = signal
        self.check_event()
        self.render()

        return self.signal if self.signal else 0
