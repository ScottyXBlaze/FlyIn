from enum import Enum
from typing import Self

from pygame.color import THECOLORS
from pydantic import BaseModel, Field, model_validator


class ZoneType(str, Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


class Metadata(BaseModel):
    zone: ZoneType = Field(default=ZoneType.normal)
    color: str = Field(default="none")
    max_drones: int = Field(ge=1, default=1)

    @model_validator(mode="after")
    def color_validator(self) -> Self:
        if self.color is None:
            return self
        if (
            self.color.lower() != "none"
            and self.color.lower() not in THECOLORS.keys()
        ):
            raise ValueError("Invalid color arguments: " + self.color)
        if self.color.lower() == "none":
            self.color = "black"
        return self


class Hub(BaseModel):
    name: str
    x: int
    y: int
    metadata: Metadata = Field(default=Metadata())

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        if "-" in self.name or " " in self.name:
            raise ValueError("Invalid name parameters")
        return self


class Connection(BaseModel):
    hub1: str
    hub2: str
    max_link_capacity: int = Field(gt=0, default=1)

    @model_validator(mode="after")
    def validate_hubs(self) -> Self:
        if self.hub1 == self.hub2:
            raise ValueError("Same hub connection name")
        return self


class DroneNetwork(BaseModel):
    nb_drones: int = Field(gt=0)
    start_hub: str = Field(default="")
    end_hub: str = Field(default="")
    hubs: dict[str, Hub] = Field(default_factory=dict)
    raw_connection: list[Connection] = Field(
        default_factory=list, exclude=False
    )
    connections: dict[str, set[str]] = Field(default_factory=dict)

    def get_start_hub(self) -> Hub:
        return self.hubs[self.start_hub]

    def get_end_hub(self) -> Hub:
        return self.hubs[self.end_hub]

    def get_neighbors(self, hub_name: str) -> list[Hub]:
        neighbor_names = self.connections.get(hub_name, set())
        return [self.hubs[name] for name in neighbor_names]
