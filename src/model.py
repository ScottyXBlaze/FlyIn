# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    model.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:00 by nyramana         #+#    #+#              #
#    Updated: 2026/06/16 12:57:27 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain every model for the program."""

from enum import Enum
from typing import Self

from pygame.color import THECOLORS
from pydantic import BaseModel, Field, model_validator


class ZoneType(str, Enum):
    """ZoneType enum."""

    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


class Metadata(BaseModel):
    """Metadata class for the hub."""

    zone: ZoneType = Field(default=ZoneType.normal)
    color: str = Field(default="none")
    max_drones: int = Field(ge=1, default=1)

    @model_validator(mode="after")
    def color_validator(self) -> Self:
        """Validate the color to make it valid for pygame."""
        if self.color is None:
            return self
        if (
            self.color.lower() != "none"
            and self.color.lower() not in THECOLORS.keys()
            and self.color.lower() != "rainbow"
        ):
            print("Invalid color arguments: " + self.color)
            print("Setting color as White")
            self.color = "white"

        if self.color.lower() == "none":
            self.color = "black"
        return self


class Hub(BaseModel):
    """Basic Hub class."""

    name: str
    x: int = Field()
    y: int = Field()
    metadata: Metadata = Field(default=Metadata())
    current_drone: int = Field(default=0)

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        """Check the name of the hub."""
        if "-" in self.name or " " in self.name:
            raise ValueError("Invalid name parameters")
        return self

    def add_drone(self) -> None:
        """Add a drone in the hub."""
        self.current_drone += 1

    def remove_drone(self) -> None:
        """Remove a drone in the hub."""
        self.current_drone -= 1

    @property
    def get_position(self) -> tuple[int, int]:
        """
        Get the position of the hub.

        Returns:
            tuple: The position (x, y).
        """
        return self.x, self.y

    def is_available(self) -> bool:
        """
        Check if the hub can still hold drone.

        Returns:
            bool: True if it can.
        """
        return self.current_drone < self.metadata.max_drones


class Connection(BaseModel):
    """Connection Class."""

    hub1: str
    hub2: str
    max_link_capacity: int = Field(gt=0, default=1)
    current_drone: int = Field(default=0)

    @model_validator(mode="after")
    def validate_hubs(self) -> Self:
        """Check if the same hub was entered in the hub."""
        if self.hub1 == self.hub2:
            raise ValueError("Same hub connection name")
        return self

    def is_available(self) -> bool:
        """
        Check if the connection is available.

        Returns:
            bool: True if so.
        """
        return self.max_link_capacity > self.current_drone

    def add_drone(self) -> None:
        """Add a drone to the connection."""
        self.current_drone += 1

    def remove_drone(self) -> None:
        """Remove a drone to the connection."""
        self.current_drone -= 1


class DroneNetwork(BaseModel):
    """DroneNetwork Class."""

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


class Vector2:
    """Simple 2D vector class."""

    def __init__(self, pos: tuple[int, int] = (0, 0)) -> None:
        """Everything starts here."""
        self.x = pos[0]
        self.y = pos[1]

    def set_position(self, x: int, y: int) -> None:
        """
        Set a new value for the vector.

        Args:
            x (int): x position.
            y (int): y position.
        """
        self.x = x
        self.y = y

    def get_position(self) -> tuple[int, int]:
        """
        Get the value of the vector.

        Returns:
            tuple[int, int]: The position in a tuple format.
        """
        return self.x, self.y
