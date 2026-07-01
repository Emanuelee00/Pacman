"""This file contains all the settings for Pacman."""
from enum import IntEnum, Enum
from typing import TypedDict
import pygame

# Fonts
FONT_OUT = "8-bit Arcade Out.ttf"
FONT_IN = "8-bit Arcade In.ttf"
FONT = "Pixel_Digivolve.otf"


class FontSize:
    """Class representing different font sizes used in the game."""

    X_SMALL = 25
    SMALL = 30
    MEDIUM = 40
    LARGE = 60
    X_LARGE = 80
    XX_LARGE = 180


# Colors
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
BLUE = pygame.Color(0, 0, 255)
CYAN = pygame.Color(43, 255, 255)
YELLOW = pygame.Color(255, 215, 0)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
GOLD = pygame.Color(255, 215, 0)


# Game settings
SPEED = 4
TOLERANCE = 4
DURATION = 120 * 1000


class Directions(Enum):
    """Enum for the possible movement directions of characters."""

    NONE = (0,  0,  0)
    UP = (0, -1,  1)
    RIGHT = (1,  0,  2)
    DOWN = (0,  1,  4)
    LEFT = (-1, 0,  8)

    @property
    def dx(self) -> int:
        """Return the x-coordinate of the direction."""
        return self.value[0]

    @property
    def dy(self) -> int:
        """Return the y-coordinate of the direction."""
        return self.value[1]

    @property
    def bit(self) -> int:
        """Return the bit value of the direction."""
        return self.value[2]


class MenuOption(TypedDict):
    """Typed representation of a menu option."""

    name: str
    position: tuple[int, int]


# Maze settings
class Tile(IntEnum):
    """Enum for the different types of tiles in the maze."""

    FLOOR = 0
    WALL = 1
    CORNER = 2


WALL_SIZE = 24
FLOOR_SIZE = 48
CELL_SIZE = WALL_SIZE + FLOOR_SIZE

# Screen settings
OFFSET_X = 100
OFFSET_Y = 100
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
SCREEN_MARGIN = 0.05
FPS = 60

# Pacgum settings
RADIUS = 3

# Cheating constants
CHEAT_LIVES = [
    pygame.K_t,
    pygame.K_o,
    pygame.K_r,
    pygame.K_e,
    pygame.K_t,
    pygame.K_t,
    pygame.K_o
    ]
CHEAT_42 = [pygame.K_4, pygame.K_2]
UNCHEAT = [pygame.K_f, pygame.K_a, pygame.K_l, pygame.K_s, pygame.K_e]
LEVEL_CHEAT = [
    pygame.K_KP1,
    pygame.K_KP2,
    pygame.K_KP3,
    pygame.K_KP4,
    pygame.K_KP5,
    pygame.K_KP6,
    pygame.K_KP7,
    pygame.K_KP8,
    pygame.K_KP9,
    pygame.K_KP0
]
