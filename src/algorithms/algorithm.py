# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/10 17:39:38 by nyramana        ###   ########.fr        #
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
        """
        Get the closest neighbor of a hub.

        Args:
            hub_name (str): the name of the hub.

        Returns:
            Hub: Description of return value.
        """
        best_neighbor: list[Hub] = []
        min_h = float("inf")

        for hub in self.drone_network.get_neighbors(hub_name):
            if hub.name in self.h_value and self.h_value[hub.name] < min_h:
                if hub.is_available():
                    min_h = self.h_value[hub.name]
                    best_neighbor = [hub]
            elif self.h_value[hub.name] == min_h:
                if hub.is_available():
                    best_neighbor.append(hub)

        for neighbor in best_neighbor:
            if neighbor and min_h < self.h_value.get(hub_name, float("inf")):
                return neighbor
        return None

    def get_hub_by_pos(self, pos: tuple[int, int]) -> Hub | None:
        """
        Get the hub by it's position.

        Args:
            pos (tuple[int, int]): The position of the hub.
        Returns:
            Hub: The Hub in the position or None.
        """
        for _, hub in self.drone_network.hubs.items():
            if hub.get_position == pos:
                return hub
        return None

    def moove_drone(self, drone: Drone, new_hub: Hub, old_hub: Hub) -> str:
        """
        Move a drone to a specific hub | connection.

        Args:
            drone (Drone): The drone we want to move.
            new_hub (Hub): The hub we want to move.
            old_hub (Hub): The hub we are at.
        """
        # Check if the drone is in connection
        if not drone.is_in_connection:
            # Check if it the zone is restricted
            if new_hub.metadata.zone == ZoneType.restricted:
                drone.is_in_connection = True

                connection = self.drone_network.get_connection_between(
                    new_hub.name, old_hub.name
                )
                if not connection:
                    print("No connection")
                    return ""

                drone.target_connection = connection
                drone.target_connection.add_drone()

                return f"D{drone.id}-{old_hub.name}-{new_hub.name}"
            else:
                pos_x, pos_y = new_hub.get_position
                drone.move(pos_x, pos_y)
                old_hub.remove_drone()
                new_hub.add_drone()
                return f"D{drone.id}-{new_hub.name}"
        else:
            drone.is_in_connection = False
            pos_x, pos_y = new_hub.get_position
            if drone.target_connection:
                drone.target_connection.remove_drone()
            drone.target_connection = None
            drone.target_hub = None
            drone.move(pos_x, pos_y)
            old_hub.remove_drone()
            new_hub.add_drone()
            return f"D{drone.id}-{new_hub.name}"

    def move_drone(
        self, drone: Drone, new_hub: Hub, old_hub: Hub
    ) -> str | None:
        """
        Move the drone and modify it's value.

        Args:
            drone (Drone): Drone class.
            new_hub (Hub): The destination hub.
            old_hub (Hub): The ancient hub.
        Returns:
            str: The action while moving the drone.
        """
        if not drone.is_in_connection:
            if getattr(new_hub.metadata, "zone", None) == ZoneType.restricted:
                # Phase 1 : Entrée en transit (Zone restreinte)
                drone.is_in_connection = True
                connection = self.drone_network.get_connection_between(
                    new_hub.name, old_hub.name
                )
                if not connection:
                    return ""
                print(connection)
                drone.target_connection = connection
                drone.target_connection.add_drone()
                drone.target_hub = new_hub
                return f"D{drone.id}-{old_hub.name}-{new_hub.name}"
            else:
                # Déplacement normal (1 tour)
                pos_x, pos_y = new_hub.get_position
                drone.move(pos_x, pos_y)
                old_hub.remove_drone()
                new_hub.add_drone()
                return f"D{drone.id}-{new_hub.name}"
        else:
            dest_hub = drone.target_hub
            if not dest_hub:
                return ""
            if drone.target_connection:
                drone.target_connection.remove_drone()
                drone.target_connection = None
                drone.target_hub = None
            pos_x, pos_y = dest_hub.get_position
            drone.move(pos_x, pos_y)
            old_hub.remove_drone()
            dest_hub.add_drone()

            # Reset des variables de transit
            drone.is_in_connection = False
            drone.target_hub = None
            return f"D{drone.id}-{dest_hub.name}"

    def run(self) -> None:
        """Run the algorithm."""
        end_position = self.drone_network.get_end_hub.get_position

        while True:
            result = []
            drones_to_remove = []

            for drone in self.drones:
                # If the drone reaches the end
                if drone.get_position == end_position:
                    drones_to_remove.append(drone)
                    continue

                # Get the current Hub
                current_hub = self.get_hub_by_pos(drone.get_position)
                if not current_hub:
                    raise ValueError("Position not matching")

                # Get the closest neighbor
                closest_neighbor = self.get_closest_neighbor(current_hub.name)
                if not closest_neighbor:
                    continue

                # Move if available
                if (
                    closest_neighbor.get_position == end_position
                    or closest_neighbor.is_available()
                ):
                    move = self.moove_drone(
                        drone, closest_neighbor, current_hub
                    )
                    if move:
                        result.append(move)

            # Remove drone that reach the end
            for drone in drones_to_remove:
                if drone in self.drones:
                    self.drones.remove(drone)

            if not result:
                return

            print(" ".join(result))
