"""Module that contain the main rendering class."""

import pygame
import os
import sys

from src.rendering.camera import Camera

from .model import HubSprite, ConnectionSprite

from ..parsers.model import DroneNetwork, Hub

from .groups import AllSprite

from typing import Any

from .settings import WINDOWHEIGHT, WINDOWWIDTH


class Renderer:
    """Rendering class for the FlyIn Project."""

    def __init__(self, drone_network: DroneNetwork) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): The main class of the project.
        """
        # Common
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("FlyIn - Drone Simulator")

        # Camera
        self.camera = Camera()

        # Text
        self.font = pygame.font.SysFont(None, 20)

        # DroneNetwork
        self.drone_network = drone_network
        self.bound = self.check_bound(self.drone_network.hubs)

        # Sprite groups
        self.all_sprite = AllSprite()

        # Assets
        self.assets: dict[str, pygame.Surface] = {}

        self.running = True

        self.load_hubs()
        self.load_connections()
        self.load_assets()

    def load_hubs(self) -> None:
        """Load every hub sprite."""
        for _, hub in self.drone_network.hubs.items():
            self.all_sprite.add(
                HubSprite((hub.x, hub.y), hub.metadata.color, hub.name)
            )

    def load_connections(self) -> None:
        """Load every connection sprite."""
        for connection in self.drone_network.raw_connection:
            hub1 = self.drone_network.hubs.get(connection.hub1)
            hub2 = self.drone_network.hubs.get(connection.hub2)
            if hub1 is not None and hub2 is not None:
                self.all_sprite.add(ConnectionSprite(hub1, hub2, connection))

    def load_assets(self) -> None:
        """Load every assets."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_file = {
            "drone": "drone.png",
            "ui": "BackUI.png",
            "ui_pos": "BackPos.png",
            "ui_inf": "BackInfo.png",
            "ui_main": "BackMain.png",
        }
        for name, path in image_file.items():
            try:
                path = os.path.join(base_dir, "assets", path)
                self.assets[name] = pygame.image.load(path)
            except pygame.error as e:
                print(e)
                sys.exit()

        self.assets["ui_main"] = pygame.transform.scale(
            self.assets["ui_main"], self.screen.get_size()
        )

    def handle_camera(self) -> None:
        """Handle the camera to not go too far."""
        self.camera.camera_x = min(self.bound[0], self.camera.camera_x)
        self.camera.camera_x = max(self.bound[2], self.camera.camera_x)
        self.camera.camera_y = min(self.bound[1], self.camera.camera_y)
        self.camera.camera_y = max(self.bound[3], self.camera.camera_y)

    def check_bound(self, hubs: dict[str, Hub]) -> list[int]:
        """Check the limits of the scree based on hubs coordinates."""
        maximum_x = max(hubs.values(), key=lambda x: x.x).x * 50 - 200
        maximum_y = max(hubs.values(), key=lambda x: x.y).y * 50 - 300
        minimum_x = min(hubs.values(), key=lambda x: x.x).x * 50 + 200
        minimum_y = min(hubs.values(), key=lambda x: x.y).y * 50 + 100
        return [maximum_x, maximum_y, minimum_x, minimum_y]

    def check_event(self) -> None:
        """Check some event."""
        self.handle_camera()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.camera.draging = True
                    self.camera.last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.camera.draging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.camera.draging:
                    self.camera.camera_x -= (
                        event.pos[0] - self.camera.last_mouse_pos[0]
                    )
                    self.camera.camera_y -= (
                        event.pos[1] - self.camera.last_mouse_pos[1]
                    )
                    self.camera.last_mouse_pos = event.pos

    def get_input(self, delta: float) -> None:
        """
        Get the input from the user.

        Args:
            delta (float): Delta time.
        """
        keys = pygame.key.get_pressed()
        self.camera.camera_x += int(
            200 * delta * (keys[pygame.K_d] - keys[pygame.K_a])
        )
        self.camera.camera_y += int(
            200 * delta * (keys[pygame.K_s] - keys[pygame.K_w])
        )

        if keys[pygame.K_q]:
            self.running = False

    def check_for_ui(self) -> None:
        """Check if we need to show the UI or not."""
        hub = self.check_over_pos()
        if hub is not None:
            self.draw_hub_tooltip(hub, pygame.mouse.get_pos())

    def draw_hub_tooltip(self, hub: str, mouse_pos: tuple[int, int]) -> None:
        """
        Draw a tooltip for a hub.

        Args:
            hub (str): The hub we want to show.
            mouse_pos (tuple[int, int]): The position of the mouse.
        """
        real_hub = self.drone_network.hubs.get(hub)
        if not real_hub:
            return
        lines = [
            f"Name: {real_hub.name}",
            f"Pos: x={real_hub.x}  y={real_hub.y}",
            f"ZoneType: {real_hub.metadata.zone.name}",
            f"Color: {real_hub.metadata.color}",
            f"MaxDrone: {real_hub.metadata.max_drones}",
        ]

        padding = 10
        line_spacing = 5
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fonts = os.path.join(base_dir, "assets", "Oxanium-Bold.ttf")
        font = pygame.font.Font(fonts, 19)

        text_surfaces = [font.render(line, True, (0, 0, 0)) for line in lines]
        max_w = max(surf.get_width() for surf in text_surfaces) + (padding * 2)
        total_h = (
            sum(surf.get_height() for surf in text_surfaces)
            + (line_spacing * (len(lines) - 1))
            + (padding * 2)
        )

        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15

        if tooltip_x + max_w > self.screen.get_width():
            tooltip_x = mouse_pos[0] - max_w - 5
        if tooltip_y + total_h > self.screen.get_height():
            tooltip_y = mouse_pos[1] - total_h - 5

        resized_bg = pygame.transform.scale(
            self.assets["ui_inf"], (max_w, total_h)
        )
        current_y = padding
        for surf in text_surfaces:
            resized_bg.blit(surf, (padding, current_y))
            current_y += surf.get_height() + line_spacing

        self.screen.blit(resized_bg, (tooltip_x, tooltip_y))

    def check_over_pos(self) -> str | None:
        """
        Check if the mouse is over a hub.

        Returns:
            str: the name of the hub or None.
        """
        mouse_pos = pygame.mouse.get_pos()
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        mouse_world_x = mouse_pos[0] - center_x + self.camera.camera_x
        mouse_world_y = mouse_pos[1] - center_y + self.camera.camera_y
        for hub in self.all_sprite.sprites():
            if isinstance(hub, HubSprite):
                if hub.is_hovered((mouse_world_x, mouse_world_y)):
                    return hub.name
        return None

    def run(self) -> None:
        """Run the rendering."""
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.check_event()
            self.get_input(dt)
            self.screen.blit(self.assets["ui_main"])
            self.all_sprite.draw_sprite(
                (self.camera.camera_x, self.camera.camera_y)
            )
            self.camera_text = self.font.render(
                f" X: {self.camera.camera_x:.1f} |"
                + f"Y: {self.camera.camera_y:.1f} {'hello':.1}",
                True,
                (182, 32, 42),
            )
            self.fps_text = self.font.render(
                f"FPS {int(self.clock.get_fps())}", True, "white"
            )
            self.screen.blit(self.assets["ui"], (WINDOWWIDTH - 100, 0))
            self.screen.blit(self.assets["ui_pos"], (0, 0))
            self.screen.blit(self.fps_text, (WINDOWWIDTH - 78, 9))
            self.check_for_ui()
            self.all_sprite.update()
            pygame.display.update()
