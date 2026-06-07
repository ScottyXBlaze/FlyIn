from .. import DroneNetwork
from .reverse_dijkstra import ReverseDijkstra


class Algorithm:
    def __init__(self, drone_network: DroneNetwork) -> None:
        self.drone_network = drone_network
        self.heuristic_value = ReverseDijkstra.calculate_heuristic(
            self.drone_network
        )
