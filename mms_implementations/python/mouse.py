"""
Mouse agent model for MMS Micromouse navigation and wall sensing.
Adapted from floodfill_py/mouse.py for the official MMS simulator.
"""

from typing import Optional, Tuple
from cell import Cell, Maze
import API


class Mouse:
    """
    Simulates a Micromouse robot interacting with the MMS simulator:
    tracks position (x, y), orientation (0: North, 1: East, 2: South, 3: West),
    queries MMS wall sensors, projects walls, and performs physical MMS turns/moves.
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    # Direction offsets for (dx, dy)
    DELTAS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Relative side codes (left, right, front)
    SIDES = {
        0: ('W', 'E', 'N'),
        1: ('N', 'S', 'E'),
        2: ('E', 'W', 'S'),
        3: ('S', 'N', 'W'),
    }

    # Direction to MMS wall character ('n', 'e', 's', 'w')
    DIR_CHARS = ['n', 'e', 's', 'w']

    def __init__(self, x: int = 0, y: int = 0, orientation: int = 0):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.left = ''
        self.right = ''
        self.front = ''
        self.is_on_front_sensor = False
        self.is_on_left_sensor = False
        self.is_on_right_sensor = False
        self.set_sides(orientation)

    def set_sides(self, orientation: Optional[int] = None) -> None:
        """Update relative side strings (left, right, front) based on orientation."""
        if orientation is None:
            orientation = self.orientation
        self.left, self.right, self.front = self.SIDES[orientation]

    def reset_pose(self, x: int = 0, y: int = 0, orientation: int = 0) -> None:
        """Reset mouse position and orientation to starting state."""
        self.x = x
        self.y = y
        self.orientation = orientation
        self.is_on_front_sensor = False
        self.is_on_left_sensor = False
        self.is_on_right_sensor = False
        self.set_sides(orientation)

    def update_sensors_from_mms(self) -> None:
        """Query wall presence at current position directly from the MMS simulator API."""
        self.set_sides(self.orientation)
        self.is_on_front_sensor = API.wallFront()
        self.is_on_left_sensor = API.wallLeft()
        self.is_on_right_sensor = API.wallRight()

    def update_maze_walls(self, maze: Maze) -> None:
        """
        Project current sensor readings into the internal discovered maze
        and visualize discovered walls in MMS using API.setWall().
        """
        cell = maze[self.x, self.y]
        setters = [
            cell.set_north_wall,
            cell.set_east_wall,
            cell.set_south_wall,
            cell.set_west_wall,
        ]

        front_dir = self.orientation
        left_dir = (self.orientation - 1) % 4
        right_dir = (self.orientation + 1) % 4

        if self.is_on_front_sensor:
            setters[front_dir](maze)
            API.setWall(self.x, self.y, self.DIR_CHARS[front_dir])
        if self.is_on_left_sensor:
            setters[left_dir](maze)
            API.setWall(self.x, self.y, self.DIR_CHARS[left_dir])
        if self.is_on_right_sensor:
            setters[right_dir](maze)
            API.setWall(self.x, self.y, self.DIR_CHARS[right_dir])

    def turn_towards_and_move(self, current_cell: Cell, next_cell: Cell) -> None:
        """
        Determine target orientation to next_cell, command MMS to turn accordingly,
        and issue API.moveForward() to step into next_cell.
        """
        dx = next_cell.x - current_cell.x
        dy = next_cell.y - current_cell.y

        if dx == 0 and dy == 1:
            target_orientation = self.NORTH
        elif dx == 1 and dy == 0:
            target_orientation = self.EAST
        elif dx == 0 and dy == -1:
            target_orientation = self.SOUTH
        elif dx == -1 and dy == 0:
            target_orientation = self.WEST
        else:
            raise ValueError(f"Invalid step from {current_cell} to {next_cell}")

        # Compute turn delta (0: none, 1: right, 2: turn back, 3: left)
        turn_delta = (target_orientation - self.orientation + 4) % 4

        if turn_delta == 1:
            API.turnRight()
        elif turn_delta == 2:
            API.turnRight()
            API.turnRight()
        elif turn_delta == 3:
            API.turnLeft()

        self.orientation = target_orientation
        self.set_sides(self.orientation)

        # Move forward in MMS
        API.moveForward()

        # Update internal coordinate tracking
        self.x = next_cell.x
        self.y = next_cell.y
