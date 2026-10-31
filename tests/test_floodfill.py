"""
Automated unit and regression tests for Micromouse flood-fill implementation.
Verifies functional equivalence against the golden baseline across all maze sizes.
"""

import os
import sys
import unittest

# Add floodfill_py directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "floodfill_py"))

from cell import Cell, Maze, create_empty_maze
from mouse import Mouse
from floodFill import flood_fill, navigate, navigate_ui
from mazes import (
    wall_arrangement_x5,
    wall_arrangement_x6,
    wall_arrangement_10x10,
    wall_arrangement_16x16,
    build_preset_maze,
)


class TestCellAndMaze(unittest.TestCase):
    def test_cell_initialization(self):
        c = Cell(2, 3)
        self.assertEqual(c.x, 2)
        self.assertEqual(c.y, 3)
        self.assertEqual(c.value, -1)
        self.assertFalse(c.is_north_wall)
        self.assertFalse(c.is_south_wall)
        self.assertFalse(c.is_east_wall)
        self.assertFalse(c.is_west_wall)
        self.assertEqual(c.wall_code, '')

    def test_reciprocal_walls(self):
        maze = Maze(5)
        maze[1, 1].set_north_wall(maze)
        self.assertTrue(maze[1, 1].is_north_wall)
        self.assertTrue(maze[1, 2].is_south_wall)
        self.assertIn('N', maze[1, 1].wall_code)
        self.assertIn('S', maze[1, 2].wall_code)

        maze[1, 1].set_east_wall(maze)
        self.assertTrue(maze[1, 1].is_east_wall)
        self.assertTrue(maze[2, 1].is_west_wall)

    def test_maze_indexing(self):
        maze = Maze(6)
        c = maze[0, 0]
        self.assertEqual((c.x, c.y), (0, 0))
        c_top = maze[5, 5]
        self.assertEqual((c_top.x, c_top.y), (5, 5))
        with self.assertRaises(IndexError):
            _ = maze[6, 0]

    def test_maze_centers(self):
        maze_odd = Maze(5)
        centers_odd = maze_odd.get_centers()
        self.assertEqual(len(centers_odd), 1)
        self.assertEqual((centers_odd[0].x, centers_odd[0].y), (2, 2))

        maze_even = Maze(6)
        centers_even = maze_even.get_centers()
        self.assertEqual(len(centers_even), 4)
        center_coords = {(c.x, c.y) for c in centers_even}
        self.assertEqual(center_coords, {(2, 2), (3, 2), (2, 3), (3, 3)})

    def test_create_empty_maze_boundaries(self):
        m = create_empty_maze(5)
        # Check corners have proper outer walls
        self.assertTrue(m[0, 0].is_west_wall)
        self.assertTrue(m[0, 0].is_south_wall)
        self.assertTrue(m[4, 4].is_east_wall)
        self.assertTrue(m[4, 4].is_north_wall)


class TestMouse(unittest.TestCase):
    def test_mouse_rotations(self):
        mouse = Mouse()
        self.assertEqual(mouse.orientation, Mouse.NORTH)

        mouse.turn_right()
        self.assertEqual(mouse.orientation, Mouse.EAST)

        mouse.turn_right()
        self.assertEqual(mouse.orientation, Mouse.SOUTH)

        mouse.turn_right()
        self.assertEqual(mouse.orientation, Mouse.WEST)

        mouse.turn_right()
        self.assertEqual(mouse.orientation, Mouse.NORTH)

        mouse.turn_left()
        self.assertEqual(mouse.orientation, Mouse.WEST)

        mouse.turn_back()
        self.assertEqual(mouse.orientation, Mouse.EAST)

    def test_mouse_movement(self):
        mouse = Mouse(0, 0, Mouse.NORTH)
        mouse.move_forward()
        self.assertEqual((mouse.x, mouse.y), (0, 1))

        mouse.orientation = Mouse.EAST
        mouse.move_forward()
        self.assertEqual((mouse.x, mouse.y), (1, 1))

        mouse.orientation = Mouse.SOUTH
        mouse.move_forward()
        self.assertEqual((mouse.x, mouse.y), (1, 0))

        mouse.orientation = Mouse.WEST
        mouse.move_forward()
        self.assertEqual((mouse.x, mouse.y), (0, 0))

    def test_mouse_sensing_and_mapping(self):
        testing_maze = create_empty_maze(4)
        testing_maze[0, 0].set_north_wall(testing_maze)

        mouse = Mouse(0, 0, Mouse.NORTH)
        mouse.update_sensors(testing_maze)
        self.assertTrue(mouse.is_on_front_sensor)  # North wall is front
        self.assertTrue(mouse.is_on_left_sensor)   # West boundary is left
        self.assertFalse(mouse.is_on_right_sensor) # East has no wall

        empty_maze = create_empty_maze(4)
        mouse.update_maze_walls(empty_maze)
        self.assertTrue(empty_maze[0, 0].is_north_wall)
        self.assertTrue(empty_maze[0, 1].is_south_wall)


class TestFloodFillRegression(unittest.TestCase):
    """
    Verify exact flood-fill distances and navigation paths against golden values.
    """

    def test_5x5_maze(self):
        maze = build_preset_maze(5)
        centers = maze.get_centers()
        flood_fill(maze, centers)

        # Distance from (0, 0) to center (2, 2)
        self.assertEqual(maze[0, 0].value, 6)
        self.assertEqual(maze[2, 2].value, 0)

        path = navigate_ui(Mouse(), build_preset_maze(5))
        expected_path = [
            [0, 1, 0],
            [1, 1, 1],
            [1, 2, 0],
            [1, 3, 0],
            [2, 3, 1],
            [2, 2, 2],
        ]
        self.assertEqual(path, expected_path)

    def test_6x6_maze(self):
        maze = build_preset_maze(6)
        centers = maze.get_centers()
        flood_fill(maze, centers)

        self.assertEqual(maze[0, 0].value, 8)
        for c in centers:
            self.assertEqual(c.value, 0)

        path = navigate_ui(Mouse(), build_preset_maze(6))
        self.assertEqual(len(path), 18)
        self.assertEqual(path[-1], [3, 3, 2])
        self.assertEqual(path[0], [0, 1, 0])

    def test_10x10_maze(self):
        maze = build_preset_maze(10)
        centers = maze.get_centers()
        flood_fill(maze, centers)

        self.assertEqual(maze[0, 0].value, 8)
        for c in centers:
            self.assertEqual(c.value, 0)

        path = navigate_ui(Mouse(), build_preset_maze(10))
        expected_path = [
            [0, 1, 0],
            [0, 2, 0],
            [0, 3, 0],
            [1, 3, 1],
            [1, 4, 0],
            [1, 5, 0],
            [2, 5, 1],
            [2, 4, 2],
            [3, 4, 1],
            [4, 4, 1],
        ]
        self.assertEqual(path, expected_path)

    def test_16x16_maze(self):
        maze = build_preset_maze(16)
        centers = maze.get_centers()
        flood_fill(maze, centers)

        self.assertEqual(maze[0, 0].value, 44)
        for c in centers:
            self.assertEqual(c.value, 0)

        path = navigate_ui(Mouse(), build_preset_maze(16))
        self.assertEqual(len(path), 100)
        self.assertEqual(path[0], [0, 1, 0])
        self.assertEqual(path[-1], [7, 7, 1])


if __name__ == "__main__":
    unittest.main()

