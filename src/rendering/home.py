# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    home.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:51:36 by nyramana         #+#    #+#              #
#    Updated: 2026/06/12 20:33:57 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import pygame
import os
from src.rendering.base_state import State
from src.rendering.settings import WINDOWHEIGHT, WINDOWWIDTH
from src.rendering.sprite_converter import SpriteConverter


class Home(State):
    def __init__(self) -> None:
        self.running = True
        self.sprites: dict[str, pygame.Surface] = {}
        self.frames: dict[str, list[pygame.Surface]] = {}
        self.signal = 0
        self.screen = pygame.display.get_surface()
        self.init_sprites()

        self.position_exit = self.frames["exit"][0].get_frect()
        self.position_exit.topright = (
            WINDOWWIDTH - 80,
            200,
        )

        self.position_start = self.frames["start"][0].get_frect()
        self.position_start.topright = (
            WINDOWWIDTH - 80,
            50,
        )

        if self.screen:
            self.back = self.screen.copy()
            self.background = pygame.Surface(
                self.screen.get_frect().size
            ).convert_alpha()
            self.background.fill((206, 208, 206, 80))

    def set_position(self) -> None:
        self.sprites["logo"].get_frect(
            center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
        )

    def init_sprites(self) -> None:
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.signal = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.signal = 2

    def update(self) -> None:
        pass

    def render(self) -> None:
        if not self.screen:
            return
        self.screen.blit(self.back)
        self.screen.blit(self.background)
        self.screen.blit(self.sprites["logo"], (50, 50))
        self.screen.blit(self.frames["exit"][0], self.position_exit)
        self.screen.blit(self.frames["start"][0], self.position_start)
        pygame.display.update()

    def reset(self) -> None:
        self.signal = 0
        self.back = pygame.display.get_surface()
        self.back = None if not self.back else self.back.copy()

    def run(self) -> int:
        self.check_event()
        self.update()
        self.render()
        return self.signal
