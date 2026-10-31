#ifndef MAZE_H
#define MAZE_H

#include <stdbool.h>

/**
 * Cardinal directions for movement and wall orientation.
 * 0: North (+y)
 * 1: East  (+x)
 * 2: South (-y)
 * 3: West  (-x)
 */
typedef enum {
    DIR_NORTH = 0,
    DIR_EAST  = 1,
    DIR_SOUTH = 2,
    DIR_WEST  = 3
} Direction;

/**
 * Represents an individual cell within the maze.
 */
typedef struct {
    int x;
    int y;
    bool is_north_wall;
    bool is_south_wall;
    bool is_west_wall;
    bool is_east_wall;
    char wall_code[5]; // Canonical sorted string: 'E', 'N', 'S', 'W'
    int value;         // Flood-fill distance value (-1 if unassigned)
} Cell;

/**
 * Represents an N x N maze grid.
 */
typedef struct {
    int size;
    Cell *cells; // Flat array of size * size elements
} Maze;

/**
 * Create a new dynamically allocated maze of the given dimension.
 */
Maze* maze_create(int size);

/**
 * Free all memory associated with the maze.
 */
void maze_destroy(Maze *maze);

/**
 * Retrieve cell pointer at coordinates (x, y). Returns NULL if out of bounds.
 */
Cell* maze_get_cell(Maze *maze, int x, int y);
const Cell* maze_get_cell_const(const Maze *maze, int x, int y);

/**
 * Update the canonical wall_code string of a cell.
 */
void cell_update_wall_code(Cell *cell);

/**
 * Set walls on a cell and update reciprocal walls on adjacent neighbors.
 */
void cell_set_north_wall(Cell *cell, Maze *maze);
void cell_set_south_wall(Cell *cell, Maze *maze);
void cell_set_west_wall(Cell *cell, Maze *maze);
void cell_set_east_wall(Cell *cell, Maze *maze);

/**
 * Update wall codes for all cells in the maze.
 */
void maze_update_all_wall_codes(Maze *maze);

/**
 * Reset flood-fill values of all cells to -1.
 */
void maze_reset_values(Maze *maze);

/**
 * Get the center destination cells of the maze.
 * Fills out_centers with 1 cell for odd sizes, 4 cells for even sizes.
 * Returns the number of center cells (1 or 4).
 */
int maze_get_centers(const Maze *maze, Cell *out_centers[4]);

/**
 * Create a maze with outer perimeter boundary walls set.
 */
Maze* maze_create_empty(int size);

#endif /* MAZE_H */

