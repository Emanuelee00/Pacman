"""Module defining the base Character class."""

from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from pygame import Color
from pygame import Surface, Rect
from pacman.settings import (
    Directions,
    WALL_SIZE,
    FLOOR_SIZE,
    CELL_SIZE,
    BLACK
)
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from pacman.spritesheet import Spritesheet


class Character(pygame.sprite.Sprite, ABC):
    """Base class for all moving characters in the game."""

    SIZE = (40, 40)
    SPRITES: dict[Directions, list[tuple[int, int, int, int]]] = {}
    INITIAL_DIRECTION = Directions.NONE

    def __init__(
            self,
            maze: list[list[int]],
            spritesheet: Spritesheet,
            ) -> None:
        """Initialize the character state.

        Args:
            maze: Grid used for movement.
            spritesheet: Sprite sheet used to build the animation frames.
        """
        super().__init__()
        self.maze: list[list[int]] = maze
        self.spritesheet: Spritesheet = spritesheet
        self.direction: Directions = Directions.NONE
        self.animation: dict[Directions, list[Surface]] = {}
        self.image, self.rect = self._load_image()
        self.frame_slower: float = 0
        self.is_visible: bool = True
        self.is_alive: bool = True
        self.is_blocked: bool = False

    def _load_image(self) -> tuple[Surface, Rect]:
        """
        Build the animation frames and return the first frame.

        Returns:
            A tuple containing the initial image and its rect.
        """
        for direction, coords in self.SPRITES.items():
            self.animation[direction] = [
                pygame.transform.scale(
                    self.spritesheet.get_sprite(*rect),
                    self.SIZE,
                )
                for rect in coords
            ]
            for sprite in self.animation[direction]:
                sprite.set_colorkey(Color(BLACK))

        image = self.animation[self.INITIAL_DIRECTION][0]

        return image, image.get_rect()

    def respawn(self) -> None:
        """Reset the character to its spawn state."""
        ...

    def _current_cell(self) -> tuple[int, int]:
        """Return the maze cell that currently contains the character."""
        cx = max(
            0,
            min(
                len(self.maze[0]) - 1,
                (self.rect.centerx - WALL_SIZE) // CELL_SIZE,
            ),
        )

        cy = max(
            0,
            min(
                (self.rect.centery - WALL_SIZE) // CELL_SIZE,
                len(self.maze) - 1,
            ),
        )
        return cx, cy

    def _to_pixels(self, cx: int, cy: int) -> tuple[int, int]:
        """Convert maze coordinates to the pixel center of a cell.

        Args:
            cx: Cell column index.
            cy: Cell row index.

        Returns:
            The pixel coordinates for the center of the cell.
        """
        center_x = cx * CELL_SIZE + WALL_SIZE + FLOOR_SIZE // 2
        center_y = cy * CELL_SIZE + WALL_SIZE + FLOOR_SIZE // 2
        return center_x, center_y

    def _can_move(
        self,
        direction: Directions,
        cx: int,
        cy: int,
    ) -> bool:
        """Check whether the character can move from a given cell.

        Args:
            direction: Direction to test.
            cx: Current cell column.
            cy: Current cell row.

        Returns:
            True if movement is allowed, False otherwise.
        """
        if direction == Directions.NONE:
            return False
        nx, ny = cx + direction.dx, cy + direction.dy
        tunnel_row = len(self.maze) // 2
        if direction == Directions.LEFT and cx == 0 and cy == tunnel_row:
            return True
        if (
            direction == Directions.RIGHT
            and cx == len(self.maze[0]) - 1
            and cy == tunnel_row
        ):
            return True
        if not (0 <= ny < len(self.maze) and 0 <= nx < len(self.maze[ny])):
            return False
        return not (self.maze[cy][cx] & direction.bit)

    def teleport(self) -> None:
        """Wrap the character around the horizontal tunnel."""
        if self.rect.centerx < 0:
            self.rect.centerx = len(self.maze[0]) * CELL_SIZE + WALL_SIZE
        elif self.rect.centerx >= len(self.maze[0]) * CELL_SIZE + WALL_SIZE:
            self.rect.centerx = 0

    def _opposite_direction(self, direction: Directions) -> Directions:
        """Return the opposite of a direction.

        Args:
            direction: Direction to invert.

        Returns:
            The opposite direction or NONE if there is no opposite.
        """
        if direction == Directions.UP:
            return Directions.DOWN
        elif direction == Directions.DOWN:
            return Directions.UP
        elif direction == Directions.LEFT:
            return Directions.RIGHT
        elif direction == Directions.RIGHT:
            return Directions.LEFT
        else:
            return Directions.NONE

    @abstractmethod
    def update(self) -> None:
        """Advance the character state by one frame."""
        ...
