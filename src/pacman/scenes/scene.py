"""Module containing the base Scene class."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame
    from pacman.game import Game


class Scene():
    """Base class for all game scenes."""

    def __init__(self, game: Game) -> None:
        """Initialize the scene state.

        Args:
            game: Reference to the main Game object.
        """
        self.game = game
        self.prev_scene: Scene | None = None

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Process a list of Pygame events."""
        ...

    def render(self, surface: pygame.Surface) -> None:
        """Render the scene on the given surface."""
        ...

    def update(self) -> None:
        """Update the scene state."""
        ...

    def enter_scene(self) -> None:
        """Push the scene onto the game's scene stack."""
        if self.game.scenes_stack:
            self.prev_scene = self.game.scenes_stack[-1]
        self.game.scenes_stack.append(self)

    def exit_scene(self) -> None:
        """Pop the scene from the game's scene stack."""
        self.game.scenes_stack.pop()
        del self
