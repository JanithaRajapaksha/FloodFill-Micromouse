#ifndef FLOODFILL_H
#define FLOODFILL_H

#include <stdbool.h>
#include "maze.h"
#include "mouse.h"

/**
 * A single step in the mouse trajectory: (x, y, orientation).
 */
typedef struct {
    int x;
    int y;
    int orientation;
} PathStep;

/**
 * Dynamic container for trajectory steps.
 */
typedef struct {
    PathStep *steps;
    int count;
    int capacity;
} Path;

/**
 * Path lifecycle functions.
 */
Path* path_create(int initial_capacity);
void path_append(Path *path, int x, int y, int orientation);
void path_destroy(Path *path);

/**
 * Run BFS flood fill from goal cells across the maze.
 */
void flood_fill(Maze *maze, Cell **goal_cells, int num_goals);

/**
 * Simulate micromouse navigating the testing_maze.
 * If verbose is true, logs each step and diagnostic messages to stdout.
 * Returns a dynamically allocated Path* containing all steps taken.
 */
Path* navigate(Mouse *mouse, const Maze *testing_maze, bool verbose);

/**
 * Silent navigation returning the trajectory Path*.
 */
Path* navigate_ui(Mouse *mouse, const Maze *testing_maze);

#endif /* FLOODFILL_H */

