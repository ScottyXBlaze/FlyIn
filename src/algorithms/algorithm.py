# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    algorithm.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42.fr>         +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:49:13 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 14:25:51 by nyramana        ###   ########.fr        #
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
        self.drone_positions_per_turn: list[dict[int, tuple[int, int]]] = []
        self.edge_usage: dict[tuple[str, str], int] = {}

        # Variable to store the result
        self.result: list[tuple[int, tuple[float, float]]] = []

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
        current_h = self.h_value.get(hub_name, float("inf"))
        candidates: list[tuple[tuple[float, int, int, int, int, str], Hub]] = []

        for hub in self.drone_network.get_neighbors(hub_name):
            hub_h = self.h_value.get(hub.name, float("inf"))
            if hub_h >= current_h:
                continue

            connection = self.drone_network.get_connection_between(
                hub_name, hub.name
            )
            # If the connection is not available (for restricted)
            if not connection or not connection.is_available():
                continue

            if (
                hub.name != self.drone_network.end_hub
                and not hub.is_available()
            ):
                continue

            edge_key = (hub_name, hub.name)
            usage = self.edge_usage.get(edge_key, 0)

            zone_rank = {
                ZoneType.priority: 0,
                ZoneType.normal: 1,
                ZoneType.restricted: 2,
                ZoneType.blocked: 3,
            }[hub.metadata.zone]

            # Keep the shortest path preference, but add a small load-aware
            # penalty so parallel branches get used more evenly.
            score = (
                float(hub_h)
                + (usage * 1.5)
                + (hub.current_drone / hub.metadata.max_drones)
                + (connection.current_drone / connection.max_link_capacity)
                + (zone_rank * 0.05)
            )
            candidates.append(
                (
                    (
                        score,
                        usage,
                        hub.current_drone,
                        connection.current_drone,
                        zone_rank,
                        hub.name,
                    ),
                    hub,
                )
            )

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

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
    ) -> tuple[str, tuple[float, float]]:
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
                new_x, new_y = new_hub.get_position
                old_x, old_y = old_hub.get_position

                new_pos: tuple[float, float] = (
                    (new_x + old_x) / 2,
                    (new_y + old_y) / 2,
                )
                return (
                    f"D{drone.id}-{old_hub.name}-{new_hub.name}",
                    new_pos,
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

    def run(self) -> None:
        """Run the algorithm."""
        end_position = self.drone_network.get_end_hub.get_position

        turn = 0
        while True:
            result: list[str] = []
            drones_to_remove = []
            drones_snapshot = list(self.drones)
            moved_this_turn: set[int] = set()
            for drone in drones_snapshot:
                if not drone.is_in_connection:
                    continue

                if drone.get_position == end_position:
                    drones_to_remove.append(drone)
                    continue

                current_hub = self.get_hub_by_pos(drone.get_position)
                if not current_hub:
                    raise ValueError("Position not matching")

                if not drone.target_hub:
                    return

                move, position = self.moove_drone(
                    drone, drone.target_hub, current_hub
                )
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

                move, position = self.moove_drone(
                    drone, closest_neighbor, current_hub
                )
                if move:
                    result.append(move)
                    self.result.append((turn, position))
                    moved_this_turn.add(drone.id)
                    edge_key = (current_hub.name, closest_neighbor.name)
                    self.edge_usage[edge_key] = (
                        self.edge_usage.get(edge_key, 0) + 1
                    )

            # Remove drone that reach the end
            for drone in drones_to_remove:
                if drone in self.drones:
                    self.drones.remove(drone)

            # If there are no drones left, we stop
            if not self.drones:
                return

            # If nothing moved and nobody is in transit, the network is stuck
            if not result and not any(
                drone.is_in_connection for drone in self.drones
            ):
                return

            # Record positions of all drones for this turn
            turn_positions: dict[int, tuple[int, int]] = {}
            for drone in self.drones:
                turn_positions[drone.id] = drone.get_position
            self.drone_positions_per_turn.append(turn_positions)

            turn += 1

            print(" ".join(result))

    def get_path(self) -> list[dict[int, tuple[int, int]]]:
        """
        Get the path of every drone.

        Returns:
            list[list[tuple[int, int]]]: The path of every drone.
        """
        return self.drone_positions_per_turn
