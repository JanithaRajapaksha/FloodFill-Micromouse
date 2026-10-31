from cell import Cell, Maze
from mouse import Mouse

from floodFill import create_empty_maze, wall_arrangement_x5, wall_arrangement_x6, wall_arrangement_10x10, flood_fill, navigate, navigate_ui

MAX_LENGTH = 10


maze1 = create_empty_maze(MAX_LENGTH)
wall_arrangement_10x10(maze1)
centers = maze1.get_centers()
flood_fill(maze1, centers)

mouse = Mouse()
maze = maze1

navigate(mouse, maze)
# print(navigate_ui(mouse, maze))
