# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    n_parsers.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/15 18:45:05 by nyramana         #+#    #+#              #
#    Updated: 2026/06/15 19:06:22 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

from typing import Any
from .. import Connection, DroneNetwork, Hub

class Parsers:
    def __init__(self, path: str) -> None:
        self.path = path
        self.raw_data: dict[str, Any] = {}
        self.hubs: dict[str, Hub] = {}
        self.connections: dict[str, set[str]] = {}
        self.raw_connections: dict[str, Connection] = {}

        self.all_validation: dict[str, bool] = {
            "nb_drones": False,
            "start_hub": False,
            "end_hub": False,
        }

    def is_readable(self, line: str) -> bool:
        if line.startswith("#") or not line:
            return False
        return True

    def parse_nb_drones(self, line: str) -> None:
        # Expected: nb_drones: Int
        args = line.split()

        # It should only split in two
        if len(args) != 2:
            raise ValueError(f"Invalid arguments '{line}', should be nb_drones: Int")

        if args[0] != "nb_drones:":
            raise ValueError(f"Invalid key '{args[0]}', should be nb_drones: Int")

        self.raw_data[args[0][:-1]] = args[1]

    def parse_metadata_hub(self, metadata: str) -> 

    def parse_hub(self, line: str) -> None:
        args = line.split(maxsplit=4)

        if len(args) != 5 or line != 4:
            raise ValueError(f"Invalid arguments '{line}', should be hub: name int int [metadata]")

        if args[0] != "hub:":
            raise ValueError(f"Invalid key '{args[0]}', should be hub: name int int [metadata]")

        name = args[1]
        x = args[2]
        y = args[3]

        hub_data: dict[str, str] = {
            "name": name,
            "x": x,
            "y": y,
        }

        if len(args) == 5:
            raw_metadata = self.parse_metadata_hub(args[4])


    def parse_line(self, line: str) -> None:
        if line.startswith("hub:"):
            self.parse_hub(line)

    def read_file(self) -> None:
        with open(self.path) as file:
            # To Ignore every uninportant line
            line = file.readline().strip()
            while line.startswith("#") or not line:
                line = file.readline().strip()

            # The first readable line is always the nb or drone
            self.parse_nb_drones(line)

            for line in file:
                self.parse_line(line.strip())
