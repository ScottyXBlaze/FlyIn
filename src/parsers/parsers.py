from typing import Any
from .model import DroneNetwork, Hub, Connection


class Parsers:
    def __init__(self, path: str) -> None:
        self.path = path
        self.raw_data: dict[str, Any] = {}
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, set[str]] = {}
        self.raw_connections: list[Connection] = []

    def read_line(self) -> DroneNetwork:
        with open(self.path) as file:
            for line in file:
                self.parse_line(line)
        self.raw_data.update(
            {
                "hubs": self.hubs,
                "connections": self.connections,
                "raw_connection": self.raw_connections,
            }
        )
        return DroneNetwork.model_validate(self.raw_data)

    def parse_line(self, line: str) -> None:
        args = line.split(" ")
        if args[0].strip() == "nb_drones:":
            self.raw_data[args[0][:-1]] = args[1]
        elif line.strip().startswith("hub:"):
            self.parse_hub(line)
        elif line.strip().startswith("start_hub:"):
            self.raw_data["start_hub"] = args[1]
            self.parse_hub(line)
        elif line.strip().startswith("end_hub:"):
            self.raw_data["end_hub"] = args[1]
            self.parse_hub(line)
        elif line.strip().startswith("connection:"):
            self.parse_connection(line)

    def parse_connection(self, line: str) -> None:
        args = line.split(" ", 2)
        connection = args[1].split("-")

        if len(connection) < 2:
            raise ValueError("Invalid connection value")

        hub1, hub2 = [i.strip() for i in connection]
        for hub in connection:
            if hub not in self.connections:
                self.connections[hub.strip()] = set()

        max_link_capacity = 1
        if len(args) == 3:
            if args[2].startswith("[") and args[2].endswith("]"):
                key, value = args[2].strip()[1:-1].split("=", 1)
                if key == "max_link_capacity":
                    max_link_capacity = int(value)
                else:
                    raise ValueError("Invalid metadata")

        self.add_connections(hub1, hub2)
        self.raw_connections.append(
            Connection(
                hub1=hub1, hub2=hub2, max_link_capacity=max_link_capacity
            )
        )

    def add_connections(self, hub1: str, hub2: str) -> None:
        self.connections[hub1].add(hub2)
        self.connections[hub2].add(hub1)

    def parse_hub(self, line: str) -> None:
        args = line.strip().split(" ", 4)
        if len(args) < 4:
            raise ValueError(f"Invalid hub {line}")
        name = args[1]
        x = args[2]
        y = args[3]

        hub_data: dict[str, Any] = {
            "name": name,
            "x": x,
            "y": y,
        }
        if len(args) == 5:
            raw_metadata = self.parse_metadata_hub(args[4])
            hub_data["metadata"] = raw_metadata

        self.hubs.update({name: Hub.model_validate(hub_data)})

    @staticmethod
    def parse_metadata_connection(metadata: str) -> dict[str, str]:
        config = {}
        args = metadata[1:-1]
        name, value = args.split("=")
        if name != "max_link_capacity":
            raise ValueError("Invalid metadata")
        else:
            config[name] = value
        return config

    @staticmethod
    def parse_metadata_hub(metadata: str) -> dict[str, str]:
        config = {}
        args = metadata[1:-1]
        for arg in args.split(" "):
            name, value = arg.split("=")
            if name not in {"color", "zone", "max_drones"}:
                raise ValueError("Invalid metadata arguments")
            else:
                config[name] = value
        return config
