# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main_algorithm.py                                 :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:24 by nyramana         #+#    #+#              #
#    Updated: 2026/06/21 18:07:58 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Main algorithm module, It contains everything to run the algroritm.

This module contains the ReverseDijkstra and Algorithm class that solve
every map.
"""

import heapq

from main_model import DroneNetwork, ZoneType, Drone, Hub


class Algorithm:
    """
    Main class for the algorithm.

    This algorithm has no real name but act like the A* method.
    It uses the heuristic value made with the ReverseDijkstra algorithm
    and compare every single neighbor using a specific value like the
    heuristic, then the zonetype, then the zone capacity and so one.
    I made it like that so that every drone don't go to a specific but
    traverse other zone that has the same value but not visited often.
    """

    class ReverseDijkstra:
        """
        This class contains the ReverseDijkstra algorithm.

        ReverseDijkstra algorithm is an alternative of the original
        Dijkstra but used specially to check the closest path from every
        single zone to it's destination. It is made so that we don't need
        to recalculate every single zone for each drone but we just check
        it's value and compare with another zone to see which zone is the
        best.
        """

        @staticmethod
        def calculate_heuristic(
            drone_connection: DroneNetwork,
        ) -> dict[str, int | float]:
            """
            Calculate the heuristic value for each hub.

            Args:
                drone_connection (DroneNetwork): The class
                for the drone connection.
            Returns:
                dict: a dict of {name: value} for each hub.
            """
            network_compass: dict[str, int | float] = {}
            open_list: list[tuple[int | float, str]] = []
            heapq.heappush(open_list, (0, drone_connection.get_end_hub.name))

            while open_list:
                current_cost, current_hub = heapq.heappop(open_list)

                real_hub = drone_connection.hubs[current_hub]
                if current_hub in network_compass:
                    continue

                network_compass[current_hub] = current_cost

                for hub in drone_connection.get_neighbors(current_hub):
                    new_cost = current_cost
                    if hub.name in network_compass:
                        continue

                    if real_hub.metadata.zone == ZoneType.restricted:
                        new_cost += 2
                    elif (
                        real_hub.metadata.zone == ZoneType.normal
                        or real_hub.metadata.zone == ZoneType.priority
                    ):
                        new_cost += 1
                    else:
                        new_cost = -1

                    if hub.metadata.zone == ZoneType.blocked:
                        new_cost = -1

                    if new_cost >= 0:
                        heapq.heappush(open_list, (new_cost, hub.name))

            return network_compass

    def __init__(self, drone_network: DroneNetwork) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): The drone network class.
        """
        self._drone_network: DroneNetwork = drone_network

        self.h_value: dict[str, int | float] = (
            self.ReverseDijkstra.calculate_heuristic(drone_network)
        )
        self._drones: list[Drone] = self._set_drones()
        self._hub_by_position: dict[tuple[int, int], Hub] = {
            hub.get_position: hub for hub in self._drone_network.hubs.values()
        }

        self._drone_positions_per_turn: list[dict[int, tuple[int, int]]] = []
        self._edge_usage: dict[tuple[str, str], int] = {}

    def _set_drones(self) -> list[Drone]:
        """
        Create every drone we need.

        Returns:
            list[Drone]: List of the drone.
        """
        drones: list[Drone] = []
        start_pos = self._drone_network.get_start_hub.get_position
        for i in range(1, self._drone_network.nb_drones + 1):
            drones.append(Drone(i, start_pos))
        return drones

    def _get_closest_neighbor(self, hub_name: str) -> Hub | None:
        """
        Get the closest neighbor of a hub.

        Args:
            hub_name (str): the name of the hub.

        Returns:
            Hub: Description of return value.
        """
        # current minimum Heuristic value
        current_h = self.h_value.get(hub_name, float("inf"))

        best_key: tuple[float, int, int, int, int, str] | None = None
        best_hub: Hub | None = None

        for hub in self._drone_network.get_neighbors(hub_name):

            hub_h = self.h_value.get(hub.name, float("inf"))
            if hub_h >= current_h:
                continue

            connection = self._drone_network.get_connection_between(
                hub_name, hub.name
            )  # If the connection is not available (for restricted)
            if not connection or not connection.is_available():
                continue

            if (
                hub.name != self._drone_network.end_hub
                and not hub.is_available()
            ):
                continue

            edge_key = (hub_name, hub.name)
            usage = self._edge_usage.get(edge_key, 0)

            zone_rank = {
                ZoneType.priority: 0,
                ZoneType.normal: 1,
                ZoneType.restricted: 2,
                ZoneType.blocked: 3,
            }[hub.metadata.zone]

            special_rank = 0 if hub.name == "priority" else zone_rank

            score = (
                float(hub_h)
                + (usage * 1.5)
                + (hub.current_drone / hub.metadata.max_drones)
                + (connection.current_drone / connection.max_link_capacity)
                + (zone_rank * 0.05)
            )
            candidate_key = (
                score,
                special_rank,
                usage,
                hub.current_drone,
                connection.current_drone,
                hub.name,
            )
            if best_key is None or candidate_key < best_key:
                best_key = candidate_key
                best_hub = hub

        return best_hub

    def get_hub_by_pos(self, pos: tuple[int, int]) -> Hub | None:
        """
        Get the hub by it's position.

        Args:
            pos (tuple[int, int]): The position of the hub.
        Returns:
            Hub: The Hub in the position or None.
        """
        return self._hub_by_position.get(pos)

    def _move_in_connection(
        self,
        drones_snapshot: list[Drone],
        end_position: tuple[int, int],
        result: list[str],
        moved_this_turn: set[int],
    ) -> tuple[list[Drone], bool]:
        """
        Move drone that is in connection.

        Args:
            drones_snapshot (list[Drone]): list of drone to move.
            end_position (tuple[int, int]): Position of the end_hub.
            turn (int): The current turn.
            result (list[str]): The result to print.
            moved_this_turn (set[int]): Every drone that moved in the turn.
        Returns:
            tuple: The list of drone to remove and bool to see if it should
            stop or not.
        """
        drones_to_remove: list[Drone] = []

        for drone in drones_snapshot:
            if not drone.is_in_connection:
                continue

            if drone.get_position == end_position:
                drones_to_remove.append(drone)
                continue

            current_hub = self.get_hub_by_pos(drone.get_position)
            if not current_hub:
                raise ValueError(f"Invalid position {drone.get_position}")

            if not drone.target_hub:
                return drones_to_remove, True

            move = self._move_drone(drone, drone.target_hub, current_hub)
            if move:
                result.append(move)
                moved_this_turn.add(drone.id)

        return drones_to_remove, False

    def _move_waiting(
        self,
        drones_snapshot: list[Drone],
        end_position: tuple[int, int],
        result: list[str],
        moved_this_turn: set[int],
        drones_to_remove: list[Drone],
    ) -> bool:
        """
        Move drone that isn't in a Connection.

        Args:
            drones_snapshot (list[Drone]): list of drone to move.
            end_position (tuple[int, int]): Position of the end_hub.
            turn (int): The current turn.
            result (list[str]): The result to print.
            moved_this_turn (set[int]): Every drone that moved in the turn.
            drones_to_remove (list[Drone]): list of drone to remove.
        Returns:
            bool: Description of return value.
        """
        has_in_connection = False
        for drone in drones_snapshot:
            if drone.id in moved_this_turn or drone.is_in_connection:
                continue

            if drone.get_position == end_position:
                drones_to_remove.append(drone)
                continue

            current_hub = self.get_hub_by_pos(drone.get_position)
            if not current_hub:
                raise ValueError("Position not matching")

            closest_neighbor = self._get_closest_neighbor(current_hub.name)
            if not closest_neighbor:
                continue

            move = self._move_drone(drone, closest_neighbor, current_hub)
            if move:
                result.append(move)
                moved_this_turn.add(drone.id)

                edge_key = (current_hub.name, closest_neighbor.name)
                self._edge_usage[edge_key] = (
                    self._edge_usage.get(edge_key, 0) + 1
                )

                if drone.is_in_connection:
                    has_in_connection = True

        return has_in_connection

    def _remove_arrived_drones(self, drones_to_remove: list[Drone]) -> None:
        """Remove all drones that reached destination in one pass."""
        if not drones_to_remove:
            return

        drones_to_remove_ids = {drone.id for drone in drones_to_remove}
        self._drones = [
            drone
            for drone in self._drones
            if drone.id not in drones_to_remove_ids
        ]

    def _record_turn_positions(self) -> None:
        """Store current drones positions for rendering."""
        turn_positions = {
            drone.id: drone.get_position for drone in self._drones
        }
        self._drone_positions_per_turn.append(turn_positions)

    def _move_drone(self, drone: Drone, new_hub: Hub, old_hub: Hub) -> str:
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
                connection = self._drone_network.get_connection_between(
                    new_hub.name, old_hub.name
                )
                if not connection or not connection.is_available():
                    return ""

                if (
                    new_hub.name != self._drone_network.end_hub
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
                if (
                    new_hub.name != self._drone_network.end_hub
                    and not new_hub.is_available()
                ):
                    return ""

                pos_x, pos_y = new_hub.get_position
                drone.move(pos_x, pos_y)
                old_hub.remove_drone()
                new_hub.add_drone()
                return f"D{drone.id}-{new_hub.name}"
        else:
            drone.is_in_connection = False
            if drone.target_connection:
                drone.target_connection.remove_drone()
            drone.target_connection = None
            drone.target_hub = None
            pos_x, pos_y = new_hub.get_position
            drone.move(pos_x, pos_y)
            return f"D{drone.id}-{new_hub.name}"

    def run(self) -> None:
        """Run the algorithm."""
        end_position = self._drone_network.get_end_hub.get_position

        turn = 0
        while True:
            # The result of every drone moving
            result: list[str] = []

            # Copy of the list of drone.
            drones_snapshot: list[Drone] = self._drones.copy()

            # To store who move in the turn to avoid moving twice
            moved_this_turn: set[int] = set()

            to_remove, can_stop = self._move_in_connection(
                drones_snapshot,
                end_position,
                result,
                moved_this_turn,
            )
            if can_stop:
                return

            in_connection = self._move_waiting(
                drones_snapshot,
                end_position,
                result,
                moved_this_turn,
                to_remove,
            )

            self._remove_arrived_drones(to_remove)

            # If there are no drones left, we stop
            if not self._drones:
                print(f"\nTotal Turn: {turn}")
                return

            # If nothing moved and nobody is in transit
            if not result and not in_connection:
                print(f"\nTotal Turn: {turn}")
                return

            self._record_turn_positions()

            turn += 1

            print(" ".join(result))

    def get_path(self) -> list[dict[int, tuple[int, int]]]:
        """
        Get the path of every drone.

        Returns:
            list[list[tuple[int, int]]]: The path of every drone.
        """
        return self._drone_positions_per_turn
