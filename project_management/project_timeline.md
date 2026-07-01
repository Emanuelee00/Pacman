# Project Timeline — Pacman


## Authors

| Alias | Identity |
|---|---|
| eielmini | Emanuele Ielmini |
| zadjerma | Zakaria Djermani |

---

## Week 1 — May 6–12 | Foundation

**Goal:** Get a playable prototype with maze rendering and Pacman movement.

### Features added
- **Project setup** — Initial Pygame project structure, `.gitignore`, base files
- **Maze rendering** — Tile-based maze drawn to screen using a spritesheet
- **Pacman movement** — First working movement logic with keyboard input
- **Scene manager** — Basic scene management system (menu → game)
- **Menu scene** — First navigable main menu
- **Pacgums (dots)** — Pac-dots placed inside the maze, collectible by Pacman
- **Ghost skeleton** — Base ghost class introduced, no AI yet
- **File structure** — Major reorganization of the project structure for clarity

### State at end of week
The game showed a maze, a moving Pacman collecting dots, and a menu screen. No ghost AI, no score, no game over.

### Commits
`f96c240` `81b11a2` `f4025b7` `b5c4529` `30c3cc3` `40bf2d6` `2180e5d` `d1dc9d7` `74bd09f` `50d6f2d` `4619f03`

---

## Week 2 — May 13–19 | Ghosts & Game Structure

**Goal:** Implement the first ghost, build the highscore system, and organize the scene architecture.

### Features added
- **Cheat code** — First "42" cheat code and JSON config parser
- **Game over screen** — Displayed when Pacman dies
- **High score system** — Player name input + scores saved to a JSON file (PR #1 & #2)
- **Blinky** — First fully working ghost with movement and chase logic
- **Spritesheet system** — `Spritesheet` class to load and slice sprite images for all characters
- **Maze spritesheet** — Dedicated spritesheet for maze tile rendering
- **Inky & Pinky** — Two more ghosts implemented with distinct behaviors (PR #3)
- **Ghost base class refactored** — Shared ghost logic moved to abstract `Ghost` class
- **Scene architecture** — Scenes reorganized into a clean hierarchy

### State at end of week
Three ghosts chasing Pacman, a working highscore screen, and a solid scene system. No frightened mode, no levels yet.

### Commits
`637212e` `c71a77d` `569f9ce` `29d5884` `15644cf` `774b7bf` `f587711` `0fdf898` `be1adf8` `9160014` `5143f9a` `5a8b3c1` `1246e9c` `3ce93db` `300682f` `f4a7461`

---

## Week 3 — May 20–26 | Gameplay Complete

**Goal:** Implement all remaining gameplay features and finalize the full game loop.

### Features added
- **All scenes completed** — Play, pause, instructions, end game, win screen, highscore screen (PR #4)
- **Missile (cheat feature)** — Pacman can shoot a missile to destroy ghosts
- **Pacman death** — Death animation triggered on ghost collision
- **42 cheat** — "42" typed in-game activates a special visual mode
- **Frightened mode** — Ghosts turn blue and become vulnerable after Pacman eats a power pellet; they flash before returning to normal
- **Clyde** — Fourth ghost added, with its own targeting behavior
- **BFS pathfinding** — Ghosts can use Breadth-First Search for smarter chase behavior (PR #5 prep)
- **Strategy pattern** — Ghost AI decoupled via `ChaseStrategy` interface (`EuclideanChaseStrategy`, `BFSChaseStrategy`)
- **Level manager** — `LevelManager` class handles level progression, maze generation per level, and character respawn
- **Pause scene** — In-game pause with proper timer management
- **Settings screen** — Settings accessible from the menu
- **Maze scaling** — Maze correctly scaled to the game canvas size
- **Timeout between levels** — Brief wait screen between level transitions
- **Win screen** — Displayed when all levels are completed
- **Score display** — Points shown when eating a ghost

### State at end of week
Fully playable game: multiple levels, four ghosts with AI, all scenes, cheat codes, high scores, win/lose conditions.

### Commits
`8d35237` `945f7d4` `68b3fb8` `4f0c86f` `852e1c5` `cecae4b` `5603c03` `42ce375` `9dc7b68` `94efa17` `e25d530` `58e5510` `b2a9b0b` `118a05a` `d3b56fc` `42f4069` `f043ea6` `5e913fa` `8468d5e` `d1c7d0c` `ede6aae` `b5d629a` `db01024` `0483a36` `6c014e2` `26b7b6c` `b33b842` `180380c` `604294d` `39b782c` `df7bbb5` `5ffa723` `62eb314` `8510e56` `d392023` `b42d0b3` `25f328c` `6fb114d` `573569f` `dc777d5` `2834ca1` `a0ff19d` `ba599ce` `16af203` `8bd3ed8` `b8e3222` `59f323b`

---

## Week 4 — May 30 – June 8 | Packaging & Fixes

**Goal:** Port the project to the 42 school repo, package a standalone binary, and fix remaining issues.

### Features added / fixed
- **Project ported to 42 repo** — Full codebase uploaded with build tooling
- **Standalone binary** — Game packaged with PyInstaller (`pacman` executable)
- **Build system** — `Makefile`, `pyproject.toml`, `uv.lock`, `pacman.spec` added
- **Full README** — Complete documentation written
- **Window dimensions tuned** — Final window size adjusted in `config.json` and `settings.py`
- **Config cleanup** — Redundant entries removed from `config.json`
- **Level config fix** — Parser adjusted for correct level parameter handling
- **Ghost config validation fix** — Bug in ghost config field validation corrected

### State at end of week
Final deliverable: fully packaged game, clean config, no known bugs.

### Commits
`660a6c4` `729d38a` `e65034c` `796c025` `02a966e`

---

## Feature Evolution Summary

| Feature | Week |
|---|---|
| Maze rendering | 1 |
| Pacman movement | 1 |
| Scene manager | 1 |
| Pac-dots | 1 |
| Ghost skeleton | 1 |
| High score system | 2 |
| Game over screen | 2 |
| Blinky (ghost 1) | 2 |
| Inky, Pinky (ghosts 2 & 3) | 2 |
| Spritesheet system | 2 |
| All scenes (pause, win, instructions…) | 3 |
| Pacman death animation | 3 |
| Frightened mode (power pellets) | 3 |
| Clyde (ghost 4) | 3 |
| BFS + Strategy pattern for ghost AI | 3 |
| Level manager (multi-level) | 3 |
| Missile cheat | 3 |
| 42 easter egg | 3 |
| Standalone binary (PyInstaller) | 4 |
| Final bug fixes | 4 |

## Pull Requests

| PR | Branch | Date | Content |
|----|--------|------|---------|
| #1 | highscore | 13/05/2026 | Game over + highscore + name input |
| #2 | highscore | 13/05/2026 | Highscore completion |
| #3 | ghosts | 18/05/2026 | Blinky, Inky, Pinky + refactor |
| #4 | scene | 20/05/2026 | All scenes + missile |
| #5 | level_cheat | 27/05/2026 | Cheat level + ghost points fix |

## Global Statistics

| Metric | Value |
|---|---|
| Total duration | 33 days (06/05 → 08/06/2026) |
| Total commits | 73 |
| Merged pull requests | 5 |
| Contributors | 2 (Emanuele Ielmini, Zakaria Djermani) |
