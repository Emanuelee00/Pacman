"""Module for ghost chase strategies in the Pacman game."""

from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING, Protocol
from pacman.settings import Directions

if TYPE_CHECKING:
    from pacman.characters.ghosts import Ghost


class ChaseStrategy(Protocol):
    """Protocol for ghost chase strategies."""

    def get_direction(
            self,
            ghost: Ghost,
            current_cell: tuple[int, int],
            target_cell: tuple[int, int]
            ) -> Directions:
        """
        Find the next direction for a ghost to chase Pacman.

        Args:
            ghost: The ghost for which to calculate the next move.
            current_cell: The current cell coordinates of the ghost.
            target_cell: The target cell based on Pacman's position.

        Returns:
            The direction the ghost should move to chase Pacman.
        """
        ...


class EuclideanChaseStrategy:
    """Chase strategy that uses Euclidean distance to find the next move."""

    def get_direction(
            self,
            ghost: Ghost,
            current_cell: tuple[int, int],
            target_cell: tuple[int, int]
            ) -> Directions:
        """Calculate the next direction based on the Euclidean distance."""
        cx, cy = current_cell
        next_direction = Directions.NONE
        min_dist = float("inf")

        available_directions = [
            direction for direction in Directions
            if direction != Directions.NONE
            and direction != ghost._opposite_direction(ghost.direction)
            and ghost._can_move(direction, cx, cy)
        ]

        if not available_directions:
            return ghost._opposite_direction(ghost.direction)

        if len(available_directions) == 1:
            return available_directions[0]

        for direction in available_directions:
            nx = cx + direction.dx
            ny = cy + direction.dy
            new_dist = ghost.distance_target((nx, ny), target_cell)

            if new_dist < min_dist:
                min_dist = new_dist
                next_direction = direction

        return next_direction


class BFSChaseStrategy:
    """Chase strategy that uses breadth-first search to find the next move."""

    def get_direction(
            self,
            ghost: Ghost,
            current_cell: tuple[int, int],
            target_cell: tuple[int, int]
            ) -> Directions:
        """Calculate the next direction based on breadth-first search."""
        cx, cy = current_cell
        next_direction = Directions.NONE
        queue: deque[tuple[tuple[int, int], list[Directions]]] = (
            deque([((cx, cy), [])]
                  )
        )
        visited: set[tuple[int, int]] = {(cx, cy)}

        while queue:
            (x, y), path = queue.popleft()

            if (x, y) == target_cell:
                return path[0] if path else Directions.NONE

            for direction in Directions:
                nx, ny = x + direction.dx, y + direction.dy

                if (
                    nx < 0
                    or ny < 0
                    or ny >= len(ghost.maze)
                    or nx >= len(ghost.maze[ny])
                ):
                    continue

                if (
                    (nx, ny) not in visited
                    and ghost._can_move(direction, x, y)
                ):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [direction]))
        return next_direction
