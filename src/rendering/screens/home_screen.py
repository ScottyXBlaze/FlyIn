# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    home_screen.py                                    :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:52:42 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:44:37 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contains the home screen model to use for the rendering."""

import os
import time
from typing import override

import pygame

from ..models import Button
from ..utils import GlobalParameters, SpriteConverter, State


class Home(State):
    """Home screen for the rendering."""

    def __init__(self) -> None:
        """Everything starts here."""
        self._running: bool = True
        self._sprites: dict[str, pygame.Surface] = {}
        self._frames: dict[str, list[pygame.Surface]] = {}
        self._signal: int = 0
        tmp: pygame.Surface | None = pygame.display.get_surface()
        self._screen: pygame.Surface = tmp if tmp else pygame.Surface((10, 10))
        self._init_sprites()

        self._all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )

        self._button_sfx: pygame.Sound = pygame.mixer.Sound(
            os.path.join(GlobalParameters.PATH, "assets", "songs", "start.wav")
        )
        self._button_sfx.set_volume(0.2)

        self._button_start: Button = Button(
            (
                (GlobalParameters.WINDOWWIDTH // 2 - 200),
                GlobalParameters.WINDOWHEIGHT - 400,
            ),
            self._frames["start"],
            self._button_sfx,
        )

        self._button_end: Button = Button(
            (
                (GlobalParameters.WINDOWWIDTH // 2 - 200),
                GlobalParameters.WINDOWHEIGHT - 250,
            ),
            self._frames["exit"],
            self._button_sfx,
        )
        self._all_sprites.add(self._button_start, self._button_end)

        if self._screen:
            self._back: pygame.Surface = self._screen.copy()
            self._background: pygame.Surface = pygame.Surface(
                self._screen.get_frect().size
            ).convert_alpha()
            self._background = pygame.image.load(
                os.path.join(
                    GlobalParameters.PATH, "assets", "background", "main2.png"
                )
            )
            self._background = pygame.transform.scale(
                self._background,
                self._screen.get_size() if self._screen else (0, 0),
            )

    def _init_sprites(self) -> None:
        """Initialize every sprite for the screen."""
        logo = {
            "logo": "logo.png",
        }
        sprites = {
            "exit": "exit.png",
            "start": "start.png",
        }
        for name, path in logo.items():
            self._sprites[name] = pygame.image.load(
                os.path.join(GlobalParameters.PATH, "assets", "model", path)
            )

        for name, path in sprites.items():
            self._sprites[name] = pygame.image.load(
                os.path.join(
                    GlobalParameters.PATH, "assets", "big_button", path
                )
            )
        for name, sprite in self._sprites.items():
            self._sprites[name] = pygame.transform.scale2x(sprite)

        for name, sprite in self._sprites.items():
            if name == "logo":
                continue
            self._frames[name] = SpriteConverter().convert_sprite(
                sprite, (1, 3)
            )

    def _check_event(self) -> None:
        """Check different event and handle them."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._signal = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._button_start._is_working = True
                elif event.key == pygame.K_ESCAPE:
                    self._button_end._is_working = True

    def _render(self) -> None:
        """Render surface in the screen."""
        if not self._screen:
            return
        if self._back:
            _ = self._screen.blit(self._back)
            _ = self._screen.blit(self._background)
        _ = self._screen.blit(
            self._sprites["logo"],
            (GlobalParameters.WINDOWWIDTH // 2 - 200, 50),
        )
        _ = self._all_sprites.draw(self._screen)
        pygame.display.update()

    @override
    def reset(self) -> None:
        """Reset some state of the screen."""
        self._signal = 0
        self._button_start.reset()
        self._button_end.reset()

    @override
    def run(self, dt: float) -> int:
        """Run the home program (should be called every frame)."""
        signal = self._button_end.update_sprite(dt, 1)
        if not signal:
            signal = 0
            signal = self._button_start.update_sprite(dt, 2)
            if not signal:
                self._signal = 0
            else:
                _ = self._button_sfx.play()
                self._signal = signal
        else:
            _ = self._button_sfx.play()
            time.sleep(0.3)
            self._signal = signal
        self._check_event()
        self._render()

        return self._signal if self._signal else 0
