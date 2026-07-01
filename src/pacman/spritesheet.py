"""Module for handling spritesheets in the Pacman game."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from pygame import Surface
    from pathlib import Path


class Spritesheet:
    """Class for loading and extracting sprites from a spritesheet image."""

    def __init__(self, path: Path) -> None:
        """Initialize the spritesheet loading the image from the given path."""
        self.spritesheet = pygame.image.load(path).convert_alpha()

    def get_sprite(self, x: int, y: int, w: int, h: int) -> Surface:
        """Extract a sprite from the spritesheet."""
        sprite = self.spritesheet.subsurface(pygame.Rect(x, y, w, h))
        sprite.set_colorkey((0, 0, 0))
        return sprite
