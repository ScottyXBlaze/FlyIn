import pygame
import os

from .model import HubSprite, ConnectionSprite

from ..parsers.model import DroneNetwork, Hub

from .groups import AllSprite

from typing import Any

WINDOWWIDTH, WINDOWHEIGHT = 800, 600


class Renderer:
    def __init__(self, drone_network: DroneNetwork) -> None:
        # Common
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("FlyIn - Drone Simulator")

        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.draging: bool = False
        self.last_mouse_pos: tuple[int, int] = (0, 0)

        # Text
        self.font = pygame.font.SysFont(None, 20)
        # DroneNetwork
        self.drone_network = drone_network
        self.bound = self.check_bound(self.drone_network.hubs)

        # Sprite groups
        self.all_sprite = AllSprite()

        # Assets
        self.assets: dict[str, Any] = {}

        self.running = True

        self.load_drones()
        self.load_connections()
        self.load_assets()

    def load_drones(self) -> None:
        for _, hub in self.drone_network.hubs.items():
            self.all_sprite.add(HubSprite((hub.x, hub.y), hub.metadata.color))

    def load_connections(self) -> None:
        for connection in self.drone_network.raw_connection:
            hub1 = self.drone_network.hubs.get(connection.hub1)
            hub2 = self.drone_network.hubs.get(connection.hub2)
            if hub1 is not None and hub2 is not None:
                self.all_sprite.add(ConnectionSprite(hub1, hub2, connection))

    def load_assets(self) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path_drone = os.path.join(base_dir, "assets", "drone.png")
        image_path_ui_fps = os.path.join(base_dir, "assets", "BackUI.png")
        image_path_ui_pos = os.path.join(base_dir, "assets", "BackPos.png")
        try:
            sheet = pygame.image.load(image_path_drone).convert_alpha()
            self.assets["drone"] = sheet
            sheet = pygame.image.load(image_path_ui_fps).convert_alpha()
            sheet = pygame.transform.scale(sheet, (32 * 3, 32))
            self.assets["ui"] = sheet
            sheet = pygame.transform.scale2x(
                pygame.image.load(image_path_ui_pos).convert_alpha()
            )
            self.assets["ui_pos"] = sheet
        except pygame.error as e:
            print(f"Error: {e}")

    def handle_camera(self) -> None:
        self.camera_x = min(self.bound[0], self.camera_x)
        self.camera_x = max(self.bound[2], self.camera_x)
        self.camera_y = min(self.bound[1], self.camera_y)
        self.camera_y = max(self.bound[3], self.camera_y)

    def check_bound(self, hubs: dict[str, Hub]) -> list[int]:
        maximum_x = max(hubs.values(), key=lambda x: x.x).x * 50 - 200
        maximum_y = max(hubs.values(), key=lambda x: x.y).y * 50 - 300
        minimum_x = min(hubs.values(), key=lambda x: x.x).x * 50 + 200
        minimum_y = min(hubs.values(), key=lambda x: x.y).y * 50 + 100
        return [maximum_x, maximum_y, minimum_x, minimum_y]

    def check_event(self) -> None:
        self.handle_camera()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.draging = True
                    self.last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.draging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.draging:
                    self.camera_x -= event.pos[0] - self.last_mouse_pos[0]
                    self.camera_y -= event.pos[1] - self.last_mouse_pos[1]
                    self.last_mouse_pos = event.pos

    def get_input(self, delta: float) -> None:
        keys = pygame.key.get_pressed()
        self.camera_x += 200 * delta * (keys[pygame.K_d] - keys[pygame.K_a])
        self.camera_y += 200 * delta * (keys[pygame.K_s] - keys[pygame.K_w])

        if keys[pygame.K_q]:
            self.running = False

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.check_event()
            self.get_input(dt)
            self.screen.fill("lightgray")
            self.all_sprite.draw_sprite((self.camera_x, self.camera_y))
            self.camera_text = self.font.render(
                f" X: {self.camera_x:.1f} |"
                + f"Y: {self.camera_y:.1f} {'hello':.1}",
                True,
                (182, 32, 42),
            )
            self.fps_text = self.font.render(
                f"FPS {int(self.clock.get_fps())}", True, "white"
            )
            self.screen.blit(self.assets["ui"], (WINDOWWIDTH - 100, 0))
            self.screen.blit(self.assets["ui_pos"], (0, 0))
            self.screen.blit(self.camera_text, (2, 9))
            self.screen.blit(self.fps_text, (WINDOWWIDTH - 78, 9))
            pygame.display.update()
