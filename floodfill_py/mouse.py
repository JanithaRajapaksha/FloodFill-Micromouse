class Mouse:
    x, y = 0, 0
    orientation = 0
    left, right, front = '', '', ''

    is_on_front_sensor = False
    is_on_left_sensor = False
    is_on_right_sensor = False

    def set_sides(self, orientation):
        if orientation == 0:
            self.left = 'W'
            self.right = 'E'
            self.front = 'N'
        elif orientation == 2:
            self.left = 'E'
            self.right = 'W'
            self.front = 'S'
        elif orientation == 3:
            self.left = 'S'
            self.right = 'N'
            self.front = 'W'
        elif orientation == 1:
            self.left = 'N'
            self.right = 'S'
            self.front = 'E'

    def turn_left(self, orientation):
        if orientation == 0:
            self.orientation = 3
        else:
            self.orientation -= 1

    def turn_right(self, orientation):
        if orientation == 3:
            self.orientation = 0
        else:
            self.orientation += 1

    def turn_back(self, orientation):
        self.turn_right(orientation)
        self.turn_right(orientation)

    def move_forward(self):

            if self.orientation == 0:
                self.y += 1
            elif self.orientation == 1:
                self.x += 1
            elif self.orientation == 2:
                self.y -= 1
            elif self.orientation == 3:
                self.x -= 1

    def update_mouse_orientation(self, current_cell, next_cell):
        dx = next_cell.x - current_cell.x
        dy = next_cell.y - current_cell.y

        if dx == 0 and dy == 1:  # Moving North
            self.orientation = 0
        elif dx == 1 and dy == 0:  # Moving East
            self.orientation = 1
        elif dx == 0 and dy == -1:  # Moving South
            self.orientation = 2
        elif dx == -1 and dy == 0:  # Moving West
            self.orientation = 3

    def update_sensors(self, testing_maze):
        self.set_sides(self.orientation)

        if self.orientation == 0:
            self.is_on_front_sensor = testing_maze[self.x, self.y].is_north_wall
            self.is_on_left_sensor = testing_maze[self.x, self.y].is_west_wall
            self.is_on_right_sensor = testing_maze[self.x, self.y].is_east_wall
        elif self.orientation == 1:
            self.is_on_front_sensor = testing_maze[self.x, self.y].is_east_wall
            self.is_on_left_sensor = testing_maze[self.x, self.y].is_north_wall
            self.is_on_right_sensor = testing_maze[self.x, self.y].is_south_wall
        elif self.orientation == 2:
            self.is_on_front_sensor = testing_maze[self.x, self.y].is_south_wall
            self.is_on_left_sensor = testing_maze[self.x, self.y].is_east_wall
            self.is_on_right_sensor = testing_maze[self.x, self.y].is_west_wall
        elif self.orientation == 3:
            self.is_on_front_sensor = testing_maze[self.x, self.y].is_west_wall
            self.is_on_left_sensor = testing_maze[self.x, self.y].is_south_wall
            self.is_on_right_sensor = testing_maze[self.x, self.y].is_north_wall

    def update_maze_walls(self, empty_maze):
        if self.orientation == 0:
            if self.is_on_front_sensor:
                empty_maze[self.x, self.y].set_north_wall(empty_maze)
            if self.is_on_left_sensor:
                empty_maze[self.x, self.y].set_west_wall(empty_maze)
            if self.is_on_right_sensor:
                empty_maze[self.x, self.y].set_east_wall(empty_maze)
        elif self.orientation == 1:
            if self.is_on_front_sensor:
                empty_maze[self.x, self.y].set_east_wall(empty_maze)
            if self.is_on_left_sensor:
                empty_maze[self.x, self.y].set_north_wall(empty_maze)
            if self.is_on_right_sensor:
                empty_maze[self.x, self.y].set_south_wall(empty_maze)
        elif self.orientation == 2:
            if self.is_on_front_sensor:
                empty_maze[self.x, self.y].set_south_wall(empty_maze)
            if self.is_on_left_sensor:
                empty_maze[self.x, self.y].set_east_wall(empty_maze)
            if self.is_on_right_sensor:
                empty_maze[self.x, self.y].set_west_wall(empty_maze)
        elif self.orientation == 3:
            if self.is_on_front_sensor:
                empty_maze[self.x, self.y].set_west_wall(empty_maze)
            if self.is_on_left_sensor:
                empty_maze[self.x, self.y].set_south_wall(empty_maze)
            if self.is_on_right_sensor:
                empty_maze[self.x, self.y].set_north_wall(empty_maze)


