"""Scene representing the main menu of the game."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from pygame import Color
from .play_scene import PlayScene
from .scene import Scene
from .highscore_scene import HighScoreScene
from .instructions_scene import InstructionScene
from pacman.settings import YELLOW, WHITE, BLUE

if TYPE_CHECKING:
    from pacman.game import Game
    from pacman.settings import MenuOption
    from pygame import Surface


class MenuScene(Scene):
    """Class representing the main menu scene."""

    def __init__(self, game: Game):
        """
        Initialize the menu scene.

        Args:
            game: The main game instance.

        Attributes:
            mid_w: The horizontal center of the screen.
            mid_h: The vertical center of the screen.
            options: A dict of menu options and their positions.
            selected_option: The index of the currently selected menu option.
            frame_slower: A counter to control cursor animation speed.
            cursor_animation: A dict of cursor images for animation frames.
            cursor_img: The current image of the cursor.
            cursor_rect: The rect representing the cursor's position and size.
        """
        super().__init__(game)
        self.mid_w: int
        self.mid_h: int
        self.mid_w, self.mid_h = (
            self.game.screen.get_width() // 2,
            self.game.screen.get_height() // 2
        )

        self.options: dict[int, MenuOption] = {
            0: {
                'name': "PLAY",
                'position': (self.mid_w, self.mid_h - 60),
            },
            1: {
                'name': "INSTRUCTIONS",
                'position': (self.mid_w, self.mid_h),
            },
            2: {
                'name': "HIGH SCORES",
                'position': (self.mid_w, self.mid_h + 60),
            },
            3: {
                'name': "EXIT",
                'position': (self.mid_w, self.mid_h + 120),
            }
        }
        self.selected_option: int = 0
        self.frame_slower: float = 0
        self.cursor_img: Surface = pygame.transform.scale(
            self.game.cursor_animation[0], (28, 28)
            )
        self.cursor_rect = self.cursor_img.get_rect()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle user input events for the menu."""
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
        """Animate the cursor."""
        current_center = self.cursor_rect.center
        frames = self.game.cursor_animation
        self.frame_slower += 0.2
        if self.frame_slower >= len(frames):
            self.frame_slower = 0
        self.cursor_img = frames[int(self.frame_slower)]
        self.cursor_rect = self.cursor_img.get_rect(center=current_center)

    def update(self) -> None:
        """Update the menu scene."""
        self._animate_cursor()

    def _select_option(self) -> None:
        """Handle the action for the selected menu option."""
        match self.selected_option:
            case 0:
                self.exit_scene()
                PlayScene(self.game).enter_scene()
            case 1:
                InstructionScene(self.game).enter_scene()
            case 2:
                HighScoreScene(self.game).enter_scene()
            case 3:
                self.game.running = False

    def render(self, surface: pygame.Surface) -> None:
        """Render the menu scene."""
        surface.fill((0, 0, 0))

        font_in, font_out = (
            self.game.fonts["title_in"], self.game.fonts["title_out"]
        )

        title_in = font_in.render("PACMAN", True, Color(YELLOW))
        title_out = font_out.render("PACMAN", True, Color(BLUE))

        surface.blit(
            title_in,
            (self.mid_w - title_in.get_width() // 2, self.mid_h - 300)
            )
        surface.blit(
            title_out,
            (self.mid_w - title_out.get_width() // 2, self.mid_h - 300)
            )
        surface.blit(self.cursor_img, self.cursor_rect)

        for i, option in self.options.items():
            color = (
                Color(YELLOW) if i == self.selected_option else Color(WHITE)
            )
            text_rect = self.game.draw_text(
                surface,
                option['name'],
                color,
                *option['position']
                )
            if i == self.selected_option:
                self.cursor_rect.center = (
                    option['position'][0] - text_rect.width // 2 - 30,
                    option['position'][1] + 3
                )
