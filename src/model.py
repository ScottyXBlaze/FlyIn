# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    model.py                                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:00 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:54:00 by nyramana        ###   ########.fr        #
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
    """Basic Hub class.

    Attributes:
        name: The name of the hub.
        x: The position x of the hub.
        y: The position y of the hub.
        metadata: The metadata of the hub.
        current_drone: The number of drone in the hub.
    """

    name: str
    x: int
    y: int
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


class DroneNetwork(BaseModel):
    """DroneNetwork Class."""

    nb_drones: int = Field(gt=0)
    start_hub: str = Field(default="")
    end_hub: str = Field(default="")
    hubs: dict[str, Hub] = Field(default_factory=dict)
    raw_connection: list[Connection] = Field(
        default_factory=list, exclude=False
    )
    connections: dict[str, set[str]] = Field(default_factory=dict)

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
