"""Module defining the Pacman character for the game."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from pathlib import Path
from .character import Character
from pacman.settings import (Directions, SPEED)

if TYPE_CHECKING:
    from pygame import Surface, Rect
    from pygame.key import ScancodeWrapper
    from pacman.spritesheet import Spritesheet


class Pacman(Character):
    """Class representing the Pacman character controlled by the player."""

    INITIAL_DIRECTION = Directions.RIGHT
    SPRITES = {
        Directions.RIGHT: [
            (0, 54, 48, 48),
            (54, 54, 48, 48),
            (108, 54, 48, 48),
        ],
        Directions.LEFT: [
            (162, 54, 48, 48),
            (216, 54, 48, 48),
            (270, 54, 48, 48),
        ],
        Directions.UP: [(0, 0, 48, 48), (54, 0, 48, 48), (108, 0, 48, 48)],
        Directions.DOWN: [
            (162, 0, 48, 48),
            (216, 0, 48, 48),
            (270, 0, 48, 48),
        ],
    }
    SPRITES_DEATH = [
        (0, 128, 52, 48),
        (52, 128, 58, 48),
        (110, 128, 62, 48),
        (172, 128, 58, 48),
        (230, 128, 58, 48),
        (288, 128, 60, 48),
        (348, 128, 54, 48),
        (402, 128, 38, 48),
        (440, 128, 26, 48),
        (462, 128, 18, 48),
        (480, 128, 48, 48),
        ]

    def __init__(
            self,
            maze: list[list[int]] | None = None,
            spritesheet: Spritesheet | None = None,
            ) -> None:
        """
        Initialize the Pacman character.

        Args:
            maze: The grid representing the maze layout.
            spritesheet: The sprite sheet containing Pacman's animation frames.
        """
        if maze is None or spritesheet is None:
            raise TypeError("Pacman requires maze and spritesheet")
        self.animation: dict[Directions, list[Surface]] = {}
        self.animation_death: list[Surface] = []

        self.spritesheet = spritesheet
        super().__init__(maze, spritesheet)

        self._next_direction: Directions = Directions.NONE
        self._frame_slower: float = 0
        self.speed: int = SPEED
        self._cheated: bool = False
        self.is_alive: bool = True
        self.start_dying: bool = False
        self.death_finished: bool = False

    def _load_image(self) -> tuple[Surface, Rect]:
        """
        Build the animation frames from the sprite sheet.

        Returns:
            A tuple containing the initial image and its rect.
        """
        if self.SPRITES_DEATH:
            self.animation_death = [
                self.spritesheet.get_sprite(*rect)
                for rect in self.SPRITES_DEATH
            ]
            self.animation_death = [
                pygame.transform.scale(sprite, self.SIZE)
                for sprite in self.animation_death
            ]
        return super()._load_image()

    @property
    def direction(self) -> Directions:
        """Get the current movement direction of Pacman."""
        return self._direction

    @direction.setter
    def direction(self, value: Directions) -> None:
        """Set the movement direction of Pacman."""
        self._direction = value

    @property
    def next_direction(self) -> Directions:
        """Get the next intended movement direction of Pacman."""
        return self._next_direction

    @next_direction.setter
    def next_direction(self, keys: ScancodeWrapper) -> None:
        """Set the next movement direction based on keyboard input."""
        if keys[pygame.K_LEFT]:
            self._next_direction = Directions.LEFT
        elif keys[pygame.K_RIGHT]:
            self._next_direction = Directions.RIGHT
        elif keys[pygame.K_UP]:
            self._next_direction = Directions.UP
        elif keys[pygame.K_DOWN]:
            self._next_direction = Directions.DOWN

    def _animate(self) -> None:
        """Handle the animation of Pacman based on its state and direction."""
        if not self.is_alive and self.start_dying:
            self._animate_frames(self.animation_death, loop=False)
            if self.frame_slower >= len(self.animation_death) - 1:
                self.death_finished = True
            return

        if self._direction != Directions.NONE:
            self._animate_frames(self.animation[self._direction], loop=True)

    def _animate_frames(self, frames: list[Surface], loop: bool) -> None:
        current_center = self.rect.center
        self.frame_slower += 0.2

        if self.frame_slower >= len(frames):
            self.frame_slower = len(frames) - 1 if not loop else 0

        self.image = frames[int(self.frame_slower)]
        self.rect = self.image.get_rect(center=current_center)

    def update(self) -> None:
        """Update Pacman's position, handle movement and animation."""
        if not self.is_blocked:
            cx, cy = self._current_cell()
            center_x, center_y = self._to_pixels(cx, cy)
            at_center = (
                abs(center_x - self.rect.centerx) < self.speed
                and abs(center_y - self.rect.centery) < self.speed
            )

            can_turn = at_center
            can_reverse = (
                self._next_direction
                == self._opposite_direction(self._direction)
            )

            if can_turn or can_reverse:
                if at_center:
                    self.rect.center = (center_x, center_y)
                if (
                    self._next_direction != Directions.NONE
                    and self._can_move(self._next_direction, cx, cy)
                ):
                    self._direction = self._next_direction
                elif not self._can_move(self._direction, cx, cy):
                    self._direction = Directions.NONE

            self.rect.x += self._direction.dx * self.speed
            self.rect.y += self._direction.dy * self.speed
            self.teleport()

        self._animate()

    def respawn(self) -> None:
        """Reset Pacman to the initial position and state."""
        self._direction = self.INITIAL_DIRECTION
        self.image = self.animation[self._direction][0]
        self.frame_slower = 0
        self.is_alive = True
        self.death_finished = False
        self.start_dying = False

        cmy = len(self.maze) // 2
        cmx = len(self.maze[0]) // 2

        pos_x, pos_y = self._to_pixels(cmx, cmy)

        if self.maze[cmy][cmx] != 15:
            self.rect.center = (pos_x, pos_y)
        else:
            directions = [Directions.LEFT, Directions.RIGHT]
            for direc in directions:
                if self.maze[cmy + direc.dy][cmx + direc.dx] != 15:
                    pos_x, pos_y = self._to_pixels(
                        cmx + direc.dx, cmy + direc.dy
                        )
                    self.rect.center = (pos_x + direc.dx, pos_y + direc.dy)

    def shoot(
            self,
            missiles_group: pygame.sprite.Group[Any],
            spritesheet: Spritesheet
            ) -> None:
        """Shoot a missile in the current direction if in cheated mode."""
        from .missile import Missile
        if not self._cheated:
            return
        for direction in (
            Directions.UP,
            Directions.DOWN,
            Directions.LEFT,
            Directions.RIGHT,
        ):
            missiles_group.add(
                Missile(self.rect.center, direction, self.maze, spritesheet)
                )

    def _load_anim(self, folder: str) -> list[pygame.Surface]:
        """Load animation frames from the specified folder."""
        base = Path(__file__).parent.parent
        assets = Path(base / "assets" / folder)

        self.walk_anim = []
        for file in assets.iterdir():
            img = pygame.image.load(Path(assets / file)).convert_alpha()
            img = pygame.transform.scale(img, self.SIZE)
            self.walk_anim.append(img)

        return self.walk_anim

    def set_normal(self) -> None:
        """Set Pacman to normal mode, disabling cheat mode."""
        self._cheated = False
        self.SIZE = Character.SIZE
        self.speed = SPEED
        current_center = self.rect.center
        self.image, self.rect = self._load_image()
        self.rect.center = current_center

    def set_cheated(self) -> None:
        """Set Pacman to cheated mode, enabling shooting."""
        self._cheated = True
        self.SIZE = (100, 100)
        self.speed = 7
        self.animation = {
            Directions.UP: self._load_anim("pacman_car/pacman-up"),
            Directions.LEFT: self._load_anim("pacman_car/pacman-left"),
            Directions.RIGHT: self._load_anim("pacman_car/pacman-right"),
            Directions.DOWN: self._load_anim("pacman_car/pacman-down"),
        }
        self.image = self.animation[Directions.RIGHT][0]
        self.rect = self.image.get_rect(center=self.rect.center)

    def set_death(self) -> None:
        """Set Pacman to the death state, starting the death animation."""
        self.is_alive = False
        self.is_blocked = True
        self._direction = Directions.NONE
        self._next_direction = Directions.NONE
        self.frame_slower = 0
