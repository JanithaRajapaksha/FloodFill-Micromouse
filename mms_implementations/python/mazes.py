"""
Benchmark test maze configurations and MMS .num file loader for Micromouse simulation.
Supports:
- MMS .num format files (example1, example2, example3, example4, example5, blank)
- Standard preset benchmarks (5x5, 6x6, 10x10, 16x16)
"""

import os
from typing import Optional, Union
from cell import Cell, Maze, create_empty_maze

MAZES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mazes")


def load_num_maze(filepath: str) -> Maze:
    """
    Parse an MMS .num maze file into a Maze object.
    Format: Each line contains 'x y north east south west' (0 or 1 for walls).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Maze file not found: {filepath}")

    records = []
    max_x = 0
    max_y = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                x = int(parts[0])
                y = int(parts[1])
                n = int(parts[2])
                e = int(parts[3])
                s = int(parts[4])
                w = int(parts[5])
                records.append((x, y, n, e, s, w))
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    width = max_x + 1
    height = max_y + 1
    maze = create_empty_maze(width, height)

    for x, y, n, e, s, w in records:
        cell = maze[x, y]
        if n:
            cell.set_north_wall(maze)
        if e:
            cell.set_east_wall(maze)
        if s:
            cell.set_south_wall(maze)
        if w:
            cell.set_west_wall(maze)

    maze.update_all_wall_codes()
    return maze


def get_mms_preset_maze(preset_name: str) -> Maze:
    """
    Load one of the MMS example mazes:
    'example1', 'example2', 'example3', 'example4', 'example5', or 'blank'.
    """
    if not preset_name.endswith(".num"):
        preset_name = f"{preset_name}.num"

    filepath = os.path.join(MAZES_DIR, preset_name)
    return load_num_maze(filepath)


# =========================================================================
# Preset Benchmarks: 5x5, 6x6, 10x10, 16x16
# =========================================================================

def wall_arrangement_x5(maze: Maze) -> None:
    """Wall arrangement for a 5x5 maze."""
    maze[0, 0].set_east_wall(maze)
    maze[2, 0].set_north_wall(maze)
    maze[2, 0].set_east_wall(maze)
    maze[3, 0].set_north_wall(maze)
    maze[2, 1].set_north_wall(maze)
    maze[2, 1].set_east_wall(maze)
    maze[0, 2].set_south_wall(maze)
    maze[0, 2].set_east_wall(maze)
    maze[1, 2].set_east_wall(maze)
    maze[3, 2].set_north_wall(maze)
    maze[3, 2].set_east_wall(maze)
    maze[0, 3].set_north_wall(maze)
    maze[1, 4].set_east_wall(maze)
    maze[3, 4].set_south_wall(maze)
    maze[4, 4].set_south_wall(maze)
    maze.update_all_wall_codes()


def wall_arrangement_x6(maze: Maze) -> None:
    """Wall arrangement for a 6x6 maze."""
    maze[2, 0].set_north_wall(maze)
    maze[3, 0].set_north_wall(maze)
    maze[4, 0].set_east_wall(maze)
    maze[5, 0].set_west_wall(maze)
    maze[0, 1].set_east_wall(maze)
    maze[2, 1].set_north_wall(maze)
    maze[3, 1].set_north_wall(maze)
    maze[4, 1].set_west_wall(maze)
    maze[5, 1].set_west_wall(maze)
    maze[0, 2].set_east_wall(maze)
    maze[1, 2].set_east_wall(maze)
    maze[3, 2].set_east_wall(maze)
    maze[4, 2].set_north_wall(maze)
    maze[5, 2].set_north_wall(maze)
    maze[1, 3].set_north_wall(maze)
    maze[1, 3].set_east_wall(maze)
    maze[2, 3].set_north_wall(maze)
    maze[3, 3].set_east_wall(maze)
    maze[1, 4].set_north_wall(maze)
    maze[2, 4].set_north_wall(maze)
    maze[3, 4].set_north_wall(maze)
    maze[4, 4].set_east_wall(maze)
    maze[4, 5].set_east_wall(maze)
    maze.update_all_wall_codes()


def wall_arrangement_10x10(maze: Maze) -> None:
    """Wall arrangement for a 10x10 maze."""
    # Row 0
    maze[0, 1].set_east_wall(maze)
    maze[0, 3].set_north_wall(maze)
    maze[0, 4].set_west_wall(maze)
    maze[0, 6].set_east_wall(maze)

    # Row 1
    maze[1, 0].set_east_wall(maze)
    maze[1, 2].set_east_wall(maze)
    maze[1, 5].set_north_wall(maze)
    maze[1, 6].set_west_wall(maze)

    # Row 2
    maze[2, 1].set_north_wall(maze)
    maze[2, 3].set_east_wall(maze)
    maze[2, 4].set_west_wall(maze)
    maze[2, 6].set_west_wall(maze)

    # Row 3
    maze[3, 2].set_east_wall(maze)
    maze[3, 3].set_north_wall(maze)
    maze[3, 4].set_north_wall(maze)
    maze[3, 5].set_west_wall(maze)
    maze[3, 7].set_east_wall(maze)

    # Row 4
    maze[4, 2].set_east_wall(maze)
    maze[4, 3].set_north_wall(maze)
    maze[4, 4].set_north_wall(maze)
    maze[4, 5].set_west_wall(maze)
    maze[4, 7].set_west_wall(maze)

    # Row 5
    maze[5, 2].set_east_wall(maze)
    maze[5, 3].set_south_wall(maze)
    maze[5, 4].set_south_wall(maze)
    maze[5, 5].set_west_wall(maze)
    maze[5, 8].set_west_wall(maze)

    # Row 6
    maze[6, 3].set_north_wall(maze)
    maze[6, 4].set_west_wall(maze)
    maze[6, 5].set_west_wall(maze)
    maze[6, 8].set_east_wall(maze)

    # Row 7
    maze[7, 0].set_north_wall(maze)
    maze[7, 1].set_east_wall(maze)
    maze[7, 2].set_north_wall(maze)
    maze[7, 3].set_north_wall(maze)
    maze[7, 5].set_east_wall(maze)
    maze[7, 6].set_east_wall(maze)
    maze[7, 8].set_east_wall(maze)

    # Row 8
    maze[8, 1].set_north_wall(maze)
    maze[8, 2].set_east_wall(maze)
    maze[8, 6].set_north_wall(maze)
    maze[8, 7].set_east_wall(maze)
    maze[8, 8].set_north_wall(maze)

    # Row 9
    maze[9, 1].set_east_wall(maze)
    maze[9, 2].set_east_wall(maze)
    maze[9, 4].set_east_wall(maze)
    maze[9, 6].set_east_wall(maze)
    maze[9, 7].set_east_wall(maze)
    maze[9, 8].set_east_wall(maze)
    maze.update_all_wall_codes()


def build_preset_maze(identifier: Union[int, str]) -> Maze:
    """
    Factory to construct a preset maze by dimension (5, 6, 10) or name
    ('example1', 'example2', 'example3', 'example4', 'example5', 'blank').
    """
    if isinstance(identifier, int):
        if identifier == 5:
            maze = create_empty_maze(5)
            wall_arrangement_x5(maze)
            return maze
        elif identifier == 6:
            maze = create_empty_maze(6)
            wall_arrangement_x6(maze)
            return maze
        elif identifier == 10:
            maze = create_empty_maze(10)
            wall_arrangement_10x10(maze)
            return maze
        elif identifier == 16:
            return get_mms_preset_maze("example1")
        else:
            raise ValueError(f"No preset maze of dimension {identifier}")
    elif isinstance(identifier, str):
        return get_mms_preset_maze(identifier)
    else:
        raise TypeError(f"Invalid maze identifier type: {type(identifier)}")
