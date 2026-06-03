import pygame


class SpriteConverter:
    def __init__(self) -> None:
        pass

    def convert_sprite(
        self,
        image: pygame.Surface,
        frames: tuple[int, int],
    ) -> list[pygame.Surface]:

        image_size = image.get_size()

        frame_size = image_size[0] / frames[0], image_size[1] / frames[1]

        frame_list = []

        for x in range(frames[0]):
            for y in range(frames[1]):
                frame_rect = pygame.Rect(
                    x * frame_size[0],
                    y * frame_size[1],
                    frame_size[0],
                    frame_size[1],
                )
                tile = image.subsurface(frame_rect)
                frame_list.append(tile)

        return frame_list
