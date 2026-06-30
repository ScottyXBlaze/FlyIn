# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    hub.py                                            :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:06:33 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:36:35 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contain the Hub model for the program."""

from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, model_validator
from pygame.color import THECOLORS


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
