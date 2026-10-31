#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

#include "maze.h"
#include "mouse.h"
#include "floodfill.h"
#include "mazes.h"

static int g_tests_run = 0;
static int g_tests_failed = 0;

#define TEST_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (!(cond)) { \
        printf("FAILED: %s (line %d): %s\n", __func__, __LINE__, msg); \
        g_tests_failed++; \
        return; \
    } \
} while (0)

static void test_cell_and_reciprocal_walls(void) {
    Maze *maze = maze_create(5);
    TEST_ASSERT(maze != NULL, "Maze creation failed");

    Cell *c11 = maze_get_cell(maze, 1, 1);
    TEST_ASSERT(c11 != NULL, "Failed to get cell (1, 1)");
    TEST_ASSERT(c11->x == 1 && c11->y == 1, "Cell coordinates mismatch");
    TEST_ASSERT(c11->value == -1, "Initial cell value must be -1");

    cell_set_north_wall(c11, maze);
    Cell *c12 = maze_get_cell(maze, 1, 2);
    TEST_ASSERT(c11->is_north_wall, "North wall must be set");
    TEST_ASSERT(c12->is_south_wall, "Reciprocal south wall must be set on (1, 2)");
    TEST_ASSERT(strstr(c11->wall_code, "N") != NULL, "Wall code must contain N");
    TEST_ASSERT(strstr(c12->wall_code, "S") != NULL, "Wall code must contain S");

    cell_set_east_wall(c11, maze);
    Cell *c21 = maze_get_cell(maze, 2, 1);
    TEST_ASSERT(c11->is_east_wall, "East wall must be set");
    TEST_ASSERT(c21->is_west_wall, "Reciprocal west wall must be set on (2, 1)");

    maze_destroy(maze);
    printf("PASS: test_cell_and_reciprocal_walls\n");
}

static void test_maze_centers(void) {
    Maze *odd_maze = maze_create(5);
    Cell *odd_centers[4];
    int count_odd = maze_get_centers(odd_maze, odd_centers);
    TEST_ASSERT(count_odd == 1, "5x5 maze must have 1 center");
    TEST_ASSERT(odd_centers[0]->x == 2 && odd_centers[0]->y == 2, "5x5 center must be (2, 2)");
    maze_destroy(odd_maze);

    Maze *even_maze = maze_create(6);
    Cell *even_centers[4];
    int count_even = maze_get_centers(even_maze, even_centers);
    TEST_ASSERT(count_even == 4, "6x6 maze must have 4 centers");
    TEST_ASSERT(even_centers[0]->x == 2 && even_centers[0]->y == 2, "Center 0 mismatch");
    TEST_ASSERT(even_centers[1]->x == 3 && even_centers[1]->y == 2, "Center 1 mismatch");
    TEST_ASSERT(even_centers[2]->x == 2 && even_centers[2]->y == 3, "Center 2 mismatch");
    TEST_ASSERT(even_centers[3]->x == 3 && even_centers[3]->y == 3, "Center 3 mismatch");
    maze_destroy(even_maze);

    printf("PASS: test_maze_centers\n");
}

static void test_mouse_motion_and_sensors(void) {
    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);

    TEST_ASSERT(mouse.orientation == DIR_NORTH, "Initial orientation must be North");
    mouse_turn_right(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_EAST, "Orientation after right turn must be East");
    mouse_turn_right(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_SOUTH, "Orientation after right turn must be South");
    mouse_turn_right(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_WEST, "Orientation after right turn must be West");
    mouse_turn_right(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_NORTH, "Orientation after right turn must be North");

    mouse_turn_left(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_WEST, "Orientation after left turn must be West");
    mouse_turn_back(&mouse);
    TEST_ASSERT(mouse.orientation == DIR_EAST, "Orientation after back turn must be East");

    // Movement
    mouse_init(&mouse, 1, 1, DIR_NORTH);
    mouse_move_forward(&mouse);
    TEST_ASSERT(mouse.x == 1 && mouse.y == 2, "Moving North should increment y");

    mouse.orientation = DIR_EAST;
    mouse_move_forward(&mouse);
    TEST_ASSERT(mouse.x == 2 && mouse.y == 2, "Moving East should increment x");

    mouse.orientation = DIR_SOUTH;
    mouse_move_forward(&mouse);
    TEST_ASSERT(mouse.x == 2 && mouse.y == 1, "Moving South should decrement y");

    mouse.orientation = DIR_WEST;
    mouse_move_forward(&mouse);
    TEST_ASSERT(mouse.x == 1 && mouse.y == 1, "Moving West should decrement x");

    // Sensing
    Maze *m = maze_create_empty(4);
    cell_set_north_wall(maze_get_cell(m, 0, 0), m);

    mouse_init(&mouse, 0, 0, DIR_NORTH);
    mouse_update_sensors(&mouse, m);
    TEST_ASSERT(mouse.is_on_front_sensor, "Front sensor should detect North wall");
    TEST_ASSERT(mouse.is_on_left_sensor, "Left sensor should detect West perimeter");
    TEST_ASSERT(!mouse.is_on_right_sensor, "Right sensor should not detect wall");

    maze_destroy(m);
    printf("PASS: test_mouse_motion_and_sensors\n");
}

static void test_preset_5x5_navigation(void) {
    Maze *maze = build_preset_maze(5);
    TEST_ASSERT(maze != NULL, "Failed to build 5x5 maze");

    Cell *centers[4];
    int num_centers = maze_get_centers(maze, centers);
    flood_fill(maze, centers, num_centers);

    TEST_ASSERT(maze_get_cell(maze, 0, 0)->value == 6, "5x5 distance at (0, 0) must be 6");
    TEST_ASSERT(maze_get_cell(maze, 2, 2)->value == 0, "5x5 distance at (2, 2) must be 0");

    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);
    Path *path = navigate_ui(&mouse, maze);
    TEST_ASSERT(path != NULL, "Navigation returned NULL path");
    TEST_ASSERT(path->count == 6, "5x5 path count must be 6");

    static const int expected[6][3] = {
        {0, 1, 0},
        {1, 1, 1},
        {1, 2, 0},
        {1, 3, 0},
        {2, 3, 1},
        {2, 2, 2}
    };
    for (int i = 0; i < 6; ++i) {
        TEST_ASSERT(path->steps[i].x == expected[i][0] &&
                    path->steps[i].y == expected[i][1] &&
                    path->steps[i].orientation == expected[i][2],
                    "5x5 path step mismatch");
    }

    path_destroy(path);
    maze_destroy(maze);
    printf("PASS: test_preset_5x5_navigation\n");
}

static void test_preset_6x6_navigation(void) {
    Maze *maze = build_preset_maze(6);
    TEST_ASSERT(maze != NULL, "Failed to build 6x6 maze");

    Cell *centers[4];
    int num_centers = maze_get_centers(maze, centers);
    flood_fill(maze, centers, num_centers);

    TEST_ASSERT(maze_get_cell(maze, 0, 0)->value == 8, "6x6 distance at (0, 0) must be 8");

    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);
    Path *path = navigate_ui(&mouse, maze);
    TEST_ASSERT(path != NULL, "Navigation returned NULL path");
    TEST_ASSERT(path->count == 18, "6x6 path count must be 18");
    TEST_ASSERT(path->steps[0].x == 0 && path->steps[0].y == 1 && path->steps[0].orientation == 0, "6x6 first step mismatch");
    TEST_ASSERT(path->steps[17].x == 3 && path->steps[17].y == 3 && path->steps[17].orientation == 2, "6x6 final step mismatch");

    path_destroy(path);
    maze_destroy(maze);
    printf("PASS: test_preset_6x6_navigation\n");
}

static void test_preset_10x10_navigation(void) {
    Maze *maze = build_preset_maze(10);
    TEST_ASSERT(maze != NULL, "Failed to build 10x10 maze");

    Cell *centers[4];
    int num_centers = maze_get_centers(maze, centers);
    flood_fill(maze, centers, num_centers);

    TEST_ASSERT(maze_get_cell(maze, 0, 0)->value == 8, "10x10 distance at (0, 0) must be 8");

    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);
    Path *path = navigate_ui(&mouse, maze);
    TEST_ASSERT(path != NULL, "Navigation returned NULL path");
    TEST_ASSERT(path->count == 10, "10x10 path count must be 10");

    static const int expected[10][3] = {
        {0, 1, 0},
        {0, 2, 0},
        {0, 3, 0},
        {1, 3, 1},
        {1, 4, 0},
        {1, 5, 0},
        {2, 5, 1},
        {2, 4, 2},
        {3, 4, 1},
        {4, 4, 1}
    };
    for (int i = 0; i < 10; ++i) {
        TEST_ASSERT(path->steps[i].x == expected[i][0] &&
                    path->steps[i].y == expected[i][1] &&
                    path->steps[i].orientation == expected[i][2],
                    "10x10 path step mismatch");
    }

    path_destroy(path);
    maze_destroy(maze);
    printf("PASS: test_preset_10x10_navigation\n");
}

static void test_preset_16x16_navigation(void) {
    Maze *maze = build_preset_maze(16);
    TEST_ASSERT(maze != NULL, "Failed to build 16x16 maze");

    Cell *centers[4];
    int num_centers = maze_get_centers(maze, centers);
    flood_fill(maze, centers, num_centers);

    TEST_ASSERT(maze_get_cell(maze, 0, 0)->value == 44, "16x16 distance at (0, 0) must be 44");

    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);
    Path *path = navigate_ui(&mouse, maze);
    TEST_ASSERT(path != NULL, "Navigation returned NULL path");
    TEST_ASSERT(path->count == 100, "16x16 path count must be 100");
    TEST_ASSERT(path->steps[0].x == 0 && path->steps[0].y == 1 && path->steps[0].orientation == 0, "16x16 first step mismatch");
    TEST_ASSERT(path->steps[99].x == 7 && path->steps[99].y == 7 && path->steps[99].orientation == 1, "16x16 final step mismatch");

    path_destroy(path);
    maze_destroy(maze);
    printf("PASS: test_preset_16x16_navigation\n");
}

int main(void) {
    printf("Running Flood-Fill C Unit Tests...\n");
    test_cell_and_reciprocal_walls();
    test_maze_centers();
    test_mouse_motion_and_sensors();
    test_preset_5x5_navigation();
    test_preset_6x6_navigation();
    test_preset_10x10_navigation();
    test_preset_16x16_navigation();

    printf("\nTotal assertions checked: %d\n", g_tests_run);
    if (g_tests_failed == 0) {
        printf("ALL TESTS PASSED SUCCESSFULLY!\n");
        return 0;
    } else {
        printf("TESTS FAILED: %d\n", g_tests_failed);
        return 1;
    }
}

