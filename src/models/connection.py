# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    connection.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:07:42 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:34:40 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the connection model for the program."""

from typing import Self

from pydantic import BaseModel, Field, model_validator


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
