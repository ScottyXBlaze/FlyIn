from typing import Self
from pydantic import BaseModel, Field, model_validator
import pygame


class Metadata(BaseModel):
    zone: str = Field(default="normal")
    color: str = Field(default="none")
    max_drones: int = Field(ge=1, default=1)

    @model_validator(mode="after")
    def zone_validator(self) -> Self:
        self.zone = self.zone.lower()
        if self.zone not in {
            "normal",
            "blocked",
            "restricted",
            "priority",
        }:
            raise ValueError("Invalid zone arguments: " + self.zone)
        return self

    @model_validator(mode="after")
    def color_validator(self) -> Self:
        if (
            self.color.lower() != "none"
            and self.color.lower() not in pygame.color.THECOLORS.keys()
        ):
            raise ValueError("Invalid color arguments: " + self.color)
        return self


class Hub(BaseModel):
    name: str
    x: int
    y: int
    metadata: Metadata = Field(default=Metadata())


class DroneNetwork(BaseModel):
    nb_drones: int = Field(gt=0)
    start_hub: str = Field(default="")
    end_hub: str = Field(default="")
    hubs: dict[str, Hub] = Field(default={})
    connections: dict[str, set[str]] = {}

    @property
    def get_start_hub(self) -> Hub:
        return self.hubs[self.start_hub]

    @property
    def get_end_hub(self) -> Hub:
        return self.hubs[self.end_hub]

    def get_neighbords(self, hub_name: str) -> list[Hub]:
        neighbord_names = self.connections.get(hub_name, set())
        return [self.hubs[name] for name in neighbord_names]
