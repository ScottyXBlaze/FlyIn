# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    state_manager.py                                  :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:48:12 by nyramana         #+#    #+#              #
#    Updated: 2026/06/16 13:28:11 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the state manager for the screen."""

import os
import sys

import pygame

from src.rendering.base_state import State
from src.rendering.home import Home

from .rendering import Renderer
from .. import DroneNetwork
from .settings import WINDOWHEIGHT, WINDOWWIDTH


class StateManager:
    """Class to manage multiple screen or display and change them."""

    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[int, int]]],
    ) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): Class that contain every variables.
            heuristic_value (dict[str, int]): heuristic value for each hub.
            path (list[dict[int, tuple[int, int]]]): Path of each drone.
        """
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.clock = pygame.time.Clock()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        pygame.display.set_icon(
            pygame.image.load(
                os.path.join(self.base_dir, "assets", "MainLogo.png")
            )
        )

        pygame.mixer.music.load(
            os.path.join(self.base_dir, "assets", "music", "Clouds.ogg")
        )
        pygame.mixer.music.play(-1)

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
        """Run the program."""
        while True:
            dt = self.clock.tick(60) / 1000
            signal = self.program.run(dt)
            if signal == 1:
                self.quit()
            elif signal == 2:
                self.change_program()
                self.program.reset()

    def quit(self) -> None:
        """Quit the program."""
        pygame.quit()
        sys.exit(0)
