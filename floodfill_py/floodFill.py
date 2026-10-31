"""
Flood-fill algorithm and Micromouse navigation solver.
"""

from collections import deque
from typing import List, Union

from cell import Cell, Maze, create_empty_maze
from mouse import Mouse
from mazes import (
    wall_arrangement_x5,
    wall_arrangement_x6,
    wall_arrangement_10x10,
    wall_arrangement_16x16,
    build_preset_maze,
)


def flood_fill(maze: Maze, goal_points: Union[Cell, List[Cell]]) -> None:
    """
    Perform BFS flood-fill from goal cell(s) through the maze, assigning
    distance values to each reachable cell.
    Exploration order is strictly North, East, South, West to preserve
    deterministic tie-breaking.
    """
    q = deque()

    if hasattr(goal_points, "__iter__"):
        for goal in goal_points:
            goal.value = 0
            q.append((goal, 0))
    else:
        goal_points.value = 0
        q.append((goal_points, 0))

    size = maze.size
    while q:
        current_cell, dist = q.popleft()
        cx, cy = current_cell.x, current_cell.y
        next_dist = dist + 1

        # Check neighbors in fixed order: North, East, South, West
        # North
        if cy + 1 < size and not current_cell.is_north_wall:
            neighbor = maze[cx, cy + 1]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # East
        if cx + 1 < size and not current_cell.is_east_wall:
            neighbor = maze[cx + 1, cy]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # South
        if cy - 1 >= 0 and not current_cell.is_south_wall:
            neighbor = maze[cx, cy - 1]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # West
        if cx - 1 >= 0 and not current_cell.is_west_wall:
            neighbor = maze[cx - 1, cy]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))


def navigate(mouse: Mouse, testing_maze: Maze, verbose: bool = True) -> List[List[int]]:
    """
    Simulate the mouse exploring testing_maze using real-time sensor updates
    and flood-fill shortest-path planning to reach the maze center.

    Parameters:
        mouse: The Mouse agent instance.
        testing_maze: The ground-truth maze with walls.
        verbose: When True, logs position and orientation steps to stdout.

    Returns:
        List of [x, y, orientation] states visited along the trajectory.
    """
    mouse.x = 0
    mouse.y = 0
    mouse.orientation = 0

    path: List[List[int]] = []
    empty_maze = create_empty_maze(testing_maze.size)
    goal_cells = empty_maze.get_centers()

    while True:
        current_cell = empty_maze[mouse.x, mouse.y]

        # Sense environment and update internal map
        mouse.update_sensors(testing_maze)
        mouse.update_maze_walls(empty_maze)

        # Flood fill from goal to determine shortest distance gradient
        empty_maze.reset_values()
        flood_fill(empty_maze, goal_cells)

        # Check if goal has been reached
        if current_cell.value == 0:
            if verbose:
                print(f"Goal reached at ({mouse.x}, {mouse.y})!")
            break

        next_cell_value = current_cell.value - 1
        accessible_neighbors = []

        # Check accessible neighbors in order: North, East, South, West
        if mouse.y + 1 < empty_maze.size and not current_cell.is_north_wall:
            accessible_neighbors.append(empty_maze[mouse.x, mouse.y + 1])

        if mouse.x + 1 < empty_maze.size and not current_cell.is_east_wall:
            accessible_neighbors.append(empty_maze[mouse.x + 1, mouse.y])

        if mouse.y - 1 >= 0 and not current_cell.is_south_wall:
            accessible_neighbors.append(empty_maze[mouse.x, mouse.y - 1])

        if mouse.x - 1 >= 0 and not current_cell.is_west_wall:
            accessible_neighbors.append(empty_maze[mouse.x - 1, mouse.y])

        # Find the neighbor along the gradient (neighbor.value == current_cell.value - 1)
        next_cell = None
        for neighbor in accessible_neighbors:
            if neighbor.value == next_cell_value:
                next_cell = neighbor
                break

        if next_cell is None:
            if verbose:
                print(f"No accessible neighbor found for cell ({mouse.x}, {mouse.y}) with value {next_cell_value}. Reapplying flood fill.")

            # Fallback if in local minimum
            empty_maze.reset_values()
            flood_fill(empty_maze, current_cell)
            accessible_neighbors.clear()

            if mouse.y + 1 < empty_maze.size and not current_cell.is_north_wall:
                accessible_neighbors.append(empty_maze[mouse.x, mouse.y + 1])
            if mouse.x + 1 < empty_maze.size and not current_cell.is_east_wall:
                accessible_neighbors.append(empty_maze[mouse.x + 1, mouse.y])
            if mouse.y - 1 >= 0 and not current_cell.is_south_wall:
                accessible_neighbors.append(empty_maze[mouse.x, mouse.y - 1])
            if mouse.x - 1 >= 0 and not current_cell.is_west_wall:
                accessible_neighbors.append(empty_maze[mouse.x - 1, mouse.y])

            for neighbor in accessible_neighbors:
                if neighbor.value == next_cell_value:
                    next_cell = neighbor
                    break

            if next_cell is None:
                raise ValueError("No accessible neighbor with the required value found after flood fill")

        mouse.update_mouse_orientation(current_cell, next_cell)
        mouse.move_forward()

        if verbose:
            print("(", mouse.x, ", ", mouse.y, ")   ", mouse.orientation)

        path.append([mouse.x, mouse.y, mouse.orientation])

    return path


def navigate_ui(mouse: Mouse, testing_maze: Maze) -> List[List[int]]:
    """Silent navigation wrapper returning the full path for UI consumption."""
    return navigate(mouse, testing_maze, verbose=False)
