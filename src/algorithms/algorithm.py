# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/08 20:20:41 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the main algorithm class."""

from .. import DroneNetwork
from .reverse_dijkstra import ReverseDijkstra

from .drone import Drone


class Algorithm:
    """Main class for the algorithm."""

    def __init__(self, drone_network: DroneNetwork) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): The drone network class.
        """
        self.drone_network = drone_network
        self.h_value = ReverseDijkstra.calculate_heuristic(drone_network)
        self.drones: list[Drone] = self.set_drones()

    def set_drones(self) -> list[Drone]:
        """
        Create every drone we need.

        Returns:
            list[Drone]: List of the drone.
        """
        drones = []
        for i in range(1, self.drone_network.nb_drones):
            drones.append(Drone(i))
        return drones
