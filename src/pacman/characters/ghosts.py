"""Module defining all ghost characters in the game."""

from abc import abstractmethod, ABC
import math
import random
import pygame
from pygame import Color
from pygame import Rect, Surface
from pacman.settings import (
    FLOOR_SIZE,
    TOLERANCE,
    WALL_SIZE,
    CELL_SIZE,
    Directions,
    BLACK
)
from .pacman import Pacman
from .character import Character
from pacman.spritesheet import Spritesheet
from pacman.strategy import ChaseStrategy, EuclideanChaseStrategy


class Ghost(Character, ABC):
    """Base class for all ghosts in the game."""

    INITIAL_DIRECTION: Directions = Directions.NONE
    SPRITES: dict[Directions, list[tuple[int, int, int, int]]] = {}
    SPRITES_SCARED: dict[str, list[tuple[int, int, int, int]]] = {
        "BLUE": [(128, 0, 14, 14), (144, 0, 14, 14)],
        "WHITE": [(160, 0, 14, 14), (176, 0, 14, 14)]
    }

    def __init__(
            self, maze: list[list[int]],
            pacman: Pacman,
            spritesheet: Spritesheet,
            chase_strategy: ChaseStrategy | None = None,
            ) -> None:
        """Initialize the ghost state.

        Args:
            maze: Grid used for movement.
            pacman: Reference to the Pacman instance for targeting.
            spritesheet: Sprite sheet used to build the animation frames.
            chase_strategy: Optional strategy for chasing Pacman.
                            Defaults to Euclidean distance.
        """
        if maze is None or spritesheet is None:
            raise TypeError("The Ghost requires maze and spritesheet")
        self.spritesheet = spritesheet
        self.chase_strategy = chase_strategy or EuclideanChaseStrategy()
        self.animation: dict[Directions, list[Surface]] = {}
        self.animation_scared: dict[str, list[Surface]] = {}
        self.pacman: Pacman = pacman
        self.base_speed = 0.70 * self.pacman.speed
        self.speed = self.base_speed
        self.decision_made = False
        self.respawn_pos = (0, 0)
        self._is_frightened = False
        self.timer_frightened = 0
        self.frightened_duration = 10000
        self.timer_respawn = 0
        self.cycle = 27
        super().__init__(maze, spritesheet)

    @property
    def is_frightened(self) -> bool:
        """Get the frightened state of the ghost."""
        return self._is_frightened

    @is_frightened.setter
    def is_frightened(self, value: bool) -> None:
        """Set the frightened state of the ghost.

        When set to True, the ghost becomes frightened and slows down.
        When set to False, the ghost returns to normal speed.
        """
        self._is_frightened = value
        if value:
            self.timer_frightened = pygame.time.get_ticks()
            self.speed = 0.50 * self.pacman.speed
        else:
            self.speed = self.base_speed

    def _load_image(self) -> tuple[Surface, Rect]:
        """Build the animation frames and return the first frame.

        Returns:
            A tuple containing the initial image and its rect.
        """
        if self.SPRITES_SCARED:
            for state, coords in self.SPRITES_SCARED.items():
                self.animation_scared[state] = [
                    pygame.transform.scale(
                        self.spritesheet.get_sprite(*rect),
                        self.SIZE,
                    )
                    for rect in coords
                ]
                for sprite in self.animation_scared[state]:
                    sprite.set_colorkey(Color(BLACK))

        return super()._load_image()

    def distance_target(
            self,
            pos: tuple[int, int],
            target_pos: tuple[int, int]
            ) -> float:
        """Get the distance from the current position to a target position.

        Args:
            pos: Current position as (x, y) in grid coordinates.
            target_pos: Target position as (x, y) in grid coordinates.

        Returns:
            The Euclidean distance between the current position and the target.
        """
        pos_x, pos_y = pos
        target_x, target_y = target_pos

        return math.sqrt((target_x - pos_x) ** 2 + (target_y - pos_y) ** 2)

    @abstractmethod
    def _target_cell(self) -> tuple[int, int]:
        """Calculate the target cell according to the ghost type."""
        ...

    def _at_center(self, center: tuple[int, int]) -> bool:
        """Check if the ghost is approximately at the center of a cell.

        Args:
            center: The pixel coordinates of the cell center.

        Returns:
            True if the ghost is at the center, False otherwise.
        """
        center_x, center_y = center
        return (abs(center_x - self.rect.centerx) < TOLERANCE
                and abs(center_y - self.rect.centery) < TOLERANCE)

    def _move(self, scatter: bool = False) -> Directions:
        cx, cy = self._current_cell()
        center_x, center_y = self._to_pixels(cx, cy)
        next_direction = self.direction

        if not self._at_center((center_x, center_y)):
            self.decision_made = False
            return next_direction

        if self.decision_made:
            return next_direction

        self.decision_made = True

        available = [
            d for d in Directions
            if d != Directions.NONE and self._can_move(d, cx, cy)
        ]

        if not available:
            return self._opposite_direction(self.direction)

        non_reverse = [
            d for d in available
            if d != self._opposite_direction(self.direction)
            ]

        if not non_reverse:
            return self._opposite_direction(self.direction)

        if len(non_reverse) == 1:
            if self._can_move(self.direction, cx, cy):
                return self.direction

        if scatter:
            return random.choice(non_reverse)

        chosen = self.chase_strategy.get_direction(
            self, (cx, cy), self._target_cell()
            )
        if chosen != Directions.NONE and chosen in non_reverse:
            return chosen
        if self.direction in non_reverse:
            return self.direction
        else:
            return non_reverse[0]

    def _animate(self) -> None:
        """Update the ghost image based on its current state and direction."""
        if self.direction != Directions.NONE:
            current_center = self.rect.center

            if self.is_frightened:
                if (
                    pygame.time.get_ticks() - self.timer_frightened
                    < self.frightened_duration - self.frightened_duration * 0.7
                ):
                    frame = self.animation_scared["BLUE"]
                else:
                    if pygame.time.get_ticks() // 300 % 2 == 1:
                        frame = self.animation_scared["BLUE"]
                    else:
                        frame = self.animation_scared["WHITE"]
            else:
                frame = self.animation[self.direction]

            self.frame_slower += 0.2
            if self.frame_slower >= len(frame):
                self.frame_slower = 0
            self.image = frame[int(self.frame_slower)]
            self.rect = self.image.get_rect(center=current_center)

    def update(self) -> None:
        """Update the ghost's position and animation."""
        if self.pacman.is_alive and self.is_alive:
            if self.is_frightened:
                self.direction = self._move(scatter=True)
                if (
                    pygame.time.get_ticks() - self.timer_frightened
                    >= self.frightened_duration
                ):
                    self.is_frightened = False

            elif pygame.time.get_ticks() // 1000 % self.cycle < 20:
                self.direction = self._move()
            else:
                self.direction = self._move(scatter=True)

            self.rect.x += self.direction.dx * self.speed  # type: ignore
            self.rect.y += self.direction.dy * self.speed  # type: ignore

        self._animate()
        self.teleport()

    def respawn(self) -> None:
        """Reset the ghost to its spawn state."""
        self.rect.center = self.respawn_pos
        self.direction = self.INITIAL_DIRECTION
        self.frame_slower = 0
        self.speed = self.base_speed
        self.is_alive = True
        self.is_visible = True
        self.is_frightened = False
        if self.direction in self.animation:
            self.image = self.animation[self.direction][0]


class Blinky(Ghost):
    """Subclass of Ghost for the Blinky ghost (The Red Ghost)."""

    INITIAL_DIRECTION = Directions.DOWN
    SPRITES = {
        Directions.RIGHT: [(0, 0, 14, 14), (16, 0, 14, 14)],
        Directions.LEFT: [(32, 0, 14, 14), (48, 0, 14, 14)],
        Directions.UP: [(64, 0, 14, 14), (80, 0, 14, 14)],
        Directions.DOWN: [(96, 0, 14, 14), (112, 0, 14, 14)],
    }

    def __init__(
            self,
            maze: list[list[int]],
            pacman: Pacman,
            spritesheet: Spritesheet,
            chase_strategy: ChaseStrategy
            ):
        """Initialize Blinky with its specific sprites and respawn position."""
        super().__init__(maze, pacman, spritesheet, chase_strategy)
        self.respawn_pos = (
            WALL_SIZE + FLOOR_SIZE // 2,
            WALL_SIZE + FLOOR_SIZE // 2
            )

    def _target_cell(self) -> tuple[int, int]:
        """
        Calculate Blinky's target cell.

        Returns:
            The grid coordinates of Pacman's current cell.
        """
        return self.pacman._current_cell()

    def respawn(self) -> None:
        """Reset Blinky to its spawn state."""
        self.rect.center = self.respawn_pos
        super().respawn()


class Pinky(Ghost):
    """Subclass of Ghost for the Pinky ghost (The Pink Ghost)."""

    INITIAL_DIRECTION = Directions.DOWN
    SPRITES = {
        Directions.RIGHT: [(0, 16, 14, 14), (16, 16, 14, 14)],
        Directions.LEFT: [(32, 16, 14, 14), (48, 16, 14, 14)],
        Directions.UP: [(64, 16, 14, 14), (80, 16, 14, 14)],
        Directions.DOWN: [(96, 16, 14, 14), (112, 16, 14, 14)],
    }

    def __init__(
            self,
            maze: list[list[int]],
            pacman: Pacman,
            spritesheet: Spritesheet,
            chase_strategy: ChaseStrategy
            ):
        """Initialize Pinky with its specific sprites and respawn position."""
        super().__init__(maze, pacman, spritesheet, chase_strategy)
        self.respawn_pos = (
            CELL_SIZE * (len(self.maze[0]) - 1) + WALL_SIZE + FLOOR_SIZE // 2,
            WALL_SIZE + FLOOR_SIZE // 2,
        )

    def _target_cell(self) -> tuple[int, int]:
        """
        Calculate Pinky's target cell.

        Returns:
            The grid coordinates of the cell 4 spaces ahead of Pacman
            in his current direction.
        """
        px, py = self.pacman._current_cell()
        return (
            max(
                0,
                min(px + self.pacman.direction.dx * 4, len(self.maze[0]) - 1)
                ),
            max(
                0,
                min(py + self.pacman.direction.dy * 4, len(self.maze) - 1)
                ),
        )

    def respawn(self) -> None:
        """Reset Pinky to its spawn state."""
        self.rect.center = self.respawn_pos
        super().respawn()


class Inky(Ghost):
    """Subclass of Ghost for the Inky ghost (The Cyan Ghost)."""

    INITIAL_DIRECTION = Directions.UP
    SPRITES = {
        Directions.RIGHT: [(0, 32, 14, 14), (16, 32, 14, 14)],
        Directions.LEFT: [(32, 32, 14, 14), (48, 32, 14, 14)],
        Directions.UP: [(64, 32, 14, 14), (80, 32, 14, 14)],
        Directions.DOWN: [(96, 32, 14, 14), (112, 32, 14, 14)],
    }

    def __init__(
            self,
            maze: list[list[int]],
            pacman: Pacman,
            blinky: Blinky,
            spritesheet: Spritesheet,
            chase_strategy: ChaseStrategy
            ):
        """Initialize Inky with its specific sprites and respawn position."""
        super().__init__(maze, pacman, spritesheet, chase_strategy)
        self.blinky = blinky
        self.respawn_pos = (
            WALL_SIZE + FLOOR_SIZE // 2,
            CELL_SIZE * (len(self.maze) - 1) + WALL_SIZE + FLOOR_SIZE // 2
            )

    def _target_cell(self) -> tuple[int, int]:
        """
        Calculate Inky's target cell.

        Returns:
            The grid coordinates of the cell that is the reflection of Blinky's
            position across the point 2 spaces ahead of Pacman.
        """
        px, py = self.pacman._current_cell()
        bx, by = self.blinky._current_cell()
        pivot_x = px + self.pacman.direction.dx * 2
        pivot_y = py + self.pacman.direction.dy * 2

        target_x = pivot_x + (pivot_x - bx)
        target_y = pivot_y + (pivot_y - by)

        target_x = max(0, min(target_x, len(self.maze[0]) - 1))
        target_y = max(0, min(target_y, len(self.maze) - 1))

        return (
            target_x,
            target_y
        )

    def respawn(self) -> None:
        """Reset Inky to its spawn state."""
        self.rect.center = self.respawn_pos
        super().respawn()


class Clyde(Ghost):
    """Subclass of Ghost for the Clyde ghost (The Orange Ghost)."""

    INITIAL_DIRECTION = Directions.UP
    SPRITES = {
        Directions.RIGHT: [(0, 48, 14, 14), (16, 48, 14, 14)],
        Directions.LEFT: [(32, 48, 14, 14), (48, 48, 14, 14)],
        Directions.UP: [(64, 48, 14, 14), (80, 48, 14, 14)],
        Directions.DOWN: [(96, 48, 14, 14), (112, 48, 14, 14)],
    }

    def __init__(
            self,
            maze: list[list[int]],
            pacman: Pacman,
            spritesheet: Spritesheet,
            chase_strategy: ChaseStrategy
            ):
        """Initialize Clyde with its specific sprites and respawn position."""
        super().__init__(maze, pacman, spritesheet, chase_strategy)
        self.respawn_pos = (
            CELL_SIZE * (len(self.maze[0]) - 1) + WALL_SIZE + FLOOR_SIZE // 2,
            CELL_SIZE * (len(self.maze) - 1) + WALL_SIZE + FLOOR_SIZE // 2,
        )

    def _target_cell(self) -> tuple[int, int]:
        """
        Calculate Clyde's target cell.

        Returns:
            The grid coordinates of pacman's current cell
            if he is far enough away (>8 as euclidean distance),
            otherwise its respawn position.
        """
        cx, cy = self._current_cell()
        px, py = self.pacman._current_cell()
        distance = self.distance_target((cx, cy), (px, py))

        if distance > 8:
            return (px, py)
        else:
            return self.respawn_pos

    def respawn(self) -> None:
        """Reset Clyde to its spawn state."""
        self.rect.center = self.respawn_pos
        super().respawn()
