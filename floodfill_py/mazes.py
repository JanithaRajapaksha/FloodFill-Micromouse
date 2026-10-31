"""
Preset maze wall configurations for Micromouse flood-fill simulations.
Includes standard 5x5, 6x6, 10x10, and 16x16 maze layouts.
"""

from cell import Cell, Maze, create_empty_maze


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
    maze[6, 6].set_east_wall(maze)
    maze[6, 7].set_east_wall(maze)

    # Row 7
    maze[7, 1].set_north_wall(maze)
    maze[7, 3].set_north_wall(maze)
    maze[7, 5].set_north_wall(maze)
    maze[7, 8].set_west_wall(maze)

    # Row 8
    maze[8, 2].set_north_wall(maze)
    maze[8, 4].set_east_wall(maze)
    maze[8, 6].set_east_wall(maze)
    maze[8, 7].set_east_wall(maze)

    # Row 9
    maze[9, 0].set_north_wall(maze)
    maze[9, 5].set_west_wall(maze)
    maze[9, 8].set_north_wall(maze)

    # Guard the center goal cells
    maze[4, 4].set_south_wall(maze)
    maze[4, 5].set_south_wall(maze)
    maze[5, 4].set_north_wall(maze)
    maze[5, 5].set_north_wall(maze)
    maze[4, 3].set_west_wall(maze)
    maze[4, 6].set_east_wall(maze)
    maze[5, 3].set_west_wall(maze)
    maze[5, 6].set_east_wall(maze)

    maze.update_all_wall_codes()


def wall_arrangement_16x16(maze: Maze) -> None:
    """Wall arrangement for a 16x16 maze."""
    # Column 0
    maze[0, 0].set_east_wall(maze)
    maze[0, 1].set_east_wall(maze)
    maze[0, 4].set_east_wall(maze)
    maze[0, 5].set_east_wall(maze)
    maze[0, 6].set_east_wall(maze)
    maze[0, 7].set_east_wall(maze)
    maze[0, 8].set_east_wall(maze)
    maze[0, 9].set_east_wall(maze)
    maze[0, 10].set_east_wall(maze)
    maze[0, 11].set_east_wall(maze)
    maze[0, 14].set_east_wall(maze)
    maze[0, 15].set_east_wall(maze)

    # Column 1
    maze[1, 1].set_east_wall(maze)
    maze[1, 2].set_east_wall(maze)
    maze[1, 2].set_north_wall(maze)
    maze[1, 3].set_east_wall(maze)
    maze[1, 4].set_east_wall(maze)
    maze[1, 5].set_east_wall(maze)
    maze[1, 6].set_east_wall(maze)
    maze[1, 7].set_east_wall(maze)
    maze[1, 8].set_east_wall(maze)
    maze[1, 9].set_east_wall(maze)
    maze[1, 10].set_east_wall(maze)
    maze[1, 11].set_east_wall(maze)
    maze[1, 12].set_east_wall(maze)
    maze[1, 12].set_north_wall(maze)
    maze[1, 13].set_east_wall(maze)
    maze[1, 14].set_east_wall(maze)

    # Column 2
    maze[2, 0].set_north_wall(maze)
    maze[2, 1].set_north_wall(maze)
    maze[2, 3].set_east_wall(maze)
    maze[2, 4].set_east_wall(maze)
    maze[2, 5].set_east_wall(maze)
    maze[2, 6].set_east_wall(maze)
    maze[2, 8].set_east_wall(maze)
    maze[2, 9].set_east_wall(maze)
    maze[2, 10].set_east_wall(maze)
    maze[2, 11].set_east_wall(maze)
    maze[2, 12].set_east_wall(maze)
    maze[2, 13].set_north_wall(maze)
    maze[2, 14].set_north_wall(maze)

    # Column 3
    maze[3, 0].set_north_wall(maze)
    maze[3, 1].set_north_wall(maze)
    maze[3, 2].set_north_wall(maze)
    maze[3, 4].set_east_wall(maze)
    maze[3, 5].set_east_wall(maze)
    maze[3, 6].set_east_wall(maze)
    maze[3, 8].set_east_wall(maze)
    maze[3, 9].set_east_wall(maze)
    maze[3, 10].set_east_wall(maze)
    maze[3, 11].set_east_wall(maze)
    maze[3, 12].set_north_wall(maze)
    maze[3, 13].set_north_wall(maze)
    maze[3, 14].set_north_wall(maze)

    # Column 4
    maze[4, 1].set_north_wall(maze)
    maze[4, 2].set_north_wall(maze)
    maze[4, 3].set_north_wall(maze)
    maze[4, 4].set_north_wall(maze)
    maze[4, 5].set_east_wall(maze)
    maze[4, 6].set_east_wall(maze)
    maze[4, 8].set_east_wall(maze)
    maze[4, 9].set_east_wall(maze)
    maze[4, 10].set_east_wall(maze)
    maze[4, 11].set_north_wall(maze)
    maze[4, 12].set_north_wall(maze)
    maze[4, 13].set_north_wall(maze)
    maze[4, 14].set_north_wall(maze)

    # Column 5
    maze[5, 0].set_north_wall(maze)
    maze[5, 1].set_north_wall(maze)
    maze[5, 2].set_north_wall(maze)
    maze[5, 3].set_north_wall(maze)
    maze[5, 4].set_north_wall(maze)
    maze[5, 5].set_east_wall(maze)
    maze[5, 6].set_east_wall(maze)
    maze[5, 8].set_east_wall(maze)
    maze[5, 9].set_east_wall(maze)
    maze[5, 10].set_north_wall(maze)
    maze[5, 11].set_north_wall(maze)
    maze[5, 12].set_north_wall(maze)
    maze[5, 13].set_north_wall(maze)
    maze[5, 14].set_north_wall(maze)

    # Column 6
    maze[6, 0].set_north_wall(maze)
    maze[6, 1].set_north_wall(maze)
    maze[6, 2].set_north_wall(maze)
    maze[6, 3].set_north_wall(maze)
    maze[6, 4].set_north_wall(maze)
    maze[6, 5].set_north_wall(maze)
    maze[6, 8].set_east_wall(maze)
    maze[6, 9].set_north_wall(maze)
    maze[6, 10].set_north_wall(maze)
    maze[6, 11].set_north_wall(maze)
    maze[6, 12].set_north_wall(maze)
    maze[6, 13].set_north_wall(maze)
    maze[6, 14].set_north_wall(maze)

    # Column 7
    maze[7, 0].set_north_wall(maze)
    maze[7, 1].set_north_wall(maze)
    maze[7, 1].set_east_wall(maze)
    maze[7, 2].set_north_wall(maze)
    maze[7, 3].set_north_wall(maze)
    maze[7, 4].set_north_wall(maze)
    maze[7, 5].set_north_wall(maze)
    maze[7, 6].set_north_wall(maze)
    maze[7, 8].set_north_wall(maze)
    maze[7, 9].set_north_wall(maze)
    maze[7, 10].set_north_wall(maze)
    maze[7, 10].set_east_wall(maze)
    maze[7, 11].set_north_wall(maze)
    maze[7, 11].set_east_wall(maze)
    maze[7, 12].set_north_wall(maze)
    maze[7, 14].set_north_wall(maze)

    # Column 8
    maze[8, 0].set_north_wall(maze)
    maze[8, 2].set_north_wall(maze)
    maze[8, 4].set_north_wall(maze)
    maze[8, 6].set_north_wall(maze)
    maze[8, 7].set_east_wall(maze)
    maze[8, 8].set_east_wall(maze)
    maze[8, 8].set_north_wall(maze)
    maze[8, 9].set_north_wall(maze)
    maze[8, 10].set_north_wall(maze)
    maze[8, 11].set_north_wall(maze)
    maze[8, 12].set_north_wall(maze)
    maze[8, 13].set_north_wall(maze)
    maze[8, 14].set_north_wall(maze)

    # Column 9
    maze[9, 0].set_north_wall(maze)
    maze[9, 1].set_north_wall(maze)
    maze[9, 2].set_north_wall(maze)
    maze[9, 3].set_north_wall(maze)
    maze[9, 4].set_north_wall(maze)
    maze[9, 5].set_north_wall(maze)
    maze[9, 6].set_east_wall(maze)
    maze[9, 7].set_east_wall(maze)
    maze[9, 8].set_east_wall(maze)
    maze[9, 9].set_east_wall(maze)
    maze[9, 9].set_north_wall(maze)
    maze[9, 10].set_north_wall(maze)
    maze[9, 11].set_north_wall(maze)
    maze[9, 12].set_north_wall(maze)
    maze[9, 13].set_north_wall(maze)

    # Column 10
    maze[10, 0].set_north_wall(maze)
    maze[10, 1].set_north_wall(maze)
    maze[10, 2].set_north_wall(maze)
    maze[10, 3].set_north_wall(maze)
    maze[10, 4].set_north_wall(maze)
    maze[10, 5].set_east_wall(maze)
    maze[10, 6].set_east_wall(maze)
    maze[10, 8].set_east_wall(maze)
    maze[10, 9].set_east_wall(maze)
    maze[10, 10].set_east_wall(maze)
    maze[10, 10].set_north_wall(maze)
    maze[10, 11].set_north_wall(maze)
    maze[10, 13].set_east_wall(maze)
    maze[10, 13].set_north_wall(maze)
    maze[10, 14].set_north_wall(maze)

    # Column 11
    maze[11, 0].set_north_wall(maze)
    maze[11, 1].set_north_wall(maze)
    maze[11, 2].set_north_wall(maze)
    maze[11, 3].set_north_wall(maze)
    maze[11, 4].set_east_wall(maze)
    maze[11, 5].set_east_wall(maze)
    maze[11, 6].set_east_wall(maze)
    maze[11, 7].set_east_wall(maze)
    maze[11, 8].set_east_wall(maze)
    maze[11, 10].set_east_wall(maze)
    maze[11, 11].set_east_wall(maze)
    maze[11, 11].set_north_wall(maze)
    maze[11, 12].set_north_wall(maze)
    maze[11, 14].set_north_wall(maze)

    # Column 12
    maze[12, 0].set_north_wall(maze)
    maze[12, 1].set_north_wall(maze)
    maze[12, 2].set_north_wall(maze)
    maze[12, 2].set_east_wall(maze)
    maze[12, 3].set_east_wall(maze)
    maze[12, 4].set_east_wall(maze)
    maze[12, 5].set_east_wall(maze)
    maze[12, 6].set_east_wall(maze)
    maze[12, 7].set_east_wall(maze)
    maze[12, 8].set_east_wall(maze)
    maze[12, 9].set_east_wall(maze)
    maze[12, 10].set_east_wall(maze)
    maze[12, 11].set_east_wall(maze)
    maze[12, 11].set_north_wall(maze)
    maze[12, 12].set_east_wall(maze)
    maze[12, 12].set_north_wall(maze)
    maze[12, 13].set_north_wall(maze)

    # Column 13
    maze[13, 0].set_north_wall(maze)
    maze[13, 1].set_north_wall(maze)
    maze[13, 2].set_east_wall(maze)
    maze[13, 3].set_east_wall(maze)
    maze[13, 4].set_east_wall(maze)
    maze[13, 5].set_east_wall(maze)
    maze[13, 7].set_east_wall(maze)
    maze[13, 8].set_east_wall(maze)
    maze[13, 9].set_east_wall(maze)
    maze[13, 10].set_east_wall(maze)
    maze[13, 11].set_east_wall(maze)
    maze[13, 12].set_east_wall(maze)
    maze[13, 13].set_east_wall(maze)
    maze[13, 13].set_north_wall(maze)
    maze[13, 14].set_north_wall(maze)

    # Column 14
    maze[14, 0].set_north_wall(maze)
    maze[14, 1].set_north_wall(maze)
    maze[14, 2].set_east_wall(maze)
    maze[14, 3].set_east_wall(maze)
    maze[14, 5].set_east_wall(maze)
    maze[14, 6].set_east_wall(maze)
    maze[14, 7].set_east_wall(maze)
    maze[14, 8].set_east_wall(maze)
    maze[14, 9].set_east_wall(maze)
    maze[14, 10].set_east_wall(maze)
    maze[14, 11].set_east_wall(maze)
    maze[14, 12].set_east_wall(maze)
    maze[14, 13].set_east_wall(maze)
    maze[14, 14].set_east_wall(maze)
    maze[14, 14].set_north_wall(maze)

    maze.update_all_wall_codes()


PRESET_CONFIGURATIONS = {
    5: wall_arrangement_x5,
    6: wall_arrangement_x6,
    10: wall_arrangement_10x10,
    16: wall_arrangement_16x16,
}


def build_preset_maze(size: int) -> Maze:
    """
    Build and return a populated Maze instance for the given size
    (5, 6, 10, or 16).
    """
    if size not in PRESET_CONFIGURATIONS:
        raise ValueError(f"No preset maze configuration for size {size}. Available sizes: {list(PRESET_CONFIGURATIONS.keys())}")
    maze = create_empty_maze(size)
    PRESET_CONFIGURATIONS[size](maze)
    return maze

