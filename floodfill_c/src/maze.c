#include <stdlib.h>
#include <string.h>
#include "maze.h"

Maze* maze_create(int size) {
    if (size <= 0) {
        return NULL;
    }

    Maze *maze = (Maze*)malloc(sizeof(Maze));
    if (!maze) {
        return NULL;
    }

    maze->size = size;
    maze->cells = (Cell*)malloc(sizeof(Cell) * size * size);
    if (!maze->cells) {
        free(maze);
        return NULL;
    }

    for (int actual_y = 0; actual_y < size; ++actual_y) {
        int y = size - 1 - actual_y;
        for (int x = 0; x < size; ++x) {
            Cell *cell = &maze->cells[actual_y * size + x];
            cell->x = x;
            cell->y = y;
            cell->is_north_wall = false;
            cell->is_south_wall = false;
            cell->is_west_wall = false;
            cell->is_east_wall = false;
            cell->wall_code[0] = '\0';
            cell->value = -1;
        }
    }

    return maze;
}

void maze_destroy(Maze *maze) {
    if (maze) {
        if (maze->cells) {
            free(maze->cells);
        }
        free(maze);
    }
}

Cell* maze_get_cell(Maze *maze, int x, int y) {
    if (!maze || x < 0 || x >= maze->size || y < 0 || y >= maze->size) {
        return NULL;
    }
    int actual_y = maze->size - 1 - y;
    return &maze->cells[actual_y * maze->size + x];
}

const Cell* maze_get_cell_const(const Maze *maze, int x, int y) {
    if (!maze || x < 0 || x >= maze->size || y < 0 || y >= maze->size) {
        return NULL;
    }
    int actual_y = maze->size - 1 - y;
    return &maze->cells[actual_y * maze->size + x];
}

void cell_update_wall_code(Cell *cell) {
    if (!cell) return;
    int idx = 0;
    if (cell->is_east_wall)  cell->wall_code[idx++] = 'E';
    if (cell->is_north_wall) cell->wall_code[idx++] = 'N';
    if (cell->is_south_wall) cell->wall_code[idx++] = 'S';
    if (cell->is_west_wall)  cell->wall_code[idx++] = 'W';
    cell->wall_code[idx] = '\0';
}

void cell_set_north_wall(Cell *cell, Maze *maze) {
    if (!cell) return;
    cell->is_north_wall = true;
    if (maze) {
        Cell *neighbor = maze_get_cell(maze, cell->x, cell->y + 1);
        if (neighbor) {
            neighbor->is_south_wall = true;
            cell_update_wall_code(neighbor);
        }
    }
    cell_update_wall_code(cell);
}

void cell_set_south_wall(Cell *cell, Maze *maze) {
    if (!cell) return;
    cell->is_south_wall = true;
    if (maze) {
        Cell *neighbor = maze_get_cell(maze, cell->x, cell->y - 1);
        if (neighbor) {
            neighbor->is_north_wall = true;
            cell_update_wall_code(neighbor);
        }
    }
    cell_update_wall_code(cell);
}

void cell_set_west_wall(Cell *cell, Maze *maze) {
    if (!cell) return;
    cell->is_west_wall = true;
    if (maze) {
        Cell *neighbor = maze_get_cell(maze, cell->x - 1, cell->y);
        if (neighbor) {
            neighbor->is_east_wall = true;
            cell_update_wall_code(neighbor);
        }
    }
    cell_update_wall_code(cell);
}

void cell_set_east_wall(Cell *cell, Maze *maze) {
    if (!cell) return;
    cell->is_east_wall = true;
    if (maze) {
        Cell *neighbor = maze_get_cell(maze, cell->x + 1, cell->y);
        if (neighbor) {
            neighbor->is_west_wall = true;
            cell_update_wall_code(neighbor);
        }
    }
    cell_update_wall_code(cell);
}

void maze_update_all_wall_codes(Maze *maze) {
    if (!maze) return;
    int total = maze->size * maze->size;
    for (int i = 0; i < total; ++i) {
        cell_update_wall_code(&maze->cells[i]);
    }
}

void maze_reset_values(Maze *maze) {
    if (!maze) return;
    int total = maze->size * maze->size;
    for (int i = 0; i < total; ++i) {
        maze->cells[i].value = -1;
    }
}

int maze_get_centers(const Maze *maze, Cell *out_centers[4]) {
    if (!maze || !out_centers) return 0;
    int mid = maze->size / 2;
    if (maze->size % 2 == 1) {
        out_centers[0] = maze_get_cell((Maze*)maze, mid, mid);
        return 1;
    }
    out_centers[0] = maze_get_cell((Maze*)maze, mid - 1, mid - 1);
    out_centers[1] = maze_get_cell((Maze*)maze, mid,     mid - 1);
    out_centers[2] = maze_get_cell((Maze*)maze, mid - 1, mid);
    out_centers[3] = maze_get_cell((Maze*)maze, mid,     mid);
    return 4;
}

Maze* maze_create_empty(int size) {
    Maze *maze = maze_create(size);
    if (!maze) return NULL;

    int total = size * size;
    for (int i = 0; i < total; ++i) {
        Cell *cell = &maze->cells[i];
        if (cell->x == 0) {
            cell_set_west_wall(cell, maze);
        }
        if (cell->x == size - 1) {
            cell_set_east_wall(cell, maze);
        }
        if (cell->y == 0) {
            cell_set_south_wall(cell, maze);
        }
        if (cell->y == size - 1) {
            cell_set_north_wall(cell, maze);
        }
    }
    return maze;
}

