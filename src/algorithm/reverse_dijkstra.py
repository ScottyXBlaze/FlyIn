# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    reverse_dijkstra.py                               :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:15:37 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:30:00 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Module that contains the reverse_dijkstra class.

ReverseDijkstra is used to calculate the heuristic value of every available hub
"""

import heapq

from ..models import DroneNetwork, ZoneType


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
