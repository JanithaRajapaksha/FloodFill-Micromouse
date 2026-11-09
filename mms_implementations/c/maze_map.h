#ifndef MAZE_MAP_H
#define MAZE_MAP_H

#include <stdint.h>
#include <stdbool.h>

#define MICROMOUSE_MAX_MAZE_SIZE 32
#define MICROMOUSE_MAX_CELLS     (MICROMOUSE_MAX_MAZE_SIZE * MICROMOUSE_MAX_MAZE_SIZE)

#define WALL_NORTH    (1U << 0)
#define WALL_EAST     (1U << 1)
#define WALL_SOUTH    (1U << 2)
#define WALL_WEST     (1U << 3)
#define CELL_VISITED  (1U << 4)

#define DISTANCE_UNREACHABLE 0xFFFF

typedef enum {
    DIR_NORTH = 0,
    DIR_EAST  = 1,
    DIR_SOUTH = 2,
    DIR_WEST  = 3,
    DIR_COUNT = 4
} Direction;

/**
 * Compact, statically-sized maze map representation.
 */
typedef struct {
    uint8_t size_x;
    uint8_t size_y;
    uint8_t walls[MICROMOUSE_MAX_CELLS];       // 1 byte per cell: bitfield (N, E, S, W, VISITED)
    uint16_t distances[MICROMOUSE_MAX_CELLS];  // Manhattan flood-fill distance
} MazeMap;

/**
 * Calculate flat 1D array index from (x, y) coordinates.
 * Coordinates follow Cartesian convention: (0,0) is bottom-left.
 */
static inline uint16_t maze_cell_index(uint8_t size_x, uint8_t size_y, uint8_t x, uint8_t y) {
    (void)size_y;
    return (uint16_t)(y * (uint16_t)size_x + x);
}

/**
 * Convert Direction enum to MMS char ('n', 'e', 's', 'w').
 */
char direction_to_char(Direction dir);

/**
 * Initialize a clear maze map with given dimensions.
 */
void maze_map_init(MazeMap *map, uint8_t size_x, uint8_t size_y);

/**
 * Initialize a maze map with outer boundary walls set.
 */
void maze_map_init_empty(MazeMap *map, uint8_t size_x, uint8_t size_y);

/**
 * Set a wall on cell (x, y) in direction dir and update the reciprocal
 * wall on the neighboring cell if within bounds.
 */
void maze_map_set_wall(MazeMap *map, uint8_t x, uint8_t y, Direction dir);

/**
 * Check if cell (x, y) has a wall in direction dir.
 */
bool maze_map_has_wall(const MazeMap *map, uint8_t x, uint8_t y, Direction dir);

/**
 * Mark a cell as visited.
 */
void maze_map_set_visited(MazeMap *map, uint8_t x, uint8_t y);

/**
 * Check if a cell has been visited.
 */
bool maze_map_is_visited(const MazeMap *map, uint8_t x, uint8_t y);

/**
 * Reset all distance values to DISTANCE_UNREACHABLE.
 */
void maze_map_reset_distances(MazeMap *map);

/**
 * Retrieve destination center coordinates for the maze.
 * Returns count: 1 for odd dimensions, 4 for even dimensions.
 */
uint8_t maze_map_get_centers(const MazeMap *map, uint8_t out_x[4], uint8_t out_y[4]);

#endif /* MAZE_MAP_H */
