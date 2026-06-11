# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    home.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:51:36 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 19:34:48 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import pygame
from src.rendering.base_state import State


class Home(State):
    def __init__(self) -> None:
        self.running = True
        self.sprites: list[pygame.Surface] = []

    def init_sprites(self) -> None:
        sprites = {
            "logo": "logo.png" 
        }
    def check_event(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.K_w:
                pass
            if event.type == pygame.K_w:
                pass

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

    def run(self) -> None:
        while True:
            self.check_event()
            self.update()
            self.render()
