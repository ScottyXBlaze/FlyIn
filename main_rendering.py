# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main_rendering.py                                 :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananari>  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/19 14:14:47 by nyramana         #+#    #+#              #
#    Updated: 2026/06/19 16:06:10 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

import random
import sys
import time
from typing import override

import pygame

from main_model import DroneNetwork
from main_rendering_models import (
    AllSprite,
    Button,
    DroneSprite,
    HubSprite,
    InfoSprite,
    Camera,
    ConnectionSprite,
)
from main_rendering_utils import GlobalParameters, SpriteConverter, State


class Home(State):
    """Home screen for the rendering."""

    def __init__(self) -> None:
        """Everything starts here."""
        self.running: bool = True
        self.sprites: dict[str, pygame.Surface] = {}
        self.frames: dict[str, list[pygame.Surface]] = {}
        self.signal: int = 0
        tmp: pygame.Surface | None = pygame.display.get_surface()
        self.screen: pygame.Surface = tmp if tmp else pygame.Surface((10, 10))
        self.init_sprites()

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )

        self.button_sfx: pygame.Sound = pygame.mixer.Sound(
            "song_click_start.wav"
        )
        self.button_sfx.set_volume(0.2)

        self.button_start: Button = Button(
            (
                (GlobalParameters.WINDOWWIDTH // 2 - 200),
                GlobalParameters.WINDOWHEIGHT - 400,
            ),
            self.frames["start"],
            self.button_sfx,
        )

        self.button_end: Button = Button(
            (
                (GlobalParameters.WINDOWWIDTH // 2 - 200),
                GlobalParameters.WINDOWHEIGHT - 250,
            ),
            self.frames["exit"],
            self.button_sfx,
        )
        self.all_sprites.add(self.button_start, self.button_end)

        if self.screen:
            self.back: pygame.Surface = self.screen.copy()
            self.background: pygame.Surface = pygame.Surface(
                self.screen.get_frect().size
            ).convert_alpha()
            self.background = pygame.image.load("rendering_back_main2.png")

            self.background = pygame.transform.scale(
                self.background,
                self.screen.get_size() if self.screen else (0, 0),
            )

    def init_sprites(self) -> None:
        """Initialize every sprite for the screen."""
        sprites = {
            "logo": "rendering_logo.png",
            "exit": "rendering_button_exit.png",
            "start": "rendering_button_start.png",
        }
        for name, path in sprites.items():
            self.sprites[name] = pygame.image.load(path)
        for name, sprite in self.sprites.items():
            self.sprites[name] = pygame.transform.scale2x(sprite)

        for name, sprite in self.sprites.items():
            if name == "logo":
                continue
            self.frames[name] = SpriteConverter().convert_sprite(
                sprite, (1, 3)
            )

    def check_event(self) -> None:
        """Check different event and handle them."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.signal = 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.button_start.is_working = True
                elif event.key == pygame.K_ESCAPE:
                    self.button_end.is_working = True

    def render(self) -> None:
        """Render surface in the screen."""
        if not self.screen:
            return
        if self.back:
            _ = self.screen.blit(self.back)
            _ = self.screen.blit(self.background)
        _ = self.screen.blit(
            self.sprites["logo"], (GlobalParameters.WINDOWWIDTH // 2 - 200, 50)
        )
        _ = self.all_sprites.draw(self.screen)
        pygame.display.update()

    @override
    def reset(self) -> None:
        """Reset some state of the screen."""
        self.signal = 0
        self.button_start.reset()
        self.button_end.reset()

    @override
    def run(self, dt: float) -> int:
        """Run the home program (should be called every frame)."""
        signal = self.button_end.update_sprite(dt, 1)
        if not signal:
            signal = 0
            signal = self.button_start.update_sprite(dt, 2)
            if not signal:
                self.signal = 0
            else:
                _ = self.button_sfx.play()
                self.signal = signal
        else:
            _ = self.button_sfx.play()
            time.sleep(0.3)
            self.signal = signal
        self.check_event()
        self.render()

        return self.signal if self.signal else 0


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
        self.screen: pygame.Surface = tmp if tmp else pygame.Surface((10, 10))
        self.clock: pygame.Clock = clock
        pygame.display.set_caption("FlyIn - Drone Simulator")

        # Camera
        self.camera: Camera = Camera()

        # Text
        self.font: pygame.Font = pygame.font.SysFont(None, 20)
        self.text_font: pygame.Font = pygame.font.SysFont(None, 25)

        # DroneNetwork
        self.drone_network: DroneNetwork = drone_network
        self.bound: list[int] = self.camera.check_bound(
            self.drone_network.hubs
        )
        self.drone_positions: list[dict[int, tuple[int, int]]] = path
        self.current_turn: int = -1
        self.start_pos: tuple[int, int] = (
            self.drone_network.get_start_hub.x,
            self.drone_network.get_start_hub.y,
        )
        self.end_pos: tuple[int, int] = (
            self.drone_network.get_end_hub.x,
            self.drone_network.get_end_hub.y,
        )

        # Sprite groups
        self.all_sprite: AllSprite = AllSprite()

        self.ui_sprite: pygame.sprite.Group[pygame.sprite.Sprite] = (
            pygame.sprite.Group()
        )
        self.drones: dict[int, DroneSprite] = {}

        # Assets
        self.assets: dict[str, pygame.Surface] = {}
        self.ui_info: InfoSprite = InfoSprite(
            "rendering_back_ui.png", self.drone_network, heuristic_value
        )
        self.ui_sprite.add(self.ui_info)

        self.ui_info.draw_hub_tooltip(self.drone_network.get_start_hub)

        self.signal = 0

        self.all_buttons: dict[str, Button] = {}

        self.hub_sfx = pygame.mixer.Sound("song_button_click.mp3")
        self.hub_sfx.set_volume(0.3)
        self.button_sfx = pygame.mixer.Sound("song_button_sfx.mp3")
        self.button_sfx.set_volume(0.3)

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
        image_file = {
            "drone": "rendering_drone.png",
            "ui": "rendering_back_ui.png",
            "ui_main": "rendering_back_main.png",
            "hub": "rendering_hub.png",
            "exit": "rendering_buttonlexit.png",
        }
        for name, path in image_file.items():
            try:
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
            "exit": ("rendering_buttonlexit.png", (10, 20)),
            "next": ("rendering_buttonlnext.png", (10, 90)),
            "prev": ("rendering_buttonlprevious.png", (10, 160)),
            "auto": ("rendering_buttonlauto.png", (10, 230)),
            "arev": ("rendering_buttonlarev.png", (10, 300)),
            "reset": ("rendering_buttonlreset.png", (10, 370)),
        }
        for b_name, b_path in button_file.items():
            image = pygame.image.load(b_path[0]).convert_alpha()
            tmp = SpriteConverter().convert_sprite(image, (1, 3))
            self.all_buttons[b_name] = Button(b_path[1], tmp, self.button_sfx)
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
            drone = DroneSprite(
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
        self.move_to_turn(self.current_turn + 1)
        self.all_buttons["next"].reset()

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

    def all_reset(self) -> None:
        """Reset all the button state."""
        for _, button in self.all_buttons.items():
            button.reset()

    def check_event(self) -> None:
        """Check some event."""
        self.handle_camera()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.signal = 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.button_sfx.play()
                    self.all_reset()
                    self.advance_turn()
                elif event.key == pygame.K_p:
                    self.button_sfx.play()
                    self.all_reset()
                    self.previous_turn()
                elif event.key == pygame.K_r:
                    self.button_sfx.play()
                    self.all_reset()
                    self.reset_game()
                elif event.key == pygame.K_a:
                    self.button_sfx.play()
                    self.all_reset()
                    self.all_buttons["auto"].is_working = True
                elif event.key == pygame.K_x:
                    self.button_sfx.play()
                    self.all_reset()
                    self.all_buttons["arev"].is_working = True
                elif event.key == pygame.K_q:
                    self.button_sfx.play()
                    self.all_buttons["exit"].is_working = True

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
            200 * delta * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        )
        self.camera.camera_y += int(
            200 * delta * (keys[pygame.K_DOWN] - keys[pygame.K_UP])
        )

        if keys[pygame.K_q]:
            self.running = False

    def check_for_ui(self) -> None:
        """Check if we need to show the UI or not."""
        hub = self.check_over_pos()
        if hub is not None:
            self.hub_sfx.play()
            self.ui_info.draw_hub_tooltip(self.drone_network.hubs.get(hub))

    def check_over_pos(self) -> str | None:
        """
        Check if the mouse is over a hub.

        Returns:
            str: the name of the hub or None.
        """
        mouse_pos = pygame.mouse.get_pos()
        center_x = GlobalParameters.WINDOWWIDTH // 2
        center_y = GlobalParameters.WINDOWHEIGHT // 2

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
        self.screen.blit(self.fps_text, (GlobalParameters.WINDOWWIDTH - 78, 9))

        self.turn_text = self.text_font.render(
            f"Turn: {self.current_turn + 1}", True, "white"
        )
        self.screen.blit(
            self.turn_text, (GlobalParameters.WINDOWWIDTH // 2 - 10, 140)
        )

        self.camera_text = self.text_font.render(
            f"X:{self.camera.camera_x} Y:{self.camera.camera_y}",
            True,
            "white",
        )
        self.screen.blit(
            self.camera_text,
            (
                GlobalParameters.WINDOWWIDTH - 120,
                GlobalParameters.WINDOWHEIGHT - 40,
            ),
        )
        # Check if the mouse was pressed
        if pygame.mouse.get_just_pressed()[0]:
            self.check_for_ui()

        # Update everything

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
        self.all_sprite.update(dt)
        self.ui_sprite.update()
        self.ui_sprite.draw(self.screen)
        pygame.display.update()
        return self.signal


class StateManager:
    """Class to manage multiple screen or display and change them."""

    def __init__(
        self,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
        path: list[dict[int, tuple[int, int]]],
    ) -> None:
        """
        Everything starts here.

        Args:
            drone_network (DroneNetwork): Class that contain every variables.
            heuristic_value (dict[str, int]): heuristic value for each hub.
            path (list[dict[int, tuple[int, int]]]): Path of each drone.
        """
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(
            (GlobalParameters.WINDOWWIDTH, GlobalParameters.WINDOWHEIGHT)
        )
        self.clock = pygame.time.Clock()

        pygame.display.set_icon(pygame.image.load("rendering_main_logo.png"))

        pygame.mixer.music.load("song_clouds.ogg")
        pygame.mixer.music.play(-1)

        self.main_program = Renderer(
            drone_network, heuristic_value, path, self.clock
        )
        self.home_program = Home()
        self.program: State = self.home_program

    def change_program(self) -> None:
        """Change the program."""
        if self.program == self.main_program:
            self.program = self.home_program
        else:
            self.program = self.main_program

    def run(self) -> None:
        """Run the program."""
        while True:
            dt = self.clock.tick(60) / 1000
            signal = self.program.run(dt)
            if signal == 1:
                self.quit()
            elif signal == 2:
                self.change_program()
                self.program.reset()

    def quit(self) -> None:
        """Quit the program."""
        pygame.quit()
        sys.exit(0)
