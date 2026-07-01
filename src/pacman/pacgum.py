"""Module for managing pacgums in game."""

from typing import TYPE_CHECKING, Any
import pygame
from pygame import Color
from pacman.settings import (
    CELL_SIZE,
    WALL_SIZE,
    FLOOR_SIZE,
    RADIUS,
    YELLOW
)

if TYPE_CHECKING:
    from pygame import Surface, Rect


class Pacgum(pygame.sprite.Sprite):
    """Class representing a pacgum in the game."""

    def __init__(
            self,
            pos_x: int,
            pos_y: int,
            radius: int = RADIUS,
            is_super: bool = False
            ) -> None:
        """
        Initialize the pacgum.

        Args:
            pos_x: The x-coordinate of the pacgum's center.
            pos_y: The y-coordinate of the pacgum's center.
            radius: The radius of the pacgum (default is RADIUS).
            is_super: Whether this pacgum is a super pacgum (default is False).
        """
        super().__init__()
        self.radius: int = radius
        self.is_super: bool = is_super
        self.image: Surface = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA
            )
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self.image, Color(YELLOW), (self.radius, self.radius), self.radius
            )
        self.rect: Rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)


class PacgumManager:
    """Class responsible for managing all pacgums in the maze."""

    def __init__(self, maze: list[list[int]]) -> None:
        """
        Initialize the pacgum manager with the maze layout.

        Args:
            maze: The grid representing the maze layout.
        """
        self.group: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self._fill_maze(maze)

    def _fill_maze(self, maze: list[list[int]]) -> None:
        """Fill the maze with pacgums based on the layout."""
        def is_corner(maze: list[list[int]], cx: int, cy: int) -> bool:
            """
            Check if the given cell is a corner in the maze.

            Args:
                maze: The grid representing the maze layout.
                cx: The x-coordinate of the cell.
                cy: The y-coordinate of the cell.

            Returns:
                True if the cell is a corner, False otherwise.
            """
            return (
                (cx == 0 and cy == 0)
                or (cx == 0 and cy == len(maze) - 1)
                or (cx == len(maze[0]) - 1 and cy == 0)
                or (cx == len(maze[0]) - 1 and cy == len(maze) - 1)
            )

        for cy in range(len(maze)):
            for cx in range(len(maze[cy])):
                if maze[cy][cx] != 15:
                    pos_x = cx * CELL_SIZE + WALL_SIZE + FLOOR_SIZE // 2
                    pos_y = cy * CELL_SIZE + WALL_SIZE + FLOOR_SIZE // 2
                    if not is_corner(maze, cx, cy):
                        self.group.add(Pacgum(pos_x, pos_y))
                    else:
                        self.group.add(Pacgum(
                            pos_x, pos_y, radius=RADIUS + 4, is_super=True)
                            )
