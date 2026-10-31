"""
Cell and Maze data structures for Micromouse grid representation.
"""

from typing import List, Optional, Tuple


class Cell:
    """
    Represents an individual grid cell in a Micromouse maze.

    Coordinates (x, y) follow Cartesian convention:
    - x: column index (0 to size-1, left to right)
    - y: row index (0 to size-1, bottom to top)

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

    def get_array_index_x(self) -> int:
        return self.x

    def get_array_index_y(self, maze_length: int) -> int:
        return maze_length - 1 - self.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Cell({self.x}, {self.y}, value={self.value})"


class Maze:
    """
    Represents an N x N Micromouse maze grid.
    Internally indexed as cells[actual_y][x] where actual_y = size - 1 - y.
    Supports index access via maze[x, y].
    """

    def __init__(self, size: int):
        self.size = size
        self.cells = [
            [Cell(col, self.size - 1 - row) for col in range(size)]
            for row in range(size)
        ]

    def __getitem__(self, index: Tuple[int, int]) -> Cell:
        x, y = index
        if 0 <= x < self.size and 0 <= y < self.size:
            actual_y = self.size - 1 - y
            return self.cells[actual_y][x]
        raise IndexError(f"Index ({x}, {y}) out of bounds for maze of size {self.size}")

    def __setitem__(self, index: Tuple[int, int], value: int) -> None:
        x, y = index
        if 0 <= x < self.size and 0 <= y < self.size:
            actual_y = self.size - 1 - y
            self.cells[actual_y][x].value = value
        else:
            raise IndexError(f"Index ({x}, {y}) out of bounds for maze of size {self.size}")

    def __repr__(self) -> str:
        return '\n'.join(' '.join(str(cell.value) for cell in row) for row in self.cells)

    def get_neighbor(self, x: int, y: int) -> Optional[Cell]:
        """Return the cell at (x, y) if within bounds, otherwise None."""
        if 0 <= x < self.size and 0 <= y < self.size:
            actual_y = self.size - 1 - y
            return self.cells[actual_y][x]
        return None

    def get_centers(self) -> List[Cell]:
        """
        Return the center goal cell(s).
        - Odd-dimensioned maze: single center cell.
        - Even-dimensioned maze: the 2x2 cluster of 4 center cells.
        """
        mid = self.size // 2
        if self.size % 2 == 1:
            return [self[mid, mid]]
        return [
            self[mid - 1, mid - 1],
            self[mid, mid - 1],
            self[mid - 1, mid],
            self[mid, mid],
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


def create_empty_maze(length: int) -> Maze:
    """Create a maze of given length with perimeter boundary walls set."""
    maze = Maze(length)
    for row in maze.cells:
        for cell in row:
            if cell.x == 0:
                cell.set_west_wall(maze)
            if cell.x == length - 1:
                cell.set_east_wall(maze)
            if cell.y == 0:
                cell.set_south_wall(maze)
            if cell.y == length - 1:
                cell.set_north_wall(maze)
    return maze
