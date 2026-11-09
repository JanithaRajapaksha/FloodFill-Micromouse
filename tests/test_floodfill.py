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

    def test_mms_example_mazes(self):
        for name in ["example1", "example2", "example3", "example4", "example5", "blank"]:
            maze = build_preset_maze(name)
            self.assertEqual(maze.size, 16)
            centers = maze.get_centers()
            self.assertEqual(len(centers), 4)
            path = navigate_ui(Mouse(), build_preset_maze(name))
            self.assertGreater(len(path), 0)
            final_cell = maze[path[-1][0], path[-1][1]]
            self.assertIn(final_cell, centers)

    def test_compact_binary_mazes(self):
        from mazes import load_bin_maze, save_bin_maze
        mazes_dir = os.path.join(os.path.dirname(__file__), "..", "mazes", "bin", "mms_mazes")
        for name in ["example1", "example2", "example3", "example4", "example5", "blank"]:
            bin_path = os.path.join(mazes_dir, f"{name}.bin")
            self.assertTrue(os.path.exists(bin_path))
            bin_maze = load_bin_maze(bin_path)
            preset_maze = build_preset_maze(name)
            self.assertEqual(bin_maze.size, preset_maze.size)
            for y in range(preset_maze.size):
                for x in range(preset_maze.size):
                    self.assertEqual(bin_maze[x, y].is_north_wall, preset_maze[x, y].is_north_wall)
                    self.assertEqual(bin_maze[x, y].is_south_wall, preset_maze[x, y].is_south_wall)
                    self.assertEqual(bin_maze[x, y].is_east_wall, preset_maze[x, y].is_east_wall)
                    self.assertEqual(bin_maze[x, y].is_west_wall, preset_maze[x, y].is_west_wall)

        # Roundtrip save & load test
        tmp_bin = "test_roundtrip.bin"
        try:
            m = build_preset_maze("example4")
            save_bin_maze(m, tmp_bin)
            reloaded = load_bin_maze(tmp_bin)
            self.assertEqual(reloaded.size, m.size)
            for y in range(m.size):
                for x in range(m.size):
                    self.assertEqual(reloaded[x, y].is_north_wall, m[x, y].is_north_wall)
                    self.assertEqual(reloaded[x, y].is_south_wall, m[x, y].is_south_wall)
                    self.assertEqual(reloaded[x, y].is_east_wall, m[x, y].is_east_wall)
                    self.assertEqual(reloaded[x, y].is_west_wall, m[x, y].is_west_wall)
        finally:
            if os.path.exists(tmp_bin):
                os.remove(tmp_bin)

    def test_japan_ntf_archive_mazes(self):
        bin_dir = os.path.join(os.path.dirname(__file__), "..", "mazes", "bin", "japan_ntf")
        num_dir = os.path.join(os.path.dirname(__file__), "..", "mazes", "num", "japan_ntf")
        self.assertTrue(os.path.exists(bin_dir))
        self.assertTrue(os.path.exists(num_dir))
        bin_files = [f for f in os.listdir(bin_dir) if f.endswith(".bin")]
        num_files = [f for f in os.listdir(num_dir) if f.endswith(".num")]
        self.assertEqual(len(bin_files), 103)
        self.assertEqual(len(num_files), 103)

        # Verify janitha_mazes category
        jan_bin = os.path.join(os.path.dirname(__file__), "..", "mazes", "bin", "janitha_mazes")
        jan_num = os.path.join(os.path.dirname(__file__), "..", "mazes", "num", "janitha_mazes")
        self.assertEqual(len(os.listdir(jan_bin)), 4)
        self.assertEqual(len(os.listdir(jan_num)), 4)

        # Test loading and solving Inaugural 1980 All-Japan maze
        m80 = build_preset_maze("AllJapan_001_1980_classic")
        self.assertEqual(m80.size, 16)
        path80 = navigate_ui(Mouse(), m80)
        self.assertGreater(len(path80), 0)
        final_cell = m80[path80[-1][0], path80[-1][1]]
        self.assertIn(final_cell, m80.get_centers())

        # Test loading and solving Inaugural 1980 All-Japan maze
        m80 = build_preset_maze("AllJapan_001_1980_classic")
        self.assertEqual(m80.size, 16)
        path80 = navigate_ui(Mouse(), m80)
        self.assertGreater(len(path80), 0)
        final_cell = m80[path80[-1][0], path80[-1][1]]
        self.assertIn(final_cell, m80.get_centers())


if __name__ == "__main__":
    unittest.main()

