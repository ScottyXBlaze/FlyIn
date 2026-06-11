# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    camera.py                                         :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:38 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 15:27:31 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Camera module for the rendering system."""

from src.rendering.settings import CELL_SIZE, OFFSET
from .. import Hub


class Camera:
    """Handle the camera for the screen."""

    def __init__(self) -> None:
        """Everything starts here."""
        # Position
        self.camera_x = 0
        self.camera_y = 0

        # Usefull variable
        self.draging = False
        self.last_mouse_pos = (0, 0)
        self.bound = [0, 0, 0, 0]

    def handle_camera(self) -> None:
        """Handle camera to not go too far."""
        self.camera_y = min(self.bound[1], self.camera_y)
        self.camera_y = max(self.bound[3], self.camera_y)
        self.camera_x = min(self.bound[0], self.camera_x)
        self.camera_x = max(self.bound[2], self.camera_x)

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
            OFFSET[0] + CELL_SIZE
        )
        minimum_y = min(hubs.values(), key=lambda x: x.y).y * (
            OFFSET[1] + CELL_SIZE
        )
        maximum_x = max(hubs.values(), key=lambda x: x.x).x * (
            OFFSET[0] + CELL_SIZE
        )
        maximum_y = max(hubs.values(), key=lambda x: x.y).y * (
            OFFSET[1] + CELL_SIZE
        )

        return [maximum_x, maximum_y, minimum_x, minimum_y]
