# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/08 19:53:37 by nyramana         #+#    #+#              #
#    Updated: 2026/06/10 16:26:20 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the base class for the drone."""

from src.model import Connection, Hub

from .. import Vector2


class Drone:
    """Main class for every drone."""

    def __init__(self, id: int) -> None:
        """
        Everything starts here.

        Args:
            id (int): The id of the drone.
        """
        self.id = id
        self._position = Vector2()
        self.is_in_connection: bool = False
        self.target_hub: Hub | None = None
        self.target_connection: Connection | None = None

    def move(self, x: int, y: int) -> None:
        """
        Move the drone to a specific location.

        Args:
            x (int): x position.
            y (int): y position.
        """
        self._position.set_position(x, y)

    @property
    def get_position(self) -> tuple[int, int]:
        """
        Get the position of the drone.

        Returns:
            tuple: The position of the drone in integer.
        """
        return self._position.get_position()
