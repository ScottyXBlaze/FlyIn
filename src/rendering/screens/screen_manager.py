# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    screen_manager.py                                 :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:44:15 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:45:13 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the screen manager model to use for the rendering."""

import sys
import os

import pygame

from ...models import DroneNetwork
from ..utils import GlobalParameters, State
from .main_screen import Renderer
from .home_screen import Home


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
        self._screen = pygame.display.set_mode(
            (GlobalParameters.WINDOWWIDTH, GlobalParameters.WINDOWHEIGHT)
        )
        self._clock = pygame.time.Clock()

        pygame.display.set_icon(
            pygame.image.load(
                os.path.join(
                    GlobalParameters.PATH, "assets", "model", "main.png"
                )
            )
        )

        pygame.mixer.music.load(
            os.path.join(
                GlobalParameters.PATH, "assets", "songs", "clouds.ogg"
            )
        )

        pygame.mixer.music.play(-1)

        self._main_program = Renderer(
            drone_network, heuristic_value, path, self._clock
        )
        self._home_program = Home()
        self._program: State = self._home_program

    def _change_program(self) -> None:
        """Change the program."""
        if self._program == self._main_program:
            self._program = self._home_program
        else:
            self._program = self._main_program

    def run(self) -> None:
        """Run the program."""
        while True:
            dt = self._clock.tick(60) / 1000
            signal = self._program.run(dt)
            if signal == 1:
                self.quit()
            elif signal == 2:
                self._change_program()
                self._program.reset()

    def quit(self) -> None:
        """Quit the program."""
        pygame.quit()
        sys.exit(0)
