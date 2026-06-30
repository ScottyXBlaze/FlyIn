# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    drone_network.py                                  :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:12:41 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:36:02 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""
Module that contain the DroneNetwork model for the program.

This class manage the whole algorithm by storing the hub, connection, ...
"""

from typing import Self

from pydantic import BaseModel, Field, model_validator

from . import Connection, Hub


class DroneNetwork(BaseModel):
    """
    DroneNetwork Class.

    It contains every important data of the program.
    """

    nb_drones: int = Field(gt=0, le=10000)
    start_hub: str = Field(default="")
    end_hub: str = Field(default="")
    hubs: dict[str, Hub] = Field(default_factory=dict)
    raw_connection: dict[str, Connection] = Field(default_factory=dict)
    connections: dict[str, set[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def init_size(self) -> Self:
        """Init the size of the starting and ending hub."""
        start_hub = self.hubs.get(self.start_hub)
        end_hub = self.hubs.get(self.end_hub)
        if start_hub and end_hub:
            start_hub.metadata.max_drones = self.nb_drones
            end_hub.metadata.max_drones = self.nb_drones
        return self

    @model_validator(mode="after")
    def check_duplicate(self) -> Self:
        """Check if there are some duplicate position."""
        pos_unavailable: set[tuple[int, int]] = set()
        for hub in self.hubs.values():
            if (hub.x, hub.y) in pos_unavailable:
                raise ValueError("Duplicate position.")
            else:
                pos_unavailable.add((hub.x, hub.y))
        return self

    @property
    def get_start_hub(self) -> Hub:
        """Get the starting hub."""
        return self.hubs[self.start_hub]

    @property
    def get_end_hub(self) -> Hub:
        """Get the ending hub."""
        return self.hubs[self.end_hub]

    def get_neighbors(self, hub_name: str) -> list[Hub]:
        """Get the neighbor of the hub."""
        neighbor_names = self.connections.get(hub_name, set())
        return [self.hubs[name] for name in neighbor_names]

    def get_connection_between(
        self, hub1: str, hub2: str
    ) -> Connection | None:
        """
        Get the connection between two hub.

        Args:
            hub1 (str): The first hub.
            hub2 (str): The second hub.
        Returns:
            Connection: The connection between each hub.
        """
        for name, connection in self.raw_connection.items():
            splitted_name = name.split("-")
            if hub1 in splitted_name and hub2 in splitted_name:
                return connection
        return None
