# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 10:32:38 by nyramana        ###   ########.fr        #
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

        # Make the end hub and start hub to be bigger to store every drone
        start_hub = self.drone_network.get_start_hub
        start_hub.current_drone = self.drone_network.nb_drones

        end_hub = self.drone_network.get_end_hub
        end_hub.current_drone = 0

        self.result: list[tuple[int, tuple[int, int]]] = []

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
        current_h = self.h_value.get(hub_name, float("inf"))

        for hub in self.drone_network.get_neighbors(hub_name):
            hub_h = self.h_value.get(hub.name, float("inf"))
            if hub_h >= current_h:
                continue

            connection = self.drone_network.get_connection_between(hub_name, hub.name)
            if not connection or not connection.is_available():
                continue

            if hub.name != self.drone_network.end_hub and not hub.is_available():
                continue

            if hub_h < min_h:
                min_h = hub_h
                best_neighbor = [hub]
            elif hub_h == min_h:
                best_neighbor.append(hub)

        for neighbor in best_neighbor:
            if neighbor and min_h < current_h:
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

    def moove_drone(
        self, drone: Drone, new_hub: Hub, old_hub: Hub
    ) -> tuple[str, tuple[int, int]]:
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
                connection = self.drone_network.get_connection_between(
                    new_hub.name, old_hub.name
                )
                if not connection or not connection.is_available():
                    return "", (0, 0)

                if (
                    new_hub.name != self.drone_network.end_hub
                    and not new_hub.is_available()
                ):
                    return "", (0, 0)

                old_hub.remove_drone()
                new_hub.add_drone()
                drone.is_in_connection = True
                drone.target_connection = connection
                drone.target_connection.add_drone()
                drone.target_hub = new_hub

                return (
                    f"D{drone.id}-{old_hub.name}-{new_hub.name}",
                    new_hub.get_position,
                )
            else:
                if (
                    new_hub.name != self.drone_network.end_hub
                    and not new_hub.is_available()
                ):
                    return "", (0, 0)

                pos_x, pos_y = new_hub.get_position
                drone.move(pos_x, pos_y)
                old_hub.remove_drone()
                new_hub.add_drone()
                return f"D{drone.id}-{new_hub.name}", new_hub.get_position
        else:
            drone.is_in_connection = False
            if drone.target_connection:
                drone.target_connection.remove_drone()
            drone.target_connection = None
            drone.target_hub = None
            pos_x, pos_y = new_hub.get_position
            drone.move(pos_x, pos_y)
            return f"D{drone.id}-{new_hub.name}", new_hub.get_position

    def movae_drone(
        self,
        drone: Drone,
        new_hub: Hub,
        old_hub: Hub,
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
                connection = self.drone_network.get_connection_between(
                    new_hub.name, old_hub.name
                )
                if not connection or not connection.is_available():
                    return ""

                if (
                    new_hub.name != self.drone_network.end_hub
                    and not new_hub.is_available()
                ):
                    return ""

                old_hub.remove_drone()
                new_hub.add_drone()
                drone.is_in_connection = True
                drone.target_connection = connection
                drone.target_connection.add_drone()
                drone.target_hub = new_hub
                return f"D{drone.id}-{old_hub.name}-{new_hub.name}"
            else:
                # Déplacement normal (1 tour)
                if (
                    new_hub.name != self.drone_network.end_hub
                    and not new_hub.is_available()
                ):
                    return ""

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
            pos_x, pos_y = dest_hub.get_position
            drone.move(pos_x, pos_y)

            # Reset des variables de transit
            drone.is_in_connection = False
            drone.target_hub = None
            return f"D{drone.id}-{dest_hub.name}"

    def run(self) -> None:
        """Run the algorithm."""
        end_position = self.drone_network.get_end_hub.get_position

        turn = 0
        while True:
            result = []
            drones_to_remove = []
            drones_snapshot = list(self.drones)
            moved_this_turn: set[int] = set()

            # First, finish drones already in transit so their connection is freed
            for drone in drones_snapshot:
                if not drone.is_in_connection:
                    continue

                if drone.get_position == end_position:
                    drones_to_remove.append(drone)
                    continue

                current_hub = self.get_hub_by_pos(drone.get_position)
                if not current_hub:
                    raise ValueError("Position not matching")

                move, position = self.moove_drone(drone, drone.target_hub, current_hub)
                if move:
                    result.append(move)
                    self.result.append((turn, position))
                    moved_this_turn.add(drone.id)

            # Then move new drones if possible
            for drone in drones_snapshot:
                if drone.id in moved_this_turn:
                    continue
                if drone.is_in_connection:
                    continue

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

                move, position = self.moove_drone(drone, closest_neighbor, current_hub)
                if move:
                    result.append(move)
                    self.result.append((turn, position))
                    moved_this_turn.add(drone.id)

            # Remove drone that reach the end
            for drone in drones_to_remove:
                if drone in self.drones:
                    self.drones.remove(drone)

            # If there are no drones left, we stop
            if not self.drones:
                print(turn)
                return

            # If nothing moved and nobody is in transit, the network is stuck
            if not result and not any(drone.is_in_connection for drone in self.drones):
                print(turn)
                return

            turn += 1

            print(" ".join(result))
