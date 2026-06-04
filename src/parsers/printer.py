"""Module that contain a printer to print statistics of the network."""

from .. import DroneNetwork, Hub, Metadata


class ModelPrinter:
    """ModelPrinter Class that contain every printer."""

    def print_hub(self, hub: Hub) -> None:
        """
        Print the hub statistics.

        Args:
            hub (Hub): The hub.
        """
        print("=== Hub ===")
        print(f"Name: {hub.name}")
        print(f"Position: {hub.x} {hub.y}")
        self.print_metadata(hub.metadata)

    def print_metadata(self, metadata: Metadata) -> None:
        """
        Print the metadata statistics.

        Args:
            metadata (Metadata): The metadata.
        """
        print("    == Metadata ==")
        print(f"    Zone: {metadata.zone}")
        print(f"    Color: {metadata.color}")
        print(f"    Max_drones: {metadata.max_drones}")

    def print_drone_network(self, drone_network: DroneNetwork) -> None:
        """
        Print The drone network statistics.

        Args:
            drone_network (DroneNetwork): The drone_network.
        """
        print("=== DroneNetwork ===")
        print(f"Nb Drones: {drone_network.nb_drones}")
        print(f"Start Hub: {drone_network.start_hub}")
        print(f"End Hub: {drone_network.end_hub}")
        for _, hub in drone_network.hubs.items():
            self.print_hub(hub)
        for hub_name, connection in drone_network.connections.items():
            print(f"Connection: {hub_name} --> {connection}")
