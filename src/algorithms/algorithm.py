# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/10 11:16:42 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the main algorithm class."""

from .. import DroneNetwork, Hub
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
        for i in range(1, self.drone_network.nb_drones + 1):
            drones.append(Drone(i))
        return drones

    def get_closest_neighbor(self, hub_name: str) -> Hub | None:
        for hub in self.drone_network.get_neighbors(hub_name):
            if self.h_value[hub_name] > self.h_value[hub.name]:
                return hub
        return None

    def get_hub_by_pos(self, pos: tuple[int, int]) -> Hub | None:
        for _, hub in self.drone_network.hubs.items():
            if hub.get_position == pos:
                return hub
        return None

    def move_drone(self, drone: Drone, new_hub: Hub, old_hub: Hub) -> None:
        drone.move(new_hub.get_position[0], new_hub.get_position[1])
        old_hub.remove_drone()
        new_hub.add_drone()

    def run(self) -> None:
        end_position = self.drone_network.get_end_hub.get_position
        while True:
            if not self.drones:
                return
            for drone in self.drones:
                print(f"Drone {drone.id}")

                # Check if it's position is in the end
                if drone.get_position == end_position:
                    self.drones.pop(self.drones.index(drone))

                # Try to see it's neighbor and and go there
                current_hub = self.get_hub_by_pos(drone.get_position)
                if not current_hub:
                    return

                closest_neigbor = self.get_closest_neighbor(current_hub.name)

                if not closest_neigbor:
                    continue
                elif closest_neigbor.is_available():
                    self.move_drone(drone, current_hub, closest_neigbor)
                    print(
                        f"move from {current_hub.name} to {closest_neigbor.name}"
                    )

                # wait
