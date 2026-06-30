# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main_rendering_models.py                          :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:40 by nyramana         #+#    #+#              #
#    Updated: 2026/06/24 15:48:23 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Module that contain the class to easily have a camera."""

import random
import sys
from typing import Any, override

import pygame

from main_model import Connection, DroneNetwork, Hub
from main_rendering_utils import (
    GlobalParameters,
    SpriteConverter,
)


class HubSprite(pygame.sprite.Sprite):
    """Sprite model for everu hub."""

    def __init__(
        self,
        pos: tuple[int, int],
        color: str,
        name: str,
        sprite: pygame.Surface,
    ) -> None:
        """
        Every initialization.

        Args:
            pos (tuple[int, int]): Position of the hub.
            color (str): Color of the hub.
            name (str): Name of the Hub.
        """
        super().__init__()
        self._name = name
        self._pos: tuple[int, int] = self._transform_pos(pos)
        self.image = sprite.copy()
        self.image = pygame.transform.scale(
            self.image,
            (GlobalParameters.CELL_SIZE, GlobalParameters.CELL_SIZE),
        )
        self.rect = self.image.get_frect(topleft=self._pos)
        self._color_name = color
        self._hue = 0
        if color != "rainbow":
            self.image = self._tint_sprite(
                self.image,
                pygame.color.THECOLORS.get(color.lower(), (0, 0, 0, 0)),
            )

    @staticmethod
    def _tint_sprite(
        sprite: pygame.Surface, color: tuple[int, int, int, int]
    ) -> pygame.Surface:
        """Apply a light color tint to the drone sprite."""
        image = sprite.copy()
        tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint.fill(color)
        image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    @staticmethod
    def _transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """
        Transform the index position into a real position in the screen.

        Args:
            pos (tuple[int, int]):  Original position of the hub.
        Returns:
            tuple: The transformed position.
        """
        return pos[0] * (
            GlobalParameters.CELL_SIZE + GlobalParameters.OFFSET[0]
        ), pos[1] * (GlobalParameters.CELL_SIZE + GlobalParameters.OFFSET[1])

    def is_hovered(self, mouse_world: tuple[int, int]) -> bool:
        """
        Check if the mouse is in the hub.

        Args:
            mouse_world (tuple[int, int]): The position of the mouse.
        """
        world_x = self._pos[0]
        world_y = self._pos[1]

        world_rect = pygame.Rect(
            0, 0, GlobalParameters.CELL_SIZE, GlobalParameters.CELL_SIZE
        )
        world_rect.topleft = (world_x, world_y)

        return world_rect.collidepoint(mouse_world)

    def update(self) -> None:
        """Update the color of the hub."""
        if self._color_name == "rainbow":
            self.color = pygame.Color(0, 0, 0)
            self.color.hsva = (self._hue, 100, 100, 100)
            if self.image:
                self.image = self._tint_sprite(
                    self.image,
                    (self.color.r, self.color.g, self.color.b, self.color.a),
                )
            self._hue += 4
            if self._hue >= 360:
                self._hue = 0


class ConnectionSprite(pygame.sprite.Sprite):
    """Sprite model for every connection."""

    def __init__(self, hub1: Hub, hub2: Hub, connection: Connection) -> None:
        """
        Every initialization starts here.

        Args:
            hub1 (Hub): The first hub for the connection.
            hub2 (Hub): The second hub for the connection.
            connection (Connection): The connection class for the two hubs.
        """
        super().__init__()

        self._hub1, self._hub2 = hub1, hub2
        self._connection = connection

        self._width = abs(hub1.x - hub2.x)
        self._height = abs(hub1.y - hub2.y)

        self._original_pos = self._transform_pos((self._width, self._height))
        self.image = pygame.Surface(
            (
                self._original_pos[0] + 10,
                self._original_pos[1] + 10,
            )
        ).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        position = self._transform_pos(
            (
                min(self._hub1.x, self._hub2.x),
                min(self._hub1.y, self._hub2.y),
            )
        )
        self.rect = self.image.get_frect(
            topleft=(
                position[0] + GlobalParameters.CELL_SIZE // 2,
                position[1] + GlobalParameters.CELL_SIZE // 2,
            ),
        )

        self._draw_line()

    @staticmethod
    def _transform_pos(pos: tuple[int, int]) -> tuple[int, int]:
        """Transform the original position to match the screen."""
        return pos[0] * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        ), pos[1] * (GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE)

    def _draw_line(self) -> None:
        """Draw the Line that connect the two hub."""
        if self.image is not None:
            start_pos = (
                0 if self._hub1.x <= self._hub2.x else self._width,
                0 if self._hub1.y <= self._hub2.y else self._height,
            )
            end_pos = (
                0 if self._hub1.x >= self._hub2.x else self._width,
                0 if self._hub1.y >= self._hub2.y else self._height,
            )
            pygame.draw.line(
                self.image,
                (
                    (50 * self._connection.max_link_capacity) % 256,
                    (30 * self._connection.max_link_capacity) % 256,
                    (20 * self._connection.max_link_capacity) % 256,
                    255,
                ),
                self._transform_pos(end_pos),
                self._transform_pos(start_pos),
                self._connection.max_link_capacity * 4,
            )


class InfoSprite(pygame.sprite.Sprite):
    """Basic Information sprite.

    Attributes:
        frames: Every frame of the image.
        frame_size: The size of each frame.
        screen: The screen size.
        image: The actual sprite.
        drone_network: The DroneNetwork class.
        rect: The rect of the sprite
    """

    def __init__(
        self,
        sprite_name: str,
        drone_network: DroneNetwork,
        heuristic_value: dict[str, int | float],
    ) -> None:
        """Everything starts here.

        Args:
            sprite_name: The name of the sprite file.
            drone_network: The DroneNetwork class.
        """
        super().__init__()
        self._frames = SpriteConverter().convert_sprite(
            pygame.image.load(sprite_name),
            (3, 3),
        )
        self._frame_size = self._frames[0].size
        self._screen = pygame.display.get_surface()
        if self._screen is None:
            return
        self.image = pygame.Surface(
            (self._screen.size[0] - 192, 128)
        ).convert_alpha()
        self.image.fill((0, 0, 0, 10))

        self._font_name = "font_JetBrainsMono.ttf"
        self._font = pygame.font.Font(self._font_name, 15)

        self._drone_network = drone_network
        self._heuristic_value = heuristic_value
        self.rect = self.image.get_frect(
            center=(self._screen.size[0] // 2, 68)
        )
        self._build_info((self._screen.size[0] - 192, 128))

    def _build_info(self, size: tuple[int, int]) -> None:
        """Build the info bubble sprite.

        Args:
            size: The size of the sprite.
        """
        if self.image is None:
            return
        for row in range(0, size[0], self._frame_size[0]):
            for col in range(0, size[1], self._frame_size[1]):
                if col == 0 and row == 0:
                    self.image.blit(self._frames[0], (row, col))
                elif row == 0 and col >= size[1] - self._frame_size[1]:
                    self.image.blit(self._frames[2], (row, col))
                elif (
                    col >= size[1] - self._frame_size[1]
                    and row >= size[0] - self._frame_size[0]
                ):
                    pass
                elif col == 0 and row >= size[0] - self._frame_size[0]:
                    pass
                elif col == 0:
                    self.image.blit(self._frames[3], (row, col))
                elif col >= size[1] - self._frame_size[1]:
                    self.image.blit(self._frames[5], (row, col))
                elif row == 0:
                    self.image.blit(self._frames[1], (row, col))
                elif row >= size[0] - self._frame_size[0]:
                    self.image.blit(self._frames[7], (row, col))
                else:
                    self.image.blit(self._frames[4], (row, col))
        # Always print the right one
        self.image.blit(
            self._frames[6], self._frames[6].get_frect(topright=(size[0], 0))
        )
        self.image.blit(
            self._frames[8], self._frames[8].get_frect(bottomright=(size))
        )

    def draw_hub_tooltip(self, hub: Hub | None) -> None:
        """Draw the information in the sprite.

        Args:
            hub: The hub to show.
        """
        if self._screen is None:
            return
        self._build_info((self._screen.size[0] - 192, 128))
        real_hub = hub
        if not real_hub:
            return
        connections = ", ".join(
            self._drone_network.connections.get(real_hub.name, {})
        )
        if len(connections) > 88:
            connections = "Too much to show..."
        lines = [
            f"Name: {real_hub.name}",
            f"Pos: x:{real_hub.x} y:{real_hub.y}",
            f"ZoneType: {real_hub.metadata.zone.name.capitalize()}",
            f"Color: {real_hub.metadata.color.capitalize()}",
            f"Max Drone for hub: {real_hub.metadata.max_drones}",
            f"Current Drone: {real_hub.current_drone}",
            f"Total drone: {self._drone_network.nb_drones}",
            f"Connected to: {connections}",
            f"H value: {self._heuristic_value.get(real_hub.name)}",
        ]

        text_surfaces = [
            self._font.render(line, True, (255, 255, 255)) for line in lines
        ]
        if self.image is None:
            return
        image_size = self.image.get_size()
        position_x = [i for i in range(25, image_size[0], image_size[0] // 3)]
        position_y = [i for i in range(20, image_size[1], image_size[1] // 4)]

        # Print every text in their position
        self.image.blit(text_surfaces[0], (position_x[0], position_y[0]))
        self.image.blit(text_surfaces[1], (position_x[0], position_y[1]))
        self.image.blit(text_surfaces[2], (position_x[1], position_y[0]))
        self.image.blit(text_surfaces[3], (position_x[1], position_y[1]))
        self.image.blit(text_surfaces[4], (position_x[2], position_y[1]))
        self.image.blit(text_surfaces[6], (position_x[2], position_y[0]))
        self.image.blit(text_surfaces[7], (position_x[0], position_y[2]))


class DroneSprite(pygame.sprite.Sprite):
    """Drone Class for rendering."""

    def __init__(
        self,
        id: int,
        position: tuple[int, int],
        sprite: pygame.Surface,
        color: tuple[int, int, int] | None = None,
        offset: tuple[int, int] = (0, 0),
    ):
        """
        Everything starts here.

        Args:
            id (int): The ID of the drone.
            position (tuple[int, int]): The position of the drone.
            sprite (pygame.Surface): The sprite of the drone.
            color (tuple[int, int]): The color of the drone.
            offset (tuple[int, int]): The offset of the drone.
        """
        super().__init__()
        # Base attribute for each drone.
        self._drone_id = id
        self._grid_pos = position
        self._pixel_offset = offset

        # frame of the drone
        self._frames = SpriteConverter().convert_sprite(sprite, (2, 1))
        if color is not None:
            self._frames = [
                self._tint_sprite(frame, color) for frame in self._frames
            ]

        self._px, self._py = self._grid_to_px(*position, self._pixel_offset)

        # Animation variable
        self._anim_speed: float = 0.3
        self._anim_active: bool = False
        self._anim_elapsed: float = 0.0

        # Animation speed
        self._frame_index: int = 0
        self._frame_elapsed: float = 0.0
        self._frame_speed: float = random.uniform(0.05, 0.2)

        # Position end to start
        self._anim_start: tuple[float, float] = (self._px, self._py)
        self._anim_end: tuple[float, float] = (self._px, self._py)

        # Image and rect of the sprite
        self.image = self._frames[self._frame_index]
        self.rect = self.image.get_frect(center=(self._px, self._py))

    def _grid_to_px(
        self, gx: int, gy: int, offset: tuple[int, int] = (0, 0)
    ) -> tuple[float, float]:
        """
        Tranform the grid position into a pixel position.

        Args:
            gx (int): Grid position in x.
            gy (int): Grid position in y.
            offset (tuple[int, int]): offset of the sprite for uniformity.

        Returns:
            tuple: The position of the drone as pixel.
        """
        return (
            gx * GlobalParameters.CELL_SIZE
            + GlobalParameters.CELL_SIZE // 2
            + GlobalParameters.OFFSET[0] * gx
            + offset[0],
            gy * GlobalParameters.CELL_SIZE
            + GlobalParameters.CELL_SIZE // 2
            + GlobalParameters.OFFSET[1] * gy
            + offset[1],
        )

    @staticmethod
    def _tint_sprite(
        sprite: pygame.Surface, color: tuple[int, int, int]
    ) -> pygame.Surface:
        """Apply a light color tint to the drone sprite."""
        image = sprite.copy()
        tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint.fill((*color, 255))
        image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    def _sync_sprite(self) -> None:
        """Keep `image` and `rect` aligned with the current pixel position."""
        self._frame_index += 1
        self._frame_index %= len(self._frames)
        self.image = self._frames[self._frame_index]

    @property
    def position(self) -> tuple[int, int]:
        """Get the position of the drone."""
        return self._grid_pos

    @position.setter
    def position(self, new_pos: tuple[int, int]) -> None:
        """
        Get the position of the drone.

        Args:
            new_pos (tuple[int, int]): The new position of the drone.
        """
        self._grid_pos = new_pos
        self._px, self._py = self._grid_to_px(*new_pos, self._pixel_offset)
        self._anim_active = False

    def _move_to(self, dest: tuple[int, int]) -> None:
        """
        Move the drone to a specific destination.

        Args:
            dest (tuple[int, int]): The destination of the drone.
        """
        # If it is already in it's position, don't do anything
        if dest == self._grid_pos and not self._anim_active:
            return

        self._anim_start = (self._px, self._py)
        self._anim_end = self._grid_to_px(*dest, self._pixel_offset)
        self._anim_elapsed = 0.0
        self._anim_active = True
        self._grid_pos = dest

    def update(self, dt: float) -> None:
        """
        Update the state of the drone.

        Args:
            dt (float): delta time.
        """
        # Animate the drone sprite all the time, movement only when needed.
        self._frame_elapsed += dt
        if self._frame_elapsed >= self._frame_speed:
            self._frame_elapsed %= self._frame_speed
            self._sync_sprite()

        if not self.rect:
            return

        if not self._anim_active:
            self.rect.center = (self._px, self._py)
            return

        self._anim_elapsed += dt
        t = min(self._anim_elapsed / self._anim_speed, 1.0)

        sx, sy = self._anim_start
        ex, ey = self._anim_end
        self._px = sx + (ex - sx) * t
        self._py = sy + (ey - sy) * t
        self.rect.center = (self._px, self._py)

        if self._anim_elapsed >= self._anim_speed:
            self._px, self._py = self._anim_end
            self._anim_active = False
            self.rect.center = self._anim_end

    @property
    def is_moving(self) -> bool:
        """Check if the drone is moving."""
        return self._anim_active


class AllSprite(pygame.sprite.Group[pygame.sprite.Sprite]):
    """Sprite Group for every sprite."""

    def __init__(self) -> None:
        """Everything starts here."""
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw_sprite(self, target_pos: tuple[int | float, int | float]) -> None:
        """
        Draw every sprite in the screen.

        Args:
            target_pos (tuple[int, int]): The position of
            where to draw every sprite.
        """
        self.offset.x = -(target_pos[0] - GlobalParameters.WINDOWWIDTH // 2)
        self.offset.y = -(target_pos[1] - GlobalParameters.WINDOWHEIGHT // 2)

        hub_layout = [
            sprite
            for sprite in self
            if not hasattr(sprite, "_connection")
            and not hasattr(sprite, "drone_id")
        ]
        connection_layout = [
            sprite
            for sprite in self
            if hasattr(sprite, "_connection")
            and not hasattr(sprite, "drone_id")
        ]

        drone_layout = [
            sprite for sprite in self if hasattr(sprite, "drone_id")
        ]

        if self.display_surface is None:
            sys.exit(1)

        for layout in [
            connection_layout,
            hub_layout,
            drone_layout,
        ]:
            for sprite in layout:
                if isinstance(
                    sprite.rect, pygame.Rect | pygame.FRect
                ) and isinstance(sprite.image, pygame.Surface):
                    draw_rect = sprite.rect.move(self.offset.x, self.offset.y)
                    _ = self.display_surface.blit(
                        sprite.image,
                        (int(draw_rect.x), int(draw_rect.y)),
                    )

    @override
    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update sprites while passing delta time only to drones."""
        dt = args[0] if args else kwargs.get("dt")
        for sprite in self.sprites():
            if isinstance(sprite, DroneSprite):
                sprite.update(dt if dt is not None else 0.0)
            else:
                sprite.update()


class Camera:
    """Handle the camera for the screen."""

    def __init__(self) -> None:
        """Everything starts here."""
        # Position
        self._camera_x = 0
        self._camera_y = 0

        # Usefull variable
        self._draging = False
        self._last_mouse_pos = (0, 0)
        self._bound = [0, 0, 0, 0]

    def handle_camera(self) -> None:
        """Handle camera to not go too far."""
        self._camera_y = min(self._bound[1], self._camera_y)
        self._camera_y = max(self._bound[3], self._camera_y)
        self._camera_x = min(self._bound[0], self._camera_x)
        self._camera_x = max(self._bound[2], self._camera_x)

    def check_bound(self, hubs: dict[str, Hub]) -> list[int]:
        """
        Check the limit of the camera to no go too to far.

        Args:
            hubs (dict[str): hubs to see their coordonates.
            Hub (Any): Description of Hub.

        Returns:
            list: Maximum and Minimum value for the camera.
        """
        minimum_x = min(hubs.values(), key=lambda x: x.x).x * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        )
        minimum_y = min(hubs.values(), key=lambda x: x.y).y * (
            GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE
        )
        maximum_x = max(hubs.values(), key=lambda x: x.x).x * (
            GlobalParameters.OFFSET[0] + GlobalParameters.CELL_SIZE
        )
        maximum_y = max(hubs.values(), key=lambda x: x.y).y * (
            GlobalParameters.OFFSET[1] + GlobalParameters.CELL_SIZE
        )

        return [maximum_x, maximum_y, minimum_x, minimum_y]


class Button(pygame.sprite.Sprite):
    """Button class for every class."""

    def __init__(
        self,
        pos: tuple[int, int],
        frames: list[pygame.Surface],
        sound: pygame.Sound,
    ) -> None:
        """
        Everything starts here.

        Args:
            pos (tuple[int, int]): Position of the button.
            frames (list[pygame.Surface]): The sprites
            for the button.
        """
        super().__init__()
        self._frames = frames
        self.image = self._frames[0]
        self.rect = self.image.get_frect(topleft=pos)

        self._frame_index = 0
        self._animation_time = 0.017
        self._current_time = 0.0
        self._is_working = False

        self._sound = sound

    def _animate(self) -> None:
        """Animate the button when called."""
        self._frame_index += 1
        self.image = self._frames[self._frame_index % len(self._frames)]

    def _time_animation(self, dt: float) -> bool:
        """
        Handle the time of the animation.

        Args:
            dt (float): Delta time.
        Returns:
            bool: True if it can animate.
        """
        self._current_time += dt
        if self._current_time >= self._animation_time:
            self._current_time = 0
            return True
        return False

    def reset(self) -> None:
        """Reset the button state like frame and time."""
        self._current_time = 0.0
        self._frame_index = 0
        self._is_working = False
        self.image = self._frames[0]

    def check_hovered(self) -> None:
        """Check if the button is hovered by the mouse."""
        if not self.rect:
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if not self._is_working:
                self._sound.play()
            self._is_working = True
        else:
            if self._is_working:
                self.reset()

    def update_sprite(self, dt: float, signal: int) -> int | None:
        """
        Update the sprite status (should be called every frame).

        Args:
            dt (float): Delta time.
            signal (int): Signal to return if True.
        Returns:
            int: The signal.
        """
        if pygame.mouse.get_pressed()[0]:
            self.check_hovered()

        if self._is_working and self._time_animation(dt):
            if self._frame_index == 3:
                return signal
            self._animate()
        return 0
