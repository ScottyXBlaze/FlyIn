import pygame

from .model import HubSprite, ConnectionSprite

from ..parsers.model import DroneNetwork

from .groups import AllSprite

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
        self.font = pygame.font.SysFont(None, 24)
        # DroneNetwork
        self.drone_network = drone_network

        # Sprite groups
        self.all_sprite = AllSprite()

        self.running = True
        self.load_drones()
        self.load_connections()

    def load_drones(self) -> None:
        for _, hub in self.drone_network.hubs.items():
            self.all_sprite.add(HubSprite((hub.x, hub.y), hub.metadata.color))

    def load_connections(self) -> None:
        for connection in self.drone_network.raw_connection:
            hub1 = self.drone_network.hubs.get(connection.hub1)
            hub2 = self.drone_network.hubs.get(connection.hub2)
            if hub1 is not None and hub2 is not None:
                self.all_sprite.add(ConnectionSprite(hub1, hub2, connection))

    def check_event(self) -> None:
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

    def get_input(self) -> None:
        pass

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.check_event()
            self.get_input()
            self.screen.fill("lightgray")
            self.all_sprite.draw((self.camera_x, self.camera_y))
            self.camera_text = self.font.render(
                f"Camera X: {self.camera_x} | Camera Y: {self.camera_y}",
                True,
                "darkblue",
            )
            self.fps_text = self.font.render(
                f"FPS {int(self.clock.get_fps())}", True, "darkblue"
            )
            self.screen.blit(self.camera_text, (10, 10))
            self.screen.blit(self.fps_text, (WINDOWWIDTH - 60, 10))
            pygame.display.update()
