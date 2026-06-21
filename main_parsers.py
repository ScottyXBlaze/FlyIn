# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main_parsers.py                                   :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:11 by nyramana         #+#    #+#              #
#    Updated: 2026/06/21 18:11:57 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Module that contain the parser of the program.

This module stores everything that is used to transform raw data into a
structured variables and class.
"""

from typing import Any
from main_model import Connection, DroneNetwork, Hub


class Parsers:
    """
    Parsers class.

    This class don't use any complex method like the regex but use some
    simple string manipulation to manage data and store them using the
    model in the main_model.py.
    """

    def __init__(self, path: str) -> None:
        """
        Everything starts here.

        Args:
            path (str): The path of the file.
        """
        self._path = path
        self._raw_data: dict[str, Any] = {}
        self._hubs: dict[str, Hub] = {}
        self._connections: dict[str, set[str]] = {}
        self._raw_connections: dict[str, Connection] = {}

        self._checker: dict[str, bool] = {
            "nb_drones": False,
            "start_hub": False,
            "end_hub": False,
        }

    def read_line(self) -> DroneNetwork:
        """
        Read the file and return the parsed file.

        Returns:
            DroneNetwork: The class that contain every information
            of the drone network.
        """
        with open(self._path) as file:

            # Check that the first argument is always the nb of drone
            for line in file:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                else:
                    self._parse_nb_drones(line)
                    self._checker["nb_drones"] = True
                    break
            else:
                raise ValueError("No readable line")

            for line in file:
                self._parse_line(line.strip())

        self._raw_data.update(
            {
                "hubs": self._hubs,
                "connections": self._connections,
                "raw_connection": self._raw_connections,
            }
        )

        variables = list(filter(lambda x: not self._checker[x], self._checker))
        if variables:
            raise ValueError(f"Missing variables: {", ".join(variables)}")

        return DroneNetwork.model_validate(self._raw_data)

    def _parse_line(self, line: str) -> None:
        """
        Parse each line.

        Args:
            line (str): The line to parse.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return

        elif line.startswith("hub: "):
            self._parse_hub(line)

        elif line.startswith("start_hub: "):
            args = line.split()
            self._raw_data["start_hub"] = args[1]
            if not self._checker["start_hub"]:
                self._checker["start_hub"] = True
            else:
                raise ValueError("Duplicate start_hub")
            self._parse_hub(line)

        elif line.startswith("end_hub: "):
            args = line.split()
            self._raw_data["end_hub"] = args[1]
            if not self._checker["end_hub"]:
                self._checker["end_hub"] = True
            else:
                raise ValueError("Duplicate end_hub")
            self._parse_hub(line)

        elif line.startswith("connection: "):
            self._parse_connection(line)

        else:
            raise ValueError(f"Invalid line '{line}'")

    def _parse_nb_drones(self, line: str) -> None:
        """
        Get the nb of drone.

        Args:
            line (str): Description of line.
        """
        if not line.strip().startswith("nb_drones:"):
            raise ValueError(
                "Invalid start line (Should be nb_drones: %d)"
                + f" Got '{line}'"
            )
        else:
            key, value = line.split(maxsplit=1)
            self._raw_data[key[:-1]] = value

    def _parse_connection(self, line: str) -> None:
        """
        Parse the connection.

        Args:
            line (str): The line to parse.
        """
        args = line.split(maxsplit=2)

        if len(args) < 2:
            raise ValueError("Invalid connection value")

        connection = args[1].split("-")

        if len(connection) < 2:
            raise ValueError("Invalid connection value")

        hub1, hub2 = sorted([i.strip() for i in connection])
        if hub1 not in self._hubs.keys() or hub2 not in self._hubs.keys():
            raise ValueError(f"Hub {hub1} or {hub2} not defined yet")

        for hub in [hub1, hub2]:
            if hub not in self._connections:
                self._connections[hub] = set()

        max_link_capacity = 1
        if len(args) == 3:
            metadata = args[2].strip()
            if metadata.startswith("[") and metadata.endswith("]"):
                key, value = metadata[1:-1].split("=", 1)
                if key == "max_link_capacity":
                    max_link_capacity = int(value)
                else:
                    raise ValueError("Invalid metadata")

        self._add_connections(hub1, hub2)
        self._raw_connections.update(
            {
                hub1
                + "-"
                + hub2: Connection(
                    hub1=hub1, hub2=hub2, max_link_capacity=max_link_capacity
                )
            }
        )

    def _add_connections(self, hub1: str, hub2: str) -> None:
        """
        Add two hubs in the connection.

        Args:
            hub1 (str): Description of hub1.
            hub2 (str): Description of hub2.
        """
        if hub2 in self._connections[hub1] and hub1 in self._connections[hub2]:
            raise ValueError(
                f"Duplicated connection for '{hub1}' and '{hub2}'"
            )
        self._connections[hub1].add(hub2)
        self._connections[hub2].add(hub1)

    def _parse_hub(self, line: str) -> None:
        """
        Parse the hub.

        Args:
            line (str): The line to parse.
        """
        args = line.strip().split(maxsplit=4)

        if len(args) < 4:
            raise ValueError(f"Invalid hub {line}")

        if args[0] not in {"hub:", "start_hub:", "end_hub:"}:
            raise ValueError(f"Invalid index {args[0]} in {line}")

        if args[1] in self._hubs.keys():
            raise ValueError(f"Duplicate hub name {args[1]}")
        name = args[1]
        x = args[2]
        y = args[3]

        hub_data: dict[str, Any] = {
            "name": name,
            "x": x,
            "y": y,
        }
        if len(args) == 5:
            raw_metadata = self._parse_metadata_hub(args[4])
            hub_data["metadata"] = raw_metadata

        self._hubs.update({name: Hub.model_validate(hub_data)})

    @staticmethod
    def _parse_metadata_connection(metadata: str) -> dict[str, str]:
        """
        Parse the metadata for the connection.

        Args:
            metadata (str): The string to parse.
        Returns:
            dict: The dictionnary that contain the parsed metadata.
        """
        config = {}
        args = metadata[1:-1]
        name, value = args.split("=")
        if name != "max_link_capacity":
            raise ValueError("Invalid metadata")
        else:
            config[name] = value
        return config

    @staticmethod
    def _parse_metadata_hub(metadata: str) -> dict[str, str]:
        """
        Parse the metadata for the hub.

        Args:
            metadata (str): The string to parse.
        Returns:
            dict: The dictionnary that contain the parsed metadata.
        """
        config = {}
        metadata = metadata.strip()

        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise ValueError(f"Invalid metadata '{metadata}'")

        args = metadata[1:-1]
        for arg in args.split():
            tmp = arg.split("=")
            if len(tmp) != 2:
                raise ValueError(f"Invalid metadata '{arg}'")
            name, value = tmp
            if name not in {"color", "zone", "max_drones"}:
                raise ValueError("Invalid metadata arguments")
            else:
                config[name] = value
        return config
