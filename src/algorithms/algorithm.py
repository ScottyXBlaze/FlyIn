# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/10 13:15:37 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the main algorithm class."""

from src.model import ZoneType

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

        self.drone_network.get_start_hub.current_drone = (
            self.drone_network.nb_drones
        )

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
        best_neighbor: Hub | None = None
        min_h = float("inf")

        for hub in self.drone_network.get_neighbors(hub_name):
            if hub.name in self.h_value and self.h_value[hub.name] < min_h:
                if hub.is_available():
                    min_h = self.h_value[hub.name]
                    best_neighbor = hub

        if best_neighbor and min_h < self.h_value.get(hub_name, float("inf")):
            return best_neighbor
        return None

    def get_hub_by_pos(self, pos: tuple[int, int]) -> Hub | None:
        for _, hub in self.drone_network.hubs.items():
            if hub.get_position == pos:
                return hub
        return None

    def move_drone(self, drone: Drone, new_hub: Hub, old_hub: Hub) -> None:
        if drone.is_in_connection:
            drone.is_in_connection = False
        else:
            pos_x, pos_y = new_hub.get_position
            drone.move(pos_x, pos_y)
            old_hub.remove_drone()
            new_hub.add_drone()

    def run(self) -> None:
        end_position = self.drone_network.get_end_hub.get_position

        i = 0
        while True:
            if not self.drones:
                return

            result = []
            drones_to_remove = []

            for drone in self.drones:

                if drone.get_position == end_position:
                    drones_to_remove.append(drone)
                    continue

                current_hub = self.get_hub_by_pos(drone.get_position)
                if not current_hub:
                    raise ValueError("Position not matching")

                closest_neighbor = self.get_closest_neighbor(current_hub.name)

                if not closest_neighbor:
                    continue

                if (
                    closest_neighbor.get_position == end_position
                    or closest_neighbor.is_available()
                ):
                    self.move_drone(drone, closest_neighbor, current_hub)
                    result.append(f"D{drone.id}-{closest_neighbor.name}")

            # Sécurisation du POP : On retire les drones arrivés en dehors de la boucle de parcours
            for drone in drones_to_remove:
                if drone in self.drones:
                    self.drones.remove(drone)
            i += 1
            print(" ".join(result))
