import cell
from cell import Cell, Maze
from mouse import Mouse
from queue import Queue


def flood_fill(maze, goal_points: list):
    q = Queue()

    # Initialize the queue with goal points
    if hasattr(goal_points, "__iter__"):  # Check if iterable
        for goal in goal_points:
            q.put((goal, 0))
            goal.value = 0
    else:
        # goal_points is the single goal element
        q.put((goal_points, 0))
        goal_points.value = 0

    while not q.empty():
        current_cell, dist = q.get()
        neighbor_cells = []

        # Add neighbors with boundary checks and conditions
        if current_cell.y + 1 < maze.size:
            north_neighbor = maze[current_cell.x, current_cell.y + 1]
            if north_neighbor and not current_cell.is_north_wall and north_neighbor.value == -1:
                neighbor_cells.append(north_neighbor)

        if current_cell.x + 1 < maze.size:
            east_neighbor = maze[current_cell.x + 1, current_cell.y]
            if east_neighbor and not current_cell.is_east_wall and east_neighbor.value == -1:
                neighbor_cells.append(east_neighbor)

        if current_cell.y - 1 >= 0:
            south_neighbor = maze[current_cell.x, current_cell.y - 1]
            if south_neighbor and not current_cell.is_south_wall and south_neighbor.value == -1:
                neighbor_cells.append(south_neighbor)

        if current_cell.x - 1 >= 0:
            west_neighbor = maze[current_cell.x - 1, current_cell.y]
            if west_neighbor and not current_cell.is_west_wall and west_neighbor.value == -1:
                neighbor_cells.append(west_neighbor)

        for neighbor in neighbor_cells:
            neighbor.value = dist + 1
            q.put((neighbor, dist + 1))
        # print(f"Cell ({current_cell.x}, {current_cell.y}) set to {dist}, neighbors updated.")


def wall_arrangement_x5(maze: Maze):
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


def wall_arrangement_x6(maze: Maze):
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


def wall_arrangement_10x10(maze: Maze):
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

    # Update all wall codes at the end
    maze.update_all_wall_codes()


def wall_arrangement_16x16(maze: Maze):
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

    # Update all wall codes at the end
    maze.update_all_wall_codes()

def create_empty_maze(length):
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


def navigate(mouse: Mouse, testing_maze: Maze):
    starting_x = 0
    starting_y = 0
    mouse.x = starting_x
    mouse.y = starting_y
    mouse.orientation = 0

    empty_maze = create_empty_maze(testing_maze.size)

    # Define goal cells
    goal_cells = empty_maze.get_centers()

    flood_fill(empty_maze, goal_cells)

    while (mouse.x, mouse.y) not in goal_cells:

        current_cell = empty_maze[mouse.x, mouse.y]

        mouse.update_sensors(testing_maze)

        # Update the empty maze walls based on sensor readings
        mouse.update_maze_walls(empty_maze)
        empty_maze.reset_values()
        flood_fill(empty_maze, goal_cells)

        next_cell_value = current_cell.value - 1
        accessible_neighbors = []

        # Check north neighbor
        if mouse.y + 1 < empty_maze.size:
            north_neighbor = empty_maze[mouse.x, mouse.y + 1]
            if north_neighbor and not current_cell.is_north_wall:
                accessible_neighbors.append(north_neighbor)

        # Check east neighbor
        if mouse.x + 1 < empty_maze.size:
            east_neighbor = empty_maze[mouse.x + 1, mouse.y]
            if east_neighbor and not current_cell.is_east_wall:
                accessible_neighbors.append(east_neighbor)

        # Check south neighbor
        if mouse.y - 1 >= 0:
            south_neighbor = empty_maze[mouse.x, mouse.y - 1]
            if south_neighbor and not current_cell.is_south_wall:
                accessible_neighbors.append(south_neighbor)

        # Check west neighbor
        if mouse.x - 1 >= 0:
            west_neighbor = empty_maze[mouse.x - 1, mouse.y]
            if west_neighbor and not current_cell.is_west_wall:
                accessible_neighbors.append(west_neighbor)

        # Find the neighbor with the desired value
        next_cell = None
        for neighbor in accessible_neighbors:
            if neighbor.value == next_cell_value:
                next_cell = neighbor
                break

        if next_cell is None:
            print(f"No accessible neighbor found for cell ({mouse.x}, {mouse.y}) with value {next_cell_value}. Reapplying flood fill.")
            if current_cell.value == 0:
                empty_maze.reset_values()
                flood_fill(empty_maze, current_cell)
                # print(empty_maze)
                # print("____________________")

                print("(", mouse.x, ", ", mouse.y, ")   ", mouse.orientation)
                # print("____________________")
                break
            empty_maze.reset_values()
            flood_fill(empty_maze, current_cell)
            accessible_neighbors.clear()

            # Re-check neighbors after flood fill
            if mouse.y + 1 < empty_maze.size:
                north_neighbor = empty_maze[mouse.x, mouse.y + 1]
                if north_neighbor and not current_cell.is_north_wall:
                    accessible_neighbors.append(north_neighbor)

            if mouse.x + 1 < empty_maze.size:
                east_neighbor = empty_maze[mouse.x + 1, mouse.y]
                if east_neighbor and not current_cell.is_east_wall:
                    accessible_neighbors.append(east_neighbor)

            if mouse.y - 1 >= 0:
                south_neighbor = empty_maze[mouse.x, mouse.y - 1]
                if south_neighbor and not current_cell.is_south_wall:
                    accessible_neighbors.append(south_neighbor)

            if mouse.x - 1 >= 0:
                west_neighbor = empty_maze[mouse.x - 1, mouse.y]
                if west_neighbor and not current_cell.is_west_wall:
                    accessible_neighbors.append(west_neighbor)

            for neighbor in accessible_neighbors:
                if neighbor.value == next_cell_value:
                    next_cell = neighbor
                    break

            if next_cell is None:
                raise ValueError("No accessible neighbor with the required value found after flood fill")

        mouse.update_mouse_orientation(current_cell, next_cell)
        mouse.update_sensors(testing_maze)
        empty_maze.reset_values()

        current_cell = next_cell
        empty_maze.reset_values()

        flood_fill(empty_maze, goal_cells)
        mouse.move_forward()
        # print(empty_maze)
        # print("____________________")

        print("(", mouse.x, ", ", mouse.y, ")   ", mouse.orientation)
        # print("____________________")


def navigate_ui(mouse: Mouse, testing_maze: Maze):
    path = []
    position_and_orientation = []
    starting_x = 0
    starting_y = 0
    mouse.x = starting_x
    mouse.y = starting_y
    mouse.orientation = 0

    empty_maze = create_empty_maze(testing_maze.size)

    # Define goal cells
    goal_cells = empty_maze.get_centers()

    flood_fill(empty_maze, goal_cells)

    while (mouse.x, mouse.y) not in goal_cells:

        current_cell = empty_maze[mouse.x, mouse.y]

        mouse.update_sensors(testing_maze)

        # Update the empty maze walls based on sensor readings
        mouse.update_maze_walls(empty_maze)
        empty_maze.reset_values()
        flood_fill(empty_maze, goal_cells)

        next_cell_value = current_cell.value - 1
        accessible_neighbors = []

        # Check north neighbor
        if mouse.y + 1 < empty_maze.size:
            north_neighbor = empty_maze[mouse.x, mouse.y + 1]
            if north_neighbor and not current_cell.is_north_wall:
                accessible_neighbors.append(north_neighbor)

        # Check east neighbor
        if mouse.x + 1 < empty_maze.size:
            east_neighbor = empty_maze[mouse.x + 1, mouse.y]
            if east_neighbor and not current_cell.is_east_wall:
                accessible_neighbors.append(east_neighbor)

        # Check south neighbor
        if mouse.y - 1 >= 0:
            south_neighbor = empty_maze[mouse.x, mouse.y - 1]
            if south_neighbor and not current_cell.is_south_wall:
                accessible_neighbors.append(south_neighbor)

        # Check west neighbor
        if mouse.x - 1 >= 0:
            west_neighbor = empty_maze[mouse.x - 1, mouse.y]
            if west_neighbor and not current_cell.is_west_wall:
                accessible_neighbors.append(west_neighbor)

        # Find the neighbor with the desired value
        next_cell = None
        for neighbor in accessible_neighbors:
            if neighbor.value == next_cell_value:
                next_cell = neighbor
                break

        if next_cell is None:
            # print(f"No accessible neighbor found for cell ({mouse.x}, {mouse.y}) with value {next_cell_value}. Reapplying flood fill.")
            return path

            if current_cell.value == 0:
                empty_maze.reset_values()
                flood_fill(empty_maze, current_cell)
                # print(empty_maze)
                # print("____________________")

                print("(", mouse.x, ", ", mouse.y, ")   ", mouse.orientation)
                # print("____________________")
                break
            empty_maze.reset_values()
            flood_fill(empty_maze, current_cell)
            accessible_neighbors.clear()

            # Re-check neighbors after flood fill
            if mouse.y + 1 < empty_maze.size:
                north_neighbor = empty_maze[mouse.x, mouse.y + 1]
                if north_neighbor and not current_cell.is_north_wall:
                    accessible_neighbors.append(north_neighbor)

            if mouse.x + 1 < empty_maze.size:
                east_neighbor = empty_maze[mouse.x + 1, mouse.y]
                if east_neighbor and not current_cell.is_east_wall:
                    accessible_neighbors.append(east_neighbor)

            if mouse.y - 1 >= 0:
                south_neighbor = empty_maze[mouse.x, mouse.y - 1]
                if south_neighbor and not current_cell.is_south_wall:
                    accessible_neighbors.append(south_neighbor)

            if mouse.x - 1 >= 0:
                west_neighbor = empty_maze[mouse.x - 1, mouse.y]
                if west_neighbor and not current_cell.is_west_wall:
                    accessible_neighbors.append(west_neighbor)

            for neighbor in accessible_neighbors:
                if neighbor.value == next_cell_value:
                    next_cell = neighbor
                    break

            if next_cell is None:
                raise ValueError("No accessible neighbor with the required value found after flood fill")

        mouse.update_mouse_orientation(current_cell, next_cell)
        mouse.update_sensors(testing_maze)
        empty_maze.reset_values()

        current_cell = next_cell
        empty_maze.reset_values()

        flood_fill(empty_maze, goal_cells)
        mouse.move_forward()
        # print(empty_maze)
        # print("____________________")

        # print("(", mouse.x, ", ", mouse.y, ")   ", mouse.orientation)
        position_and_orientation = [mouse.x, mouse.y, mouse.orientation]
        path.append(position_and_orientation)

        # print("____________________")
