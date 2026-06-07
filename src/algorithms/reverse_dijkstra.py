# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    reverse_dijkstra.py                               :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:24 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:54:25 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Class that store the reverse dijkstra class."""

import heapq

from .. import DroneNetwork, ZoneType


class ReverseDijkstra:
    """Class that store the reverse dijkstra algorithm."""

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

            if network_compass.get(current_hub):
                continue

            network_compass[current_hub] = current_cost

            for hub in drone_connection.get_neighbors(current_hub):
                new_cost = current_cost
                if hub.name in network_compass:
                    continue
                if hub.metadata.zone == ZoneType.restricted:
                    new_cost += 2
                elif (
                    hub.metadata.zone == ZoneType.normal
                    or hub.metadata.zone == ZoneType.priority
                ):
                    new_cost += 1
                else:
                    new_cost = -1

                if new_cost >= 0:
                    heapq.heappush(open_list, (new_cost, hub.name))

        return network_compass
