#include <stdio.h>
#include <stdlib.h>
#include "floodfill.h"

Path* path_create(int initial_capacity) {
    if (initial_capacity <= 0) {
        initial_capacity = 16;
    }
    Path *path = (Path*)malloc(sizeof(Path));
    if (!path) return NULL;

    path->steps = (PathStep*)malloc(sizeof(PathStep) * initial_capacity);
    if (!path->steps) {
        free(path);
        return NULL;
    }
    path->count = 0;
    path->capacity = initial_capacity;
    return path;
}

void path_append(Path *path, int x, int y, int orientation) {
    if (!path) return;
    if (path->count >= path->capacity) {
        int new_capacity = path->capacity * 2;
        PathStep *new_steps = (PathStep*)realloc(path->steps, sizeof(PathStep) * new_capacity);
        if (!new_steps) return;
        path->steps = new_steps;
        path->capacity = new_capacity;
    }
    path->steps[path->count].x = x;
    path->steps[path->count].y = y;
    path->steps[path->count].orientation = orientation;
    path->count++;
}

void path_destroy(Path *path) {
    if (path) {
        if (path->steps) {
            free(path->steps);
        }
        free(path);
    }
}

typedef struct {
    Cell *cell;
    int dist;
} QueueNode;

void flood_fill(Maze *maze, Cell **goal_cells, int num_goals) {
    if (!maze || !goal_cells || num_goals <= 0) return;

    int total_cells = maze->size * maze->size;
    QueueNode *queue = (QueueNode*)malloc(sizeof(QueueNode) * total_cells);
    if (!queue) return;

    int head = 0;
    int tail = 0;

    for (int i = 0; i < num_goals; ++i) {
        if (goal_cells[i]) {
            goal_cells[i]->value = 0;
            queue[tail++] = (QueueNode){goal_cells[i], 0};
        }
    }

    int size = maze->size;

    while (head < tail) {
        QueueNode node = queue[head++];
        Cell *cur = node.cell;
        int next_dist = node.dist + 1;
        int cx = cur->x;
        int cy = cur->y;

        // Check neighbors in fixed order: North, East, South, West

        // North
        if (cy + 1 < size && !cur->is_north_wall) {
            Cell *neighbor = maze_get_cell(maze, cx, cy + 1);
            if (neighbor && neighbor->value == -1) {
                neighbor->value = next_dist;
                queue[tail++] = (QueueNode){neighbor, next_dist};
            }
        }

        // East
        if (cx + 1 < size && !cur->is_east_wall) {
            Cell *neighbor = maze_get_cell(maze, cx + 1, cy);
            if (neighbor && neighbor->value == -1) {
                neighbor->value = next_dist;
                queue[tail++] = (QueueNode){neighbor, next_dist};
            }
        }

        // South
        if (cy - 1 >= 0 && !cur->is_south_wall) {
            Cell *neighbor = maze_get_cell(maze, cx, cy - 1);
            if (neighbor && neighbor->value == -1) {
                neighbor->value = next_dist;
                queue[tail++] = (QueueNode){neighbor, next_dist};
            }
        }

        // West
        if (cx - 1 >= 0 && !cur->is_west_wall) {
            Cell *neighbor = maze_get_cell(maze, cx - 1, cy);
            if (neighbor && neighbor->value == -1) {
                neighbor->value = next_dist;
                queue[tail++] = (QueueNode){neighbor, next_dist};
            }
        }
    }

    free(queue);
}

Path* navigate(Mouse *mouse, const Maze *testing_maze, bool verbose) {
    if (!mouse || !testing_maze) return NULL;

    mouse->x = 0;
    mouse->y = 0;
    mouse->orientation = DIR_NORTH;
    mouse_set_sides(mouse);

    Path *path = path_create(32);
    if (!path) return NULL;

    Maze *empty_maze = maze_create_empty(testing_maze->size);
    if (!empty_maze) {
        path_destroy(path);
        return NULL;
    }

    Cell *goal_cells[4];
    int num_goals = maze_get_centers(empty_maze, goal_cells);

    while (true) {
        Cell *current_cell = maze_get_cell(empty_maze, mouse->x, mouse->y);

        // Update sensor readings and discovered maze map
        mouse_update_sensors(mouse, testing_maze);
        mouse_update_maze_walls(mouse, empty_maze);

        // Compute shortest distance gradient from goal
        maze_reset_values(empty_maze);
        flood_fill(empty_maze, goal_cells, num_goals);

        int next_cell_value = current_cell->value - 1;

        // Select next cell along the gradient in order: North, East, South, West
        Cell *next_cell = NULL;

        if (mouse->y + 1 < empty_maze->size && !current_cell->is_north_wall) {
            Cell *neighbor = maze_get_cell(empty_maze, mouse->x, mouse->y + 1);
            if (neighbor && neighbor->value == next_cell_value) {
                next_cell = neighbor;
            }
        }
        if (!next_cell && mouse->x + 1 < empty_maze->size && !current_cell->is_east_wall) {
            Cell *neighbor = maze_get_cell(empty_maze, mouse->x + 1, mouse->y);
            if (neighbor && neighbor->value == next_cell_value) {
                next_cell = neighbor;
            }
        }
        if (!next_cell && mouse->y - 1 >= 0 && !current_cell->is_south_wall) {
            Cell *neighbor = maze_get_cell(empty_maze, mouse->x, mouse->y - 1);
            if (neighbor && neighbor->value == next_cell_value) {
                next_cell = neighbor;
            }
        }
        if (!next_cell && mouse->x - 1 >= 0 && !current_cell->is_west_wall) {
            Cell *neighbor = maze_get_cell(empty_maze, mouse->x - 1, mouse->y);
            if (neighbor && neighbor->value == next_cell_value) {
                next_cell = neighbor;
            }
        }

        if (!next_cell) {
            if (verbose) {
                printf("No accessible neighbor found for cell (%d, %d) with value %d. Reapplying flood fill.\n",
                       mouse->x, mouse->y, next_cell_value);
            }
            if (current_cell->value == 0) {
                if (verbose) {
                    printf("( %d ,  %d )    %d\n", mouse->x, mouse->y, (int)mouse->orientation);
                }
                break;
            }

            // Fallback for local dead-end
            maze_reset_values(empty_maze);
            flood_fill(empty_maze, &current_cell, 1);

            if (mouse->y + 1 < empty_maze->size && !current_cell->is_north_wall) {
                Cell *neighbor = maze_get_cell(empty_maze, mouse->x, mouse->y + 1);
                if (neighbor && neighbor->value == next_cell_value) next_cell = neighbor;
            }
            if (!next_cell && mouse->x + 1 < empty_maze->size && !current_cell->is_east_wall) {
                Cell *neighbor = maze_get_cell(empty_maze, mouse->x + 1, mouse->y);
                if (neighbor && neighbor->value == next_cell_value) next_cell = neighbor;
            }
            if (!next_cell && mouse->y - 1 >= 0 && !current_cell->is_south_wall) {
                Cell *neighbor = maze_get_cell(empty_maze, mouse->x, mouse->y - 1);
                if (neighbor && neighbor->value == next_cell_value) next_cell = neighbor;
            }
            if (!next_cell && mouse->x - 1 >= 0 && !current_cell->is_west_wall) {
                Cell *neighbor = maze_get_cell(empty_maze, mouse->x - 1, mouse->y);
                if (neighbor && neighbor->value == next_cell_value) next_cell = neighbor;
            }

            if (!next_cell) {
                fprintf(stderr, "Error: No accessible neighbor with required value found after flood fill.\n");
                break;
            }
        }

        mouse_update_orientation(mouse, current_cell, next_cell);
        mouse_move_forward(mouse);

        if (verbose) {
            printf("( %d ,  %d )    %d\n", mouse->x, mouse->y, (int)mouse->orientation);
        }

        path_append(path, mouse->x, mouse->y, (int)mouse->orientation);
    }

    maze_destroy(empty_maze);
    return path;
}

Path* navigate_ui(Mouse *mouse, const Maze *testing_maze) {
    return navigate(mouse, testing_maze, false);
}
