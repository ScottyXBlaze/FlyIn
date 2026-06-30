# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main_screen.py                                    :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/29 10:45:11 by nyramana         #+#    #+#              #
#    Updated: 2026/06/30 13:46:50 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #


"""Module that contains the main screen model to use for the rendering."""

import random

import pygame
import sys
import os

from ...models import DroneNetwork
from ..models import (
    AllSprite,
    Camera,
    DroneSprite,
    HubSprite,
    InfoSprite,
    Button,
    ConnectionSprite,
)
from ..utils import GlobalParameters, State, SpriteConverter


class Renderer(State):
    """Rendering class for the FlyIn Project."""

    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[int, int]]],
        clock: pygame.Clock,
    ) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): The main class of the project.
        """
        # Common
        _ = pygame.init()
        tmp = pygame.display.get_surface()
        self._screen: pygame.Surface = tmp if tmp else pygame.Surface((10, 10))
        self._clock: pygame.Clock = clock
        pygame.display.set_caption("FlyIn - Drone Simulator")

        # Camera
        self._camera: Camera = Camera()

        # Text
        self._font: pygame.Font = pygame.font.SysFont(None, 20)
        self._text_font: pygame.Font = pygame.font.SysFont(None, 25)

        # DroneNetwork
        self._drone_network: DroneNetwork = drone_network
        self._bound: list[int] = self._camera.check_bound(
            self._drone_network.hubs
        )
        self._drone_positions: list[dict[int, tuple[int, int]]] = path
        self._current_turn: int = -1
        self._start_pos: tuple[int, int] = (
            self._drone_network.get_start_hub.x,
            self._drone_network.get_start_hub.y,
        )
        self._end_pos: tuple[int, int] = (
            self._drone_network.get_end_hub.x,
            self._drone_network.get_end_hub.y,
        )

        # Sprite groups
        self._all_sprite: AllSprite = AllSprite()

        self._ui_sprite: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )
        self._drones: dict[int, DroneSprite] = {}

        # Assets
        self._assets: dict[str, pygame.Surface] = {}
        self._ui_info: InfoSprite = InfoSprite(
            os.path.join(
                GlobalParameters.PATH,
                "assets",
                "background",
                "ui.png",
            ),
            self._drone_network,
            heuristic_value,
        )
        self._ui_sprite.add(self._ui_info)

        self._ui_info.draw_hub_tooltip(self._drone_network.get_start_hub)

        self._signal = 0

        self._all_buttons: dict[str, Button] = {}

        self._hub_sfx = pygame.mixer.Sound(
            os.path.join(GlobalParameters.PATH, "assets", "songs", "click.mp3")
        )
        self._hub_sfx.set_volume(0.3)
        self._button_sfx = pygame.mixer.Sound(
            os.path.join(GlobalParameters.PATH, "assets", "songs", "sfx.mp3")
        )
        self._button_sfx.set_volume(0.3)

        self._load_assets()
        self._load_hubs()
        self._load_connections()
        self._load_drones()

    def _load_hubs(self) -> None:
        """Load every hub sprite."""
        for _, hub in self._drone_network.hubs.items():
            self._all_sprite.add(
                HubSprite(
                    (hub.x, hub.y),
                    hub.metadata.color,
                    hub.name,
                    self._assets["hub"],
                )
            )

    def _load_connections(self) -> None:
        """Load every connection sprite."""
        for _, connection in self._drone_network.raw_connection.items():
            hub1 = self._drone_network.hubs.get(connection.hub1)
            hub2 = self._drone_network.hubs.get(connection.hub2)
            if hub1 is not None and hub2 is not None:
                self._all_sprite.add(ConnectionSprite(hub1, hub2, connection))

    def _load_assets(self) -> None:
        """Load every assets."""
        ui_files = {
            "ui": "ui.png",
            "ui_main": "main.png",
        }
        ui_dir = os.path.join(GlobalParameters.PATH, "assets", "background")
        self.load_images(ui_dir, ui_files)
        model_files = {
            "drone": "drone.png",
            "hub": "hub.png",
        }
        model_dir = os.path.join(GlobalParameters.PATH, "assets", "model")
        self.load_images(model_dir, model_files)
        self._assets["drone"] = pygame.transform.scale2x(self._assets["drone"])
        self._assets["ui_main"] = pygame.transform.scale(
            self._assets["ui_main"],
            self._screen.get_size() if self._screen else (0, 0),
        )
        button_file = {
            "exit": ("exit.png", (10, 20)),
            "next": ("next.png", (10, 90)),
            "prev": ("prev.png", (10, 160)),
            "auto": ("auto.png", (10, 230)),
            "arev": ("arev.png", (10, 300)),
            "reset": ("reset.png", (10, 370)),
        }
        button_dir = os.path.join(
            GlobalParameters.PATH, "assets", "little_button"
        )
        for b_name, b_path in button_file.items():
            image = pygame.image.load(
                os.path.join(button_dir, b_path[0])
            ).convert_alpha()
            tmp = SpriteConverter().convert_sprite(image, (1, 3))
            self._all_buttons[b_name] = Button(
                b_path[1], tmp, self._button_sfx
            )
        for _, button in self._all_buttons.items():
            self._ui_sprite.add(button)

    def load_images(self, directory: str, images: dict[str, str]) -> None:
        """
        Load image and put them in the _assets attribute.

        Args:
            directory (str): The directory to find the image.
            images (dict[str, str]): The dictionnary that contain the
            name and path of the image.
        """
        for name, path in images.items():
            try:
                self._assets[name] = pygame.image.load(
                    os.path.join(directory, path)
                ).convert_alpha()
            except pygame.error as e:
                print(e)
                sys.exit()

    def _load_drones(self) -> None:
        """Load every drone sprite at the initial start hub position."""
        drone_sprite = self._assets["drone"]

        for drone_id in range(1, self._drone_network.nb_drones + 1):
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            offset = (random.randint(-8, 8), random.randint(-8, 8))
            drone = DroneSprite(
                drone_id,
                self._start_pos,
                drone_sprite,
                color=color,
                offset=offset,
            )
            self._drones[drone_id] = drone
            self._all_sprite.add(drone)

    def _turn_is_busy(self) -> bool:
        """Check if at least one drone is currently moving."""
        return any(drone.is_moving for drone in self._drones.values())

    def _move_to_turn(self, turn_index: int) -> None:
        """Animate every drone to a specific recorded turn."""
        if self._turn_is_busy():
            return

        if turn_index < -1 or turn_index >= len(self._drone_positions):
            return

        self._current_turn = turn_index

        if turn_index == -1:
            for drone in self._drones.values():
                drone._move_to(self._start_pos)
            return

        turn_positions = self._drone_positions[turn_index]

        for drone_id, drone in self._drones.items():
            position = turn_positions.get(drone_id, self._end_pos)
            if turn_index == 0 and drone_id not in turn_positions:
                position = self._end_pos
            elif drone_id not in turn_positions:
                position = self._end_pos

            if drone.position != position or drone.is_moving:
                drone._move_to(position)

    def _advance_turn(self) -> None:
        """Move the drones to the next recorded turn."""
        self._move_to_turn(self._current_turn + 1)
        self._all_buttons["next"].reset()

    def _previous_turn(self) -> None:
        """Move the drones to the previous recorded turn."""
        self._all_buttons["prev"].reset()
        self._move_to_turn(self._current_turn - 1)

    def _handle_camera(self) -> None:
        """Handle the camera to not go too far."""
        self._camera._camera_x = min(self._bound[0], self._camera._camera_x)
        self._camera._camera_x = max(self._bound[2], self._camera._camera_x)
        self._camera._camera_y = min(self._bound[1], self._camera._camera_y)
        self._camera._camera_y = max(self._bound[3], self._camera._camera_y)

    def _all_reset(self) -> None:
        """Reset all the button state."""
        for _, button in self._all_buttons.items():
            button.reset()

    def _check_event(self) -> None:
        """Check some event."""
        self._handle_camera()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._signal = 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self._button_sfx.play()
                    self._all_reset()
                    self._advance_turn()
                elif event.key == pygame.K_p:
                    self._button_sfx.play()
                    self._all_reset()
                    self._previous_turn()
                elif event.key == pygame.K_r:
                    self._button_sfx.play()
                    self._all_reset()
                    self._reset_game()
                elif event.key == pygame.K_a:
                    self._button_sfx.play()
                    self._all_reset()
                    self._all_buttons["auto"]._is_working = True
                elif event.key == pygame.K_x:
                    self._button_sfx.play()
                    self._all_reset()
                    self._all_buttons["arev"]._is_working = True
                elif event.key == pygame.K_q:
                    self._button_sfx.play()
                    self._all_buttons["exit"]._is_working = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._camera._draging = True
                    self._camera._last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._camera._draging = False

            elif event.type == pygame.MOUSEMOTION:
                if self._camera._draging:
                    self._camera._camera_x -= (
                        event.pos[0] - self._camera._last_mouse_pos[0]
                    )
                    self._camera._camera_y -= (
                        event.pos[1] - self._camera._last_mouse_pos[1]
                    )
                    self._camera._last_mouse_pos = event.pos

    def _get_input(self, delta: float) -> None:
        """
        Get the input from the user.

        Args:
            delta (float): Delta time.
        """
        keys = pygame.key.get_pressed()
        self._camera._camera_x += int(
            200 * delta * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        )
        self._camera._camera_y += int(
            200 * delta * (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        )

        if keys[pygame.K_q]:
            self.running = False

    def _check_for_ui(self) -> None:
        """Check if we need to show the UI or not."""
        hub = self._check_over_pos()
        if hub is not None:
            self._hub_sfx.play()
            self._ui_info.draw_hub_tooltip(self._drone_network.hubs.get(hub))

    def _check_over_pos(self) -> str | None:
        """
        Check if the mouse is over a hub.

        Returns:
            str: the name of the hub or None.
        """
        mouse_pos = pygame.mouse.get_pos()
        center_x = GlobalParameters.WINDOWWIDTH // 2
        center_y = GlobalParameters.WINDOWHEIGHT // 2

        mouse_world_x = mouse_pos[0] - center_x + self._camera._camera_x
        mouse_world_y = mouse_pos[1] - center_y + self._camera._camera_y
        for hub in self._all_sprite.sprites():
            if isinstance(hub, HubSprite):
                if hub.is_hovered((mouse_world_x, mouse_world_y)):
                    return hub._name
        return None

    def reset(self) -> None:
        """Reset some state of the screen."""
        self._signal = 0
        self._all_buttons["exit"].reset()
        self._all_buttons["next"].reset()
        self._all_buttons["prev"].reset()

    def _reset_game(self) -> None:
        """Reset the turn of the progam (game XD)."""
        self._move_to_turn(-1)
        self._all_buttons["reset"].reset()

    def run(self, dt: float) -> int:
        """Run the rendering."""
        # Check Event and input
        self._check_event()
        self._get_input(dt)
        if not self._screen:
            return 0

        # Show the background
        self._screen.blit(self._assets["ui_main"], (0, 0))

        # Draw every sprite
        self._all_sprite.draw_sprite(
            (self._camera._camera_x, self._camera._camera_y)
        )

        # Draw the FPS
        fps_text = self._font.render(
            f"FPS {int(self._clock.get_fps())}", True, "white"
        )
        self._screen.blit(fps_text, (GlobalParameters.WINDOWWIDTH - 78, 9))

        turn_text = self._text_font.render(
            f"Turn: {self._current_turn + 1}", True, "white"
        )
        self._screen.blit(
            turn_text, (GlobalParameters.WINDOWWIDTH // 2 - 10, 140)
        )

        camera_text = self._text_font.render(
            f"X:{self._camera._camera_x} Y:{self._camera._camera_y}",
            True,
            "white",
        )
        self._screen.blit(
            camera_text,
            (
                GlobalParameters.WINDOWWIDTH - 120,
                GlobalParameters.WINDOWHEIGHT - 40,
            ),
        )
        # Check if the mouse was pressed
        if pygame.mouse.get_just_pressed()[0]:
            self._check_for_ui()

        # Update everything

        if self._all_buttons["reset"].update_sprite(dt, 1):
            self._reset_game()
        elif self._all_buttons["next"].update_sprite(
            dt, 1
        ) or self._all_buttons["auto"].update_sprite(dt, 1):
            self._advance_turn()
        elif self._all_buttons["prev"].update_sprite(
            dt, 1
        ) or self._all_buttons["arev"].update_sprite(dt, 1):
            self._previous_turn()
        elif self._all_buttons["exit"].update_sprite(dt, 2):
            return 2
        self._all_sprite.update(dt)
        self._ui_sprite.update()
        self._ui_sprite.draw(self._screen)
        pygame.display.update()
        return self._signal
