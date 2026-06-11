# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    state_manager.py                                  :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:48:12 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 18:50:54 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import pygame

from . import Renderer
from .base_state import State
from .. import DroneNetwork


class StateManager:
    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[int, int]]],
    ) -> None:
        pygame.init()
        self.main_program = Renderer(drone_network, heuristic_value, path)


    def quit(self) -> None:
        pygame.quit()
