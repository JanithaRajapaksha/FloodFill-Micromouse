"""
Lightweight demonstration UI for Micromouse Flood-Fill using Pygame.
Dynamically scales to any maze size (5x5, 6x6, 10x10, 16x16, etc.).
"""

import os
import sys
from typing import List, Optional, Tuple

from cell import Maze
from mouse import Mouse
from floodFill import navigate, navigate_ui
from mazes import build_preset_maze, PRESET_CONFIGURATIONS

# Palette
COLOR_BG = (235, 245, 235)
COLOR_GRID = (180, 190, 180)
COLOR_VISITED = (200, 220, 255)
COLOR_WALL = (220, 20, 60)
COLOR_TEXT = (100, 100, 100)


def run_simulation(
    maze_size: int = 10,
    maze: Optional[Maze] = None,
    step_delay: float = 0.25,
    window_size: int = 800,
) -> None:
    """
    Run the visual demonstration of the micromouse solving the maze.

    Parameters:
        maze_size: Maze dimension (used if maze is not provided).
        maze: Pre-configured Maze instance. If None, loaded from presets.
        step_delay: Seconds to wait between mouse moves.
        window_size: Width and height of the Pygame window in pixels.
    """
    if maze is None:
        if maze_size in PRESET_CONFIGURATIONS:
            maze = build_preset_maze(maze_size)
        else:
            raise ValueError(f"No preset for size {maze_size}. Provide a configured Maze object.")

    # Check for pygame availability
    try:
        import pygame
    except ImportError:
        print("Pygame is not installed. To run the visual demo, install it with: pip install pygame")
        print(f"Running console navigation for {maze.size}x{maze.size} maze instead:")
        navigate(Mouse(), maze, verbose=True)
        return

    # Solve trajectory
    path = navigate_ui(Mouse(), maze)

    # Initialize Pygame display
    pygame.init()
    win = pygame.display.set_mode((window_size, window_size))
    pygame.display.set_caption(f"Micromouse Flood-Fill Demo ({maze.size}x{maze.size})")

    # Load and scale mouse icon
    dim = maze.size
    cell_size = window_size // dim
    mouse_w = max(12, int(cell_size * 0.75))
    mouse_h = max(12, int(cell_size * 0.75))

    asset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets", "mouse.png")
    mouse_surface = None
    if os.path.exists(asset_path):
        try:
            raw_img = pygame.image.load(asset_path)
            mouse_surface = pygame.transform.scale(raw_img, (mouse_w, mouse_h))
        except Exception:
            mouse_surface = None

    # Fallback mouse graphic if asset missing
    if mouse_surface is None:
        mouse_surface = pygame.Surface((mouse_w, mouse_h), pygame.SRCALPHA)
        pygame.draw.polygon(mouse_surface, (50, 100, 220), [
            (mouse_w // 2, 0),
            (0, mouse_h),
            (mouse_w, mouse_h),
        ])

    font = pygame.font.Font(None, max(14, cell_size // 4))
    visited_cells = set()
    clock = pygame.time.Clock()

    def draw_state(cur_x: int, cur_y: int, cur_orient: int) -> None:
        win.fill(COLOR_BG)

        # Draw visited cell backgrounds
        for vx, vy in visited_cells:
            rect = (vx * cell_size, (dim - 1 - vy) * cell_size, cell_size, cell_size)
            pygame.draw.rect(win, COLOR_VISITED, rect)

        # Draw grid lines
        for i in range(dim + 1):
            pos = i * cell_size
            pygame.draw.line(win, COLOR_GRID, (pos, 0), (pos, window_size), 1)
            pygame.draw.line(win, COLOR_GRID, (0, pos), (window_size, pos), 1)

        # Draw maze walls
        wall_thickness = max(2, min(6, cell_size // 10))
        for row in maze.cells:
            for cell in row:
                cx = cell.x
                cy = dim - 1 - cell.y
                x0 = cx * cell_size
                y0 = cy * cell_size
                x1 = (cx + 1) * cell_size
                y1 = (cy + 1) * cell_size

                if cell.is_north_wall:
                    pygame.draw.line(win, COLOR_WALL, (x0, y0), (x1, y0), wall_thickness)
                if cell.is_south_wall:
                    pygame.draw.line(win, COLOR_WALL, (x0, y1), (x1, y1), wall_thickness)
                if cell.is_west_wall:
                    pygame.draw.line(win, COLOR_WALL, (x0, y0), (x0, y1), wall_thickness)
                if cell.is_east_wall:
                    pygame.draw.line(win, COLOR_WALL, (x1, y0), (x1, y1), wall_thickness)

                # Optional cell coordinates
                if cell_size >= 40:
                    lbl = font.render(f"{cell.x},{cell.y}", True, COLOR_TEXT)
                    win.blit(lbl, (x0 + 4, y0 + 4))

        # Rotate and draw mouse
        # Orientation: 0: North, 1: East, 2: South, 3: West
        rotations = {0: 0, 1: -90, 2: 180, 3: 90}
        rotated_mouse = pygame.transform.rotate(mouse_surface, rotations.get(cur_orient, 0))
        mouse_rect = rotated_mouse.get_rect(
            center=(
                cur_x * cell_size + cell_size // 2,
                (dim - 1 - cur_y) * cell_size + cell_size // 2,
            )
        )
        win.blit(rotated_mouse, mouse_rect)
        pygame.display.flip()

    # Step-by-step animation
    steps = [[0, 0, 0]] + path
    running = True

    for step_x, step_y, step_orient in steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
        if not running:
            break

        visited_cells.add((step_x, step_y))
        draw_state(step_x, step_y, step_orient)
        pygame.time.delay(int(step_delay * 1000))

    # Keep window open until closed by user
    while running:
        clock.tick(15)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


def main() -> None:
    size = 10
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
        except ValueError:
            pass
    run_simulation(maze_size=size)


if __name__ == "__main__":
    main()
