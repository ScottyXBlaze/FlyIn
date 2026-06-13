# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    rendering.py                                      :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:50:02 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 11:56:58 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the main rendering class."""

import os
import random
import sys

import pygame

from .. import DroneNetwork
from .base_state import State
from .camera import Camera
from .drone import Drone
from .groups import AllSprite
from .home import Button
from .model import ConnectionSprite, HubSprite, InfoSprite
from .settings import WINDOWHEIGHT, WINDOWWIDTH


class Renderer(State):
    """Rendering class for the FlyIn Project."""

    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[float, float]]],
        clock: pygame.Clock,
    ) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): The main class of the project.
        """
        # Common
        pygame.init()
        self.screen = pygame.display.get_surface()
        self.clock = clock
        pygame.display.set_caption("FlyIn - Drone Simulator")

        # Camera
        self.camera = Camera()

        # Text
        self.font = pygame.font.SysFont(None, 20)
        self.text_font = pygame.font.SysFont(None, 25)

        # DroneNetwork
        self.drone_network = drone_network
        self.bound = self.camera.check_bound(self.drone_network.hubs)
        self.drone_positions = path
        self.current_turn = -1
        self.start_pos = (
            self.drone_network.get_start_hub.x,
            self.drone_network.get_start_hub.y,
        )
        self.end_pos = (
            self.drone_network.get_end_hub.x,
            self.drone_network.get_end_hub.y,
        )

        # Sprite groups
        self.all_sprite = AllSprite()

        self.ui_sprite: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )
        self.drones: dict[int, Drone] = {}

        # Assets
        self.assets: dict[str, pygame.Surface] = {}
        self.ui_info = InfoSprite(
            "BackUI.png", self.drone_network, heuristic_value
        )
        self.ui_sprite.add(self.ui_info)

        self.ui_info.draw_hub_tooltip(self.drone_network.get_start_hub)

        self.signal = 0

        self.all_buttons: dict[str, Button] = {}

        self.load_assets()
        self.load_hubs()
        self.load_connections()
        self.load_drones()

    def load_hubs(self) -> None:
        """Load every hub sprite."""
        for _, hub in self.drone_network.hubs.items():
            self.all_sprite.add(
                HubSprite(
                    (hub.x, hub.y),
                    hub.metadata.color,
                    hub.name,
                    self.assets["hub"],
                )
            )

    def load_connections(self) -> None:
        """Load every connection sprite."""
        for _, connection in self.drone_network.raw_connection.items():
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
            "ui_main": "BackMain.png",
            "hub": "Hub.png",
            "exit": "LittleExit.png",
        }
        for name, path in image_file.items():
            try:
                path = os.path.join(base_dir, "assets", path)
                self.assets[name] = pygame.image.load(path).convert_alpha()
            except pygame.error as e:
                print(e)
                sys.exit()

        self.assets["drone"] = pygame.transform.scale2x(self.assets["drone"])
        self.assets["ui_main"] = pygame.transform.scale(
            self.assets["ui_main"],
            self.screen.get_size() if self.screen else (0, 0),
        )
        button_file = {
            "exit": ("LittleExit.png", (10, 20)),
            "next": ("LittleExit.png", (10, 90)),
            "prev": ("LittleExit.png", (10, 160)),
            "auto": ("LittleExit.png", (10, 230)),
            "arev": ("LittleExit.png", (10, 300)),
            "reset": ("LittleExit.png", (10, 370)),
        }
        for b_name, b_path in button_file.items():
            self.all_buttons[b_name] = Button(
                b_path[1],
                [
                    pygame.image.load(
                        os.path.join(base_dir, "assets", b_path[0])
                    ).convert_alpha()
                ],
            )
        for _, button in self.all_buttons.items():
            self.ui_sprite.add(button)

    def load_drones(self) -> None:
        """Load every drone sprite at the initial start hub position."""
        drone_sprite = self.assets["drone"]

        for drone_id in range(1, self.drone_network.nb_drones + 1):
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            offset = (random.randint(-8, 8), random.randint(-8, 8))
            drone = Drone(
                drone_id,
                self.start_pos,
                drone_sprite,
                color=color,
                offset=offset,
            )
            self.drones[drone_id] = drone
            self.all_sprite.add(drone)

    def turn_is_busy(self) -> bool:
        """Check if at least one drone is currently moving."""
        return any(drone.is_moving for drone in self.drones.values())

    def move_to_turn(self, turn_index: int) -> None:
        """Animate every drone to a specific recorded turn."""
        if self.turn_is_busy():
            return

        if turn_index < -1 or turn_index >= len(self.drone_positions):
            return

        self.current_turn = turn_index

        if turn_index == -1:
            for drone in self.drones.values():
                drone.move_to(self.start_pos)
            return

        turn_positions = self.drone_positions[turn_index]

        for drone_id, drone in self.drones.items():
            position = turn_positions.get(drone_id, self.end_pos)
            if turn_index == 0 and drone_id not in turn_positions:
                position = self.end_pos
            elif drone_id not in turn_positions:
                position = self.end_pos
            if drone.position != position or drone.is_moving:
                drone.move_to(position)

    def advance_turn(self) -> None:
        """Move the drones to the next recorded turn."""
        self.all_buttons["next"].reset()
        self.move_to_turn(self.current_turn + 1)

    def previous_turn(self) -> None:
        """Move the drones to the previous recorded turn."""
        self.all_buttons["prev"].reset()
        self.move_to_turn(self.current_turn - 1)

    def handle_camera(self) -> None:
        """Handle the camera to not go too far."""
        self.camera.camera_x = min(self.bound[0], self.camera.camera_x)
        self.camera.camera_x = max(self.bound[2], self.camera.camera_x)
        self.camera.camera_y = min(self.bound[1], self.camera.camera_y)
        self.camera.camera_y = max(self.bound[3], self.camera.camera_y)

    def check_event(self) -> None:
        """Check some event."""
        self.handle_camera()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.signal = 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.advance_turn()
                elif event.key == pygame.K_b:
                    self.previous_turn()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.signal = 2
                # elif event.key == pygame.K_r:
                # self.run_to_end()

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
            self.ui_info.draw_hub_tooltip(self.drone_network.hubs.get(hub))

    def check_over_pos(self) -> str | None:
        """
        Check if the mouse is over a hub.

        Returns:
            str: the name of the hub or None.
        """
        mouse_pos = pygame.mouse.get_pos()
        center_x = WINDOWWIDTH // 2
        center_y = WINDOWHEIGHT // 2

        mouse_world_x = mouse_pos[0] - center_x + self.camera.camera_x
        mouse_world_y = mouse_pos[1] - center_y + self.camera.camera_y
        for hub in self.all_sprite.sprites():
            if isinstance(hub, HubSprite):
                if hub.is_hovered((mouse_world_x, mouse_world_y)):
                    return hub.name
        return None

    def reset(self) -> None:
        """Reset some state of the screen."""
        self.signal = 0
        self.all_buttons["exit"].reset()
        self.all_buttons["next"].reset()
        self.all_buttons["prev"].reset()

    def reset_game(self) -> None:
        """Reset the turn of the progam (game XD)."""
        self.move_to_turn(-1)
        self.all_buttons["reset"].reset()

    def run(self, dt: float) -> int:
        """Run the rendering."""
        # Check Event and input
        self.check_event()
        self.get_input(dt)
        if not self.screen:
            return 0

        # Show the background
        self.screen.blit(self.assets["ui_main"], (0, 0))

        # Draw every sprite
        self.all_sprite.draw_sprite(
            (self.camera.camera_x, self.camera.camera_y)
        )

        # Draw the FPS
        self.fps_text = self.font.render(
            f"FPS {int(self.clock.get_fps())}", True, "white"
        )
        self.screen.blit(self.fps_text, (WINDOWWIDTH - 78, 9))

        self.turn_text = self.text_font.render(
            f"Turn: {self.current_turn + 1}", True, "white"
        )
        self.screen.blit(self.turn_text, (WINDOWWIDTH // 2 - 10, 140))

        self.camera_text = self.text_font.render(
            f"X:{self.camera.camera_x} Y:{self.camera.camera_y}",
            True,
            "white",
        )
        self.screen.blit(
            self.camera_text, (WINDOWWIDTH - 120, WINDOWHEIGHT - 40)
        )
        # Check if the mouse was pressed
        if pygame.mouse.get_just_pressed()[0]:
            self.check_for_ui()

        # Update everything
        self.all_sprite.update(dt)
        self.ui_sprite.update()
        if self.all_buttons["reset"].update_sprite(dt, 1):
            self.reset_game()
        elif self.all_buttons["next"].update_sprite(dt, 1) or self.all_buttons[
            "auto"
        ].update_sprite(dt, 1):
            self.advance_turn()
        elif self.all_buttons["prev"].update_sprite(dt, 1) or self.all_buttons[
            "arev"
        ].update_sprite(dt, 1):
            self.previous_turn()
        elif self.all_buttons["exit"].update_sprite(dt, 2):
            return 2
        self.ui_sprite.draw(self.screen)
        pygame.display.update()
        return self.signal
