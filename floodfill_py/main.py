"""
Main entry point for Micromouse Flood-Fill algorithm demonstration.
"""

from cell import Cell, Maze, create_empty_maze
from mouse import Mouse
from floodFill import flood_fill, navigate, navigate_ui
from mazes import wall_arrangement_10x10, build_preset_maze


def main() -> None:
    maze_size = 10
    maze = build_preset_maze(maze_size)

    # Initial flood fill from goal center
    flood_fill(maze, maze.get_centers())

    mouse = Mouse()
    navigate(mouse, maze)


if __name__ == "__main__":
    main()
