"""Module for the Missile character."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import random
from .character import Character
from pacman.spritesheet import Spritesheet
from pacman.settings import Directions, SPEED, TOLERANCE

if TYPE_CHECKING:
    from pygame import Surface, Rect


_FRAME_W = 1536 // 7
_FRAME_H = 1024
_TARGET_H = 100
_SIZE = (max(16, _TARGET_H * _FRAME_W // _FRAME_H), _TARGET_H)
_ROTATIONS = {
    Directions.UP: 0,
    Directions.LEFT: 90,
    Directions.DOWN: 180,
    Directions.RIGHT: 270,
}


class Missile(Character):
    """Class representing a missile fired by Pacman."""

    SPRITES = {}
    INITIAL_DIRECTION = Directions.UP

    def __init__(
            self,
            center: tuple[int, int],
            direction: Directions,
            maze: list[list[int]],
            spritesheet: Spritesheet,
            ) -> None:
        """Initialize the missile.

        Args:
            center: The initial center position of the missile in pixels.
            direction: The initial direction of the missile.
            maze: The grid for movement and collision checks.
        """
        self._fire_direction = direction
        self.spritesheet = spritesheet
        super().__init__(maze, spritesheet)
        self._direction = direction
        self._spawn_time = pygame.time.get_ticks()
        self.rect.center = center

    def _load_image(self) -> tuple[Surface, Rect]:
        """Build the missile animation frames from the sprite sheet."""
        for direction, angle in _ROTATIONS.items():
            frames = []
            for i in range(7):
                frame = self.spritesheet.get_sprite(
                    i * _FRAME_W, 0, _FRAME_W, _FRAME_H
                    )
                frame = pygame.transform.scale(frame, _SIZE)
                frame = pygame.transform.rotate(frame, angle)
                frame.set_colorkey((255, 255, 255))
                frames.append(frame)
            self.animation[direction] = frames
        image = self.animation[self.INITIAL_DIRECTION][0]
        return image, image.get_rect()

    def update(self) -> None:
        """Update the missile's position and animation frame."""
        if pygame.time.get_ticks() - self._spawn_time > 7000:
            self.kill()
            return

        cx, cy = self._current_cell()
        center_x, center_y = self._to_pixels(cx, cy)
        at_center = (abs(center_x - self.rect.centerx) < TOLERANCE
                     and abs(center_y - self.rect.centery) < TOLERANCE)

        if at_center:
            self.rect.center = (center_x, center_y)
            opposite = self._opposite_direction(self._direction)
            available = [
                d for d in Directions
                if d != Directions.NONE
                and d != opposite
                and self._can_move(d, cx, cy)
            ]

            prev_direction = self._direction
            if not available:
                self.kill()
                return
            else:
                self._direction = random.choice(available)

            if self._direction != prev_direction:
                self.frame_slower = 0

        self.rect.x += self._direction.dx * SPEED
        self.rect.y += self._direction.dy * SPEED

        current_center = self.rect.center
        frames = self.animation[self._direction]
        self.frame_slower = (self.frame_slower + 0.12) % len(frames)
        self.image = frames[int(self.frame_slower)]
        self.rect = self.image.get_rect(center=current_center)
