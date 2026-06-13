# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    base_state.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/11 18:44:39 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 10:37:50 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the base state for every screen."""

from abc import ABC, abstractmethod


class State(ABC):
    """Base state class for every screen or display."""

    @abstractmethod
    def run(self, dt: float) -> int:
        """Run the program and return some signal."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the program if needed."""
        pass
