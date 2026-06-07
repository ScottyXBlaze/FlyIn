import heapq

from .. import DroneNetwork, ZoneType


class ReverseDijkstra:
    @staticmethod
    def calculate_heuristic(
        drone_connection: DroneNetwork,
    ) -> dict[str, int | float]:
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
                    new_cost = float("-inf")

                heapq.heappush(open_list, (new_cost, hub.name))

        return network_compass
