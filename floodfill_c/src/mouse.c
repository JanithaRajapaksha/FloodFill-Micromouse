#include "mouse.h"

static const int DELTA_X[4] = {0, 1, 0, -1};
static const int DELTA_Y[4] = {1, 0, -1, 0};

static const char SIDES_LEFT[4]  = {'W', 'N', 'E', 'S'};
static const char SIDES_RIGHT[4] = {'E', 'S', 'W', 'N'};
static const char SIDES_FRONT[4] = {'N', 'E', 'S', 'W'};

void mouse_init(Mouse *mouse, int x, int y, Direction orientation) {
    if (!mouse) return;
    mouse->x = x;
    mouse->y = y;
    mouse->orientation = orientation;
    mouse->is_on_front_sensor = false;
    mouse->is_on_left_sensor  = false;
    mouse->is_on_right_sensor = false;
    mouse_set_sides(mouse);
}

void mouse_set_sides(Mouse *mouse) {
    if (!mouse) return;
    int o = (int)mouse->orientation;
    mouse->left_code  = SIDES_LEFT[o];
    mouse->right_code = SIDES_RIGHT[o];
    mouse->front_code = SIDES_FRONT[o];
}

void mouse_turn_left(Mouse *mouse) {
    if (!mouse) return;
    mouse->orientation = (Direction)((mouse->orientation + 3) % 4);
    mouse_set_sides(mouse);
}

void mouse_turn_right(Mouse *mouse) {
    if (!mouse) return;
    mouse->orientation = (Direction)((mouse->orientation + 1) % 4);
    mouse_set_sides(mouse);
}

void mouse_turn_back(Mouse *mouse) {
    if (!mouse) return;
    mouse->orientation = (Direction)((mouse->orientation + 2) % 4);
    mouse_set_sides(mouse);
}

void mouse_move_forward(Mouse *mouse) {
    if (!mouse) return;
    mouse->x += DELTA_X[mouse->orientation];
    mouse->y += DELTA_Y[mouse->orientation];
}

void mouse_update_orientation(Mouse *mouse, const Cell *current_cell, const Cell *next_cell) {
    if (!mouse || !current_cell || !next_cell) return;
    int dx = next_cell->x - current_cell->x;
    int dy = next_cell->y - current_cell->y;

    if (dx == 0 && dy == 1) {
        mouse->orientation = DIR_NORTH;
    } else if (dx == 1 && dy == 0) {
        mouse->orientation = DIR_EAST;
    } else if (dx == 0 && dy == -1) {
        mouse->orientation = DIR_SOUTH;
    } else if (dx == -1 && dy == 0) {
        mouse->orientation = DIR_WEST;
    }
    mouse_set_sides(mouse);
}

void mouse_update_sensors(Mouse *mouse, const Maze *testing_maze) {
    if (!mouse || !testing_maze) return;
    mouse_set_sides(mouse);

    const Cell *cell = maze_get_cell_const(testing_maze, mouse->x, mouse->y);
    if (!cell) return;

    bool walls[4] = {
        cell->is_north_wall,
        cell->is_east_wall,
        cell->is_south_wall,
        cell->is_west_wall
    };

    int o = (int)mouse->orientation;
    mouse->is_on_front_sensor = walls[o];
    mouse->is_on_left_sensor  = walls[(o + 3) % 4];
    mouse->is_on_right_sensor = walls[(o + 1) % 4];
}

void mouse_update_maze_walls(const Mouse *mouse, Maze *empty_maze) {
    if (!mouse || !empty_maze) return;

    Cell *cell = maze_get_cell(empty_maze, mouse->x, mouse->y);
    if (!cell) return;

    typedef void (*WallSetter)(Cell*, Maze*);
    static const WallSetter setters[4] = {
        cell_set_north_wall,
        cell_set_east_wall,
        cell_set_south_wall,
        cell_set_west_wall
    };

    int o = (int)mouse->orientation;
    if (mouse->is_on_front_sensor) {
        setters[o](cell, empty_maze);
    }
    if (mouse->is_on_left_sensor) {
        setters[(o + 3) % 4](cell, empty_maze);
    }
    if (mouse->is_on_right_sensor) {
        setters[(o + 1) % 4](cell, empty_maze);
    }
}

