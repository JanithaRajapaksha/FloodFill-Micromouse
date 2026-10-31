#ifndef MOUSE_H
#define MOUSE_H

#include <stdbool.h>
#include "maze.h"

/**
 * Micromouse robot model tracking position, orientation, and sensors.
 */
typedef struct {
    int x;
    int y;
    Direction orientation;
    char left_code;
    char right_code;
    char front_code;
    bool is_on_front_sensor;
    bool is_on_left_sensor;
    bool is_on_right_sensor;
} Mouse;

/**
 * Initialize a mouse at (x, y) with the given initial orientation.
 */
void mouse_init(Mouse *mouse, int x, int y, Direction orientation);

/**
 * Update the relative side codes ('N', 'S', 'E', 'W') for front/left/right.
 */
void mouse_set_sides(Mouse *mouse);

/**
 * Turn mouse 90 degrees counter-clockwise.
 */
void mouse_turn_left(Mouse *mouse);

/**
 * Turn mouse 90 degrees clockwise.
 */
void mouse_turn_right(Mouse *mouse);

/**
 * Turn mouse 180 degrees.
 */
void mouse_turn_back(Mouse *mouse);

/**
 * Move one step forward in current orientation direction.
 */
void mouse_move_forward(Mouse *mouse);

/**
 * Update orientation based on the step from current_cell to next_cell.
 */
void mouse_update_orientation(Mouse *mouse, const Cell *current_cell, const Cell *next_cell);

/**
 * Read wall sensors at the mouse's current position from testing_maze.
 */
void mouse_update_sensors(Mouse *mouse, const Maze *testing_maze);

/**
 * Project sensed walls into the empty/discovered maze map.
 */
void mouse_update_maze_walls(const Mouse *mouse, Maze *empty_maze);

#endif /* MOUSE_H */

