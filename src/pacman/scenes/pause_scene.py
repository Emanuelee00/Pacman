"""Scene displayed when the game is paused."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from .play_scene import PlayScene
from .scene import Scene
from .menu_scene import MenuScene
from pacman.settings import YELLOW, WHITE

if TYPE_CHECKING:
    from pacman.game import Game
    from pacman.settings import MenuOption
    from pygame import Surface


class PauseScene(Scene):
    """Class representing the pause menu scene."""

    def __init__(self, game: Game) -> None:
        """
        Initialize the pause scene.

        Args:
            game: The main game instance.
        """
        super().__init__(game)
        self.mid_w: int
        self.mid_h: int
        self.mid_w, self.mid_h = (
            self.game.screen.get_width() // 2,
            self.game.screen.get_height() // 2
        )
        self.pause_start = pygame.time.get_ticks()
        self._elapsed_time = 0

        self.options: dict[int, MenuOption] = {
            0: {
                'name': "CONTINUE",
                'position': (self.mid_w, self.mid_h - 60),
            },
            1: {
                'name': "RESTART",
                'position': (self.mid_w, self.mid_h),
            },
            2: {
                'name': "RETURN TO MENU",
                'position': (self.mid_w, self.mid_h + 60),
            },
        }
        self.selected_option: int = 0

        self.frame_slower: float = 0
        self.cursor_img: Surface = pygame.transform.scale(
            self.game.cursor_animation[0], (28, 28)
            )
        self.cursor_rect = self.cursor_img.get_rect()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Handle user input events for the pause menu.

        Args:
            events: A list of Pygame events to handle.
        """
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected_option = (
                        (self.selected_option + 1) % len(self.options)
                        )
                if e.key == pygame.K_UP:
                    self.selected_option = (
                        (self.selected_option - 1) % len(self.options)
                        )
                if e.key == pygame.K_RETURN:
                    self._select_option()

    def _animate_cursor(self) -> None:
        """Animate the cursor next to the selected menu option."""
        current_center = self.cursor_rect.center
        frames = self.game.cursor_animation
        self.frame_slower += 0.2
        if self.frame_slower >= len(frames):
            self.frame_slower = 0
        self.cursor_img = frames[int(self.frame_slower)]
        self.cursor_rect = self.cursor_img.get_rect(center=current_center)

    def update(self) -> None:
        """Update cursor animation and elapsed time."""
        if self.prev_scene:
            self._elapsed_time = pygame.time.get_ticks() - self.pause_start
        self._animate_cursor()

    def _select_option(self) -> None:
        """
        Take action corresponding to the selected menu option.

        Options:
            0: Continue the game (return to previous scene)
            1: Restart the current level
            2: Return to the main menu
        """
        match self.selected_option:
            case 0:
                self.exit_scene()
            case 1:
                self.exit_scene()
                if self.game.scenes_stack:
                    self.game.scenes_stack.pop()
                    self.game.score = 0
                PlayScene(self.game).enter_scene()
            case 2:
                self.exit_scene()
                if self.game.scenes_stack:
                    self.game.scenes_stack.pop()
                    self.game.score = 0
                MenuScene(self.game).enter_scene()

    def render(self, surface: Surface) -> None:
        """
        Render the pause menu overlay and options.

        Args:
            surface: The Pygame surface to render the menu on.
        """
        sx, sy = surface.get_size()
        overlay = pygame.Surface((sx // 2.75, sy // 1.75), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        mid_w = overlay.get_width() // 2
        mid_h = overlay.get_height() // 2
        surface.blit(
            overlay,
            (sx//2 - mid_w, sy//2 - mid_h)
            )
        border_rect = pygame.Rect(
            sx//2 - mid_w, sy//2 - mid_h,
            *overlay.get_size()
            )
        pygame.draw.rect(
            surface,
            Color(YELLOW),
            border_rect,
            width=3,
            border_radius=10
            )
        surface.blit(self.cursor_img, self.cursor_rect)
        for i, option in self.options.items():
            color = (
                Color(YELLOW)
                if i == self.selected_option
                else Color(WHITE)
                )
            text_rect = self.game.draw_text(
                surface,
                option['name'],
                color,
                *option['position'],
                size="small"
                )
            if i == self.selected_option:
                self.cursor_rect.center = (
                    option['position'][0] - text_rect.width // 2 - 30,
                    option['position'][1] + 3
                )
