"""
Flood-fill algorithm and Micromouse navigation solver for MMS.
Adapted from floodfill_py/floodFill.py.
"""

from collections import deque
from typing import List, Optional, Union
import sys

from cell import Cell, Maze
from mouse import Mouse
import API


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

    width = maze.width
    height = maze.height

    while q:
        current_cell, dist = q.popleft()
        cx, cy = current_cell.x, current_cell.y
        next_dist = dist + 1

        # Check neighbors in fixed order: North, East, South, West
        # 1. North (+y)
        if cy + 1 < height and not current_cell.is_north_wall:
            neighbor = maze[cx, cy + 1]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # 2. East (+x)
        if cx + 1 < width and not current_cell.is_east_wall:
            neighbor = maze[cx + 1, cy]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # 3. South (-y)
        if cy - 1 >= 0 and not current_cell.is_south_wall:
            neighbor = maze[cx, cy - 1]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))

        # 4. West (-x)
        if cx - 1 >= 0 and not current_cell.is_west_wall:
            neighbor = maze[cx - 1, cy]
            if neighbor.value == -1:
                neighbor.value = next_dist
                q.append((neighbor, next_dist))


def explore_step_mms(mouse: Mouse, maze: Maze, goal_cells: List[Cell]) -> str:
    """
    Execute a single blind exploration step in the MMS simulator:
    1. Sense walls around current cell.
    2. Update internal discovered maze and MMS wall graphics.
    3. Run flood fill from destination centers.
    4. Update cell visualization.
    5. Check goal condition.
    6. Choose next cell and actuate turn + moveForward.

    Returns:
        'GOAL_REACHED' if current cell is destination,
        'STEP_OK' if step succeeded,
        'NO_PATH' if robot cannot find reachable path.
    """
    current_cell = maze[mouse.x, mouse.y]

    # 1. Sense environment and update internal discovered map
    mouse.update_sensors_from_mms()
    mouse.update_maze_walls(maze)

    # 2. Mark visited cell trail in MMS
    API.setColor(mouse.x, mouse.y, 'a')

    # 3. Highlight destination goal cells
    for g in goal_cells:
        API.setColor(g.x, g.y, 'G')

    # 4. Compute flood fill from center goals
    maze.reset_values()
    flood_fill(maze, goal_cells)

    # Display current flood fill distance in MMS cell
    if current_cell.value >= 0:
        API.setText(mouse.x, mouse.y, str(current_cell.value))

    # 5. Check if goal has been reached
    if current_cell.value == 0:
        API.setColor(mouse.x, mouse.y, 'g')
        return 'GOAL_REACHED'

    next_cell_value = current_cell.value - 1
    accessible_neighbors = []

    # Check accessible neighbors in order: North, East, South, West
    if mouse.y + 1 < maze.height and not current_cell.is_north_wall:
        accessible_neighbors.append(maze[mouse.x, mouse.y + 1])

    if mouse.x + 1 < maze.width and not current_cell.is_east_wall:
        accessible_neighbors.append(maze[mouse.x + 1, mouse.y])

    if mouse.y - 1 >= 0 and not current_cell.is_south_wall:
        accessible_neighbors.append(maze[mouse.x, mouse.y - 1])

    if mouse.x - 1 >= 0 and not current_cell.is_west_wall:
        accessible_neighbors.append(maze[mouse.x - 1, mouse.y])

    # Find the neighbor along the gradient (neighbor.value == current_cell.value - 1)
    next_cell = None
    for neighbor in accessible_neighbors:
        if neighbor.value == next_cell_value:
            next_cell = neighbor
            break

    if next_cell is None:
        sys.stderr.write(
            f"[WARN] Local minimum at ({mouse.x}, {mouse.y}) with value {next_cell_value}. Reapplying fallback.\n"
        )
        sys.stderr.flush()

        # Fallback if in local minimum: flood fill from current cell
        maze.reset_values()
        flood_fill(maze, current_cell)
        accessible_neighbors.clear()

        if mouse.y + 1 < maze.height and not current_cell.is_north_wall:
            accessible_neighbors.append(maze[mouse.x, mouse.y + 1])
        if mouse.x + 1 < maze.width and not current_cell.is_east_wall:
            accessible_neighbors.append(maze[mouse.x + 1, mouse.y])
        if mouse.y - 1 >= 0 and not current_cell.is_south_wall:
            accessible_neighbors.append(maze[mouse.x, mouse.y - 1])
        if mouse.x - 1 >= 0 and not current_cell.is_west_wall:
            accessible_neighbors.append(maze[mouse.x - 1, mouse.y])

        for neighbor in accessible_neighbors:
            if neighbor.value == next_cell_value:
                next_cell = neighbor
                break

        if next_cell is None:
            return 'NO_PATH'

    dir_names = ["NORTH", "EAST", "SOUTH", "WEST"]
    sys.stderr.write(
        f"[STEP] Pos: ({mouse.x:2d}, {mouse.y:2d}) {dir_names[mouse.orientation]:<5s} | "
        f"Dist: {current_cell.value:2d} | "
        f"Walls: [F:{'YES' if mouse.is_on_front_sensor else 'no '} "
        f"L:{'YES' if mouse.is_on_left_sensor else 'no '} "
        f"R:{'YES' if mouse.is_on_right_sensor else 'no '}] -> "
        f"Target: ({next_cell.x:2d}, {next_cell.y:2d})\n"
    )
    sys.stderr.flush()

    # Turn and step forward in MMS
    mouse.turn_towards_and_move(current_cell, next_cell)
    return 'STEP_OK'
