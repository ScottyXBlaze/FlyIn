# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    state_manager.py                                  :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:48:12 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 09:44:12 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import pygame

from src.rendering.base_state import State
from src.rendering.home import Home

from .rendering import Renderer
from .. import DroneNetwork
from .settings import WINDOWHEIGHT, WINDOWWIDTH


class StateManager:
    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[int, int]]],
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.clock = pygame.time.Clock()

        self.main_program = Renderer(
            drone_network, heuristic_value, path, self.clock
        )
        self.home_program = Home()
        self.program: State = self.home_program

    def change_program(self) -> None:
        """Change the program."""
        if self.program == self.main_program:
            self.program = self.home_program
        else:
            self.program = self.main_program

    def run(self) -> None:
        """
        Run the program.
        """
        while True:
            dt = self.clock.tick(60) / 1000
            signal = self.program.run(dt)
            if signal == 1:
                self.quit()
                pygame.quit()
                return
            elif signal == 2:
                self.change_program()
                self.program.reset()

    def quit(self) -> None:
        pygame.quit()
