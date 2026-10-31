class Cell:
    """Wall code:
    0: No wall
    N: North wall
    S: South wall
    W: West wall
    E: East wall

    NS: North and South walls
    WE: West and East walls
    WN: West and North walls
    SW: South and West walls
    NE: North and East walls
    ES: East and South walls

    WNE: West, North, and East walls
    NES: North, East, and South walls
    ESW: East, South, and West walls
    SWN: South, West, and North walls
    """

    def update_wall_code(self):
        wall_set = set()
        if self.is_north_wall:
            wall_set.add('N')
        if self.is_south_wall:
            wall_set.add('S')
        if self.is_west_wall:
            wall_set.add('W')
        if self.is_east_wall:
            wall_set.add('E')
        self.wall_code = ''.join(sorted(wall_set))

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_north_wall = False
        self.is_south_wall = False
        self.is_west_wall = False
        self.is_east_wall = False
        self.wall_code = ''
        self.value = -1

    def __str__(self):
        return f"({self.x}, {self.y})"

    def get_array_index_x(self):
        return self.x

    def get_array_index_y(self, maze_length):
        return maze_length - 1 - self.y

    def set_north_wall(self, maze):
        self.is_north_wall = True
        neighbor = maze.get_neighbor(self.x, self.y + 1)
        if neighbor:
            neighbor.is_south_wall = True
        self.update_wall_code()

    def set_south_wall(self, maze):
        self.is_south_wall = True
        neighbor = maze.get_neighbor(self.x, self.y - 1)
        if neighbor:
            neighbor.is_north_wall = True
        self.update_wall_code()

    def set_west_wall(self, maze):
        self.is_west_wall = True
        neighbor = maze.get_neighbor(self.x - 1, self.y)
        if neighbor:
            neighbor.is_east_wall = True
        self.update_wall_code()

    def set_east_wall(self, maze):
        self.is_east_wall = True
        neighbor = maze.get_neighbor(self.x + 1, self.y)
        if neighbor:
            neighbor.is_west_wall = True
        self.update_wall_code()


    # def __eq__(self, other):
    #     if isinstance(other, Cell):
    #         return self.x == other.x and self.y == other.y
    #     return False
    #
    # def __hash__(self):
    #     return hash((self.x, self.y))
    #
    def __repr__(self):
        return f"Cell({self.x}, {self.y}, value={self.value})"


class Maze:
    def __init__(self, size):
        self.size = size
        self.cells = [[Cell(col, self.size - 1 - row) for col in range(size)] for row in range(size)]

    def __getitem__(self, index):
        x, y = index
        if 0 <= x < self.size and 0 <= y < self.size:
            actual_y = self.size - 1 - y
            return self.cells[actual_y][x]
        raise IndexError("Index out of bounds")

    def __setitem__(self, index, value):
        x, y = index
        actual_y = self.size - 1 - y
        self.cells[actual_y][x].value = value

    def __repr__(self):
        return '\n'.join([' '.join([str(cell.value) for cell in row]) for row in self.cells])

    def get_neighbor(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self[x, y]
        return None

    def get_centers(self):
        max_size = self.size
        if max_size % 2 == 1:
            center_x = max_size // 2
            center_y = max_size // 2
            center = self[center_x, center_y]
            centers = [center]
            return centers
        else:
            center0 = self[max_size // 2 - 1, max_size // 2 - 1]
            center1 = self[max_size // 2, max_size // 2 - 1]
            center2 = self[max_size // 2 - 1, max_size // 2]
            center3 = self[max_size // 2, max_size // 2]
            centers = [center0, center1, center2, center3]
        return centers

    def reset_values(self):
        for row in self.cells:
            for cell in row:
                cell.value = -1

    def update_all_wall_codes(self):
        for row in self.cells:
            for cell in row:
                cell.update_wall_code()
