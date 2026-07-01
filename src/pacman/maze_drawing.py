"""Module for drawing the maze in the Pacman game."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from pacman.settings import CYAN, Tile, FLOOR_SIZE, WALL_SIZE

if TYPE_CHECKING:
    from pygame import Surface
    from pacman.spritesheet import Spritesheet

Tiles = {
    1: (0, 0, 24, 24),
    2: (24, 0, 24, 24),
    3: (48, 0, 24, 24),
    4: (72, 0, 24, 24),
    5: (96, 0, 24, 24),
    6: (120, 0, 24, 24),
    7: (144, 0, 24, 24),
    8: (168, 0, 24, 24),
    9: (192, 0, 24, 24),
    10: (216, 0, 24, 24),
    11: (240, 0, 24, 24),
    12: (0, 24, 24, 24),
    13: (24, 24, 24, 24),
    14: (48, 24, 24, 24),
    15: (72, 24, 24, 24),
    16: (96, 24, 24, 48),
    17: (120, 24, 48, 24),
}


def to_tile_map(maze: list[list[int]]) -> list[list[Tile]]:
    """
    Convert the maze grid into a tile map for rendering.

    Args:
        maze: The grid representing the maze layout.
    Returns:
        A 2D list representing the tile map of the maze.
    """
    tile_map = []

    for ty in range(2 * len(maze) + 1):
        row = []
        for tx in range(2 * len(maze[0]) + 1):
            x = tx // 2
            y = ty // 2

            if tx % 2 == 1 and ty % 2 == 1:
                row.append(Tile.FLOOR)

            elif tx % 2 == 1 and ty % 2 == 0:
                if ty == 0 or ty == 2 * len(maze):
                    row.append(Tile.WALL)
                elif (
                    0 < y <= len(maze) and x < len(maze[y - 1])
                    and (maze[y - 1][x] & 4)
                ):
                    row.append(Tile.WALL)
                else:
                    row.append(Tile.FLOOR)

            elif tx % 2 == 0 and ty % 2 == 1:
                tunnel_row = len(maze) // 2
                if tx == 0:
                    if y == tunnel_row:
                        row.append(Tile.FLOOR)
                    else:
                        row.append(Tile.WALL)
                elif tx == 2 * len(maze[0]):
                    if y == tunnel_row:
                        row.append(Tile.FLOOR)
                    else:
                        row.append(Tile.WALL)
                elif (
                    y < len(maze) and 0 < x <= len(maze[y])
                    and (maze[y][x - 1] & 2)
                ):
                    row.append(Tile.WALL)
                else:
                    row.append(Tile.FLOOR)

            else:
                row.append(Tile.CORNER)

        tile_map.append(row)
    return tile_map


def tiles_positions(maze: list[list[int]]) -> tuple[list[int], list[int]]:
    """
    Calculate the pixel positions for the tiles in the maze.

    Args:
        maze: The grid representing the maze layout.

    Returns:
        A tuple containing two lists: x_positions and y_positions.
    """
    x_positions = []
    x = 0

    for tx in range(2 * len(maze[0]) + 1):
        x_positions.append(x)
        x += WALL_SIZE if tx % 2 == 0 else FLOOR_SIZE

    y_positions = []
    y = 0

    for ty in range(2 * len(maze) + 1):
        y_positions.append(y)
        y += WALL_SIZE if ty % 2 == 0 else FLOOR_SIZE
    return x_positions, y_positions


def corner_code(tile_map: list[list[Tile]], ty: int, tx: int) -> int:
    """
    Calculate the corner code for a given tile position.

    Args:
        tile_map: The 2D list representing the tile map of the maze.
        ty: The y-coordinate of the tile.
        tx: The x-coordinate of the tile.
    Returns:
        An integer representing the corner code for the tile.
    """
    bits = (
        (-1, 0, 1),  # N
        (0, 1, 2),   # E
        (1, 0, 4),   # S
        (0, -1, 8),  # W
    )
    max_y = len(tile_map)
    max_x = len(tile_map[0]) if max_y else 0

    code = 0
    for dy, dx, bit in bits:
        ny = ty + dy
        nx = tx + dx
        if (
            0 <= ny < max_y and 0 <= nx < max_x
            and tile_map[ny][nx] == Tile.WALL
        ):
            code |= bit
    return code


def draw_maze(
        surface: Surface,
        tile_map: list[list[Tile]],
        maze: list[list[int]],
        spritesheet: Spritesheet,
        color_42: Color | None = None) -> None:
    """
    Draw the maze on the given surface.

    Args:
        surface: The Pygame surface to draw on.
        tile_map: The 2D list representing the tile map of the maze.
        maze: The grid representing the maze layout.
        spritesheet: The Spritesheet instance containing the tile images.
        color_42: Optional color to highlight cells with value 15 in the maze.

    Returns:
        None
    """
    if color_42 is None:
        color_42 = Color(CYAN)
    x_positions, y_positions = tiles_positions(maze)

    for ty in range(len(tile_map)):
        for tx in range(len(tile_map[0])):

            x = tx // 2
            y = ty // 2

            x_start = x_positions[tx]
            y_start = y_positions[ty]

            if tile_map[ty][tx] == Tile.WALL:
                if ty % 2 == 0:
                    sprite = spritesheet.get_sprite(*Tiles[17])
                if tx % 2 == 0:
                    sprite = spritesheet.get_sprite(*Tiles[16])
                surface.blit(sprite, (x_start, y_start))

            if tile_map[ty][tx] == Tile.CORNER:
                code = corner_code(tile_map, ty, tx)
                if code == 0:
                    continue
                sprite = spritesheet.get_sprite(*Tiles[code])
                surface.blit(sprite, (x_start, y_start))

            if tile_map[ty][tx] == Tile.FLOOR:
                if 0 < x < len(maze[0]) and maze[y][x] == 15:
                    pygame.draw.rect(
                        surface,
                        color_42,
                        pygame.Rect(
                            (x_start - 4, y_start - 4),
                            (FLOOR_SIZE + 8, FLOOR_SIZE + 8)
                            ),
                        border_radius=5
                        )
                else:
                    continue
