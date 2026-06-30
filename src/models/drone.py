# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:11:59 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:35:06 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contain the Drone model for the program."""

from . import Hub, Connection


class Vector2:
    """Simple 2D vector class."""

    def __init__(self, pos: tuple[int, int] = (0, 0)) -> None:
        """Everything starts here."""
        self.x = pos[0]
        self.y = pos[1]

    def set_position(self, x: int, y: int) -> None:
        """
        Set a new value for the vector.

        Args:
            x (int): x position.
            y (int): y position.
        """
        self.x = x
        self.y = y

    def get_position(self) -> tuple[int, int]:
        """
        Get the value of the vector.

        Returns:
            tuple[int, int]: The position in a tuple format.
        """
        return self.x, self.y


class Drone:
    """Main class for every drone."""

    def __init__(self, id: int, pos: tuple[int, int]) -> None:
        """
        Everything starts here.

        Args:
            id (int): The id of the drone.
        """
        self.id = id
        self._position = Vector2(pos)
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
