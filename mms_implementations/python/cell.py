"""
Cell and Maze data structures for Micromouse grid representation.
Adapted for the MMS (mackorone/mms) simulator.
"""

from typing import List, Optional, Tuple


class Cell:
    """
    Represents an individual grid cell in a Micromouse maze.

    Coordinates (x, y) follow Cartesian convention:
    - x: column index (0 to width-1, left to right / West to East)
    - y: row index (0 to height-1, bottom to top / South to North)

    Wall codes follow standard Micromouse convention:
    Sorted combinations of 'E', 'N', 'S', 'W' (e.g. 'EN', 'ENSW', or '' if none).
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_north_wall = False
        self.is_south_wall = False
        self.is_west_wall = False
        self.is_east_wall = False
        self.wall_code = ''
        self.value = -1

    def update_wall_code(self) -> None:
        """Update wall_code string in canonical sorted order ('E', 'N', 'S', 'W')."""
        code = []
        if self.is_east_wall:
            code.append('E')
        if self.is_north_wall:
            code.append('N')
        if self.is_south_wall:
            code.append('S')
        if self.is_west_wall:
            code.append('W')
        self.wall_code = ''.join(code)

    def set_north_wall(self, maze: Optional['Maze'] = None) -> None:
        self.is_north_wall = True
        if maze is not None:
            neighbor = maze.get_neighbor(self.x, self.y + 1)
            if neighbor is not None:
                neighbor.is_south_wall = True
                neighbor.update_wall_code()
        self.update_wall_code()

    def set_south_wall(self, maze: Optional['Maze'] = None) -> None:
        self.is_south_wall = True
        if maze is not None:
            neighbor = maze.get_neighbor(self.x, self.y - 1)
            if neighbor is not None:
                neighbor.is_north_wall = True
                neighbor.update_wall_code()
        self.update_wall_code()

    def set_west_wall(self, maze: Optional['Maze'] = None) -> None:
        self.is_west_wall = True
        if maze is not None:
            neighbor = maze.get_neighbor(self.x - 1, self.y)
            if neighbor is not None:
                neighbor.is_east_wall = True
                neighbor.update_wall_code()
        self.update_wall_code()

    def set_east_wall(self, maze: Optional['Maze'] = None) -> None:
        self.is_east_wall = True
        if maze is not None:
            neighbor = maze.get_neighbor(self.x + 1, self.y)
            if neighbor is not None:
                neighbor.is_west_wall = True
                neighbor.update_wall_code()
        self.update_wall_code()

    def has_wall(self, orientation: int) -> bool:
        """Check wall in cardinal direction (0: North, 1: East, 2: South, 3: West)."""
        if orientation == 0:
            return self.is_north_wall
        elif orientation == 1:
            return self.is_east_wall
        elif orientation == 2:
            return self.is_south_wall
        elif orientation == 3:
            return self.is_west_wall
        return True

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Cell({self.x}, {self.y}, value={self.value})"


class Maze:
    """
    Represents an arbitrary W x H Micromouse maze grid.
    Internally indexed as cells[actual_y][x] where actual_y = height - 1 - y.
    Supports index access via maze[x, y].
    """

    def __init__(self, width: int, height: Optional[int] = None):
        self.width = width
        self.height = height if height is not None else width
        self.size = self.width  # For backward-compatibility with square mazes
        self.cells = [
            [Cell(col, self.height - 1 - row) for col in range(self.width)]
            for row in range(self.height)
        ]

    def __getitem__(self, index: Tuple[int, int]) -> Cell:
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            actual_y = self.height - 1 - y
            return self.cells[actual_y][x]
        raise IndexError(f"Index ({x}, {y}) out of bounds for maze {self.width}x{self.height}")

    def __setitem__(self, index: Tuple[int, int], value: int) -> None:
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            actual_y = self.height - 1 - y
            self.cells[actual_y][x].value = value
        else:
            raise IndexError(f"Index ({x}, {y}) out of bounds for maze {self.width}x{self.height}")

    def get_neighbor(self, x: int, y: int) -> Optional[Cell]:
        """Return the cell at (x, y) if within bounds, otherwise None."""
        if 0 <= x < self.width and 0 <= y < self.height:
            actual_y = self.height - 1 - y
            return self.cells[actual_y][x]
        return None

    def get_centers(self) -> List[Cell]:
        """
        Return the center goal cell(s).
        - Odd-dimensioned maze: single center cell.
        - Even-dimensioned maze: the 2x2 cluster of 4 center cells.
        """
        mid_x = self.width // 2
        mid_y = self.height // 2

        if self.width % 2 == 1 and self.height % 2 == 1:
            return [self[mid_x, mid_y]]

        return [
            self[mid_x - 1, mid_y - 1],
            self[mid_x, mid_y - 1],
            self[mid_x - 1, mid_y],
            self[mid_x, mid_y],
        ]

    def reset_values(self) -> None:
        """Reset the flood-fill distance value of all cells to -1."""
        for row in self.cells:
            for cell in row:
                cell.value = -1

    def update_all_wall_codes(self) -> None:
        """Update the wall_code attribute of all cells."""
        for row in self.cells:
            for cell in row:
                cell.update_wall_code()


def create_empty_maze(width: int, height: Optional[int] = None) -> Maze:
    """Create a maze of given dimensions with perimeter boundary walls set."""
    maze = Maze(width, height)
    for row in maze.cells:
        for cell in row:
            if cell.x == 0:
                cell.set_west_wall(maze)
            if cell.x == maze.width - 1:
                cell.set_east_wall(maze)
            if cell.y == 0:
                cell.set_south_wall(maze)
            if cell.y == maze.height - 1:
                cell.set_north_wall(maze)
    return maze
