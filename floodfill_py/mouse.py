"""
Mouse agent model for Micromouse navigation and wall sensing.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cell import Cell, Maze


class Mouse:
    """
    Simulates a Micromouse robot with position (x, y), orientation,
    and left/front/right wall sensors.

    Orientation encoding:
    - 0: North (+y)
    - 1: East  (+x)
    - 2: South (-y)
    - 3: West  (-x)
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

    def turn_left(self, orientation: Optional[int] = None) -> None:
        """Turn mouse 90 degrees counter-clockwise."""
        if orientation is None:
            orientation = self.orientation
        self.orientation = (orientation - 1) % 4

    def turn_right(self, orientation: Optional[int] = None) -> None:
        """Turn mouse 90 degrees clockwise."""
        if orientation is None:
            orientation = self.orientation
        self.orientation = (orientation + 1) % 4

    def turn_back(self, orientation: Optional[int] = None) -> None:
        """Turn mouse 180 degrees."""
        if orientation is None:
            orientation = self.orientation
        self.orientation = (orientation + 2) % 4

    def move_forward(self) -> None:
        """Move one step forward in current orientation direction."""
        dx, dy = self.DELTAS[self.orientation]
        self.x += dx
        self.y += dy

    def update_mouse_orientation(self, current_cell: 'Cell', next_cell: 'Cell') -> None:
        """Align mouse orientation to the direction from current_cell to next_cell."""
        dx = next_cell.x - current_cell.x
        dy = next_cell.y - current_cell.y

        if dx == 0 and dy == 1:
            self.orientation = self.NORTH
        elif dx == 1 and dy == 0:
            self.orientation = self.EAST
        elif dx == 0 and dy == -1:
            self.orientation = self.SOUTH
        elif dx == -1 and dy == 0:
            self.orientation = self.WEST

    def update_sensors(self, testing_maze: 'Maze') -> None:
        """Read wall presence at the current cell from testing_maze."""
        self.set_sides(self.orientation)
        cell = testing_maze[self.x, self.y]

        # Walls ordered by direction [North, East, South, West]
        walls = [cell.is_north_wall, cell.is_east_wall, cell.is_south_wall, cell.is_west_wall]

        self.is_on_front_sensor = walls[self.orientation]
        self.is_on_left_sensor = walls[(self.orientation - 1) % 4]
        self.is_on_right_sensor = walls[(self.orientation + 1) % 4]

    def update_maze_walls(self, empty_maze: 'Maze') -> None:
        """Project current sensor readings as walls into the empty (discovered) maze."""
        cell = empty_maze[self.x, self.y]
        setters = [
            cell.set_north_wall,
            cell.set_east_wall,
            cell.set_south_wall,
            cell.set_west_wall,
        ]

        if self.is_on_front_sensor:
            setters[self.orientation](empty_maze)
        if self.is_on_left_sensor:
            setters[(self.orientation - 1) % 4](empty_maze)
        if self.is_on_right_sensor:
            setters[(self.orientation + 1) % 4](empty_maze)
