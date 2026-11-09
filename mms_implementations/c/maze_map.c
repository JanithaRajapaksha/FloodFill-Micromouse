#include "maze_map.h"
#include <string.h>

static const uint8_t WALL_MASKS[DIR_COUNT] = {
    WALL_NORTH, // DIR_NORTH = 0
    WALL_EAST,  // DIR_EAST  = 1
    WALL_SOUTH, // DIR_SOUTH = 2
    WALL_WEST   // DIR_WEST  = 3
};

static const uint8_t RECIPROCAL_MASKS[DIR_COUNT] = {
    WALL_SOUTH, // opposite of North is South
    WALL_WEST,  // opposite of East is West
    WALL_NORTH, // opposite of South is North
    WALL_EAST   // opposite of West is East
};

char direction_to_char(Direction dir) {
    switch (dir) {
        case DIR_NORTH: return 'n';
        case DIR_EAST:  return 'e';
        case DIR_SOUTH: return 's';
        case DIR_WEST:  return 'w';
        default:        return 'n';
    }
}

void maze_map_init(MazeMap *map, uint8_t size_x, uint8_t size_y) {
    if (!map) return;
    if (size_x > MICROMOUSE_MAX_MAZE_SIZE) size_x = MICROMOUSE_MAX_MAZE_SIZE;
    if (size_y > MICROMOUSE_MAX_MAZE_SIZE) size_y = MICROMOUSE_MAX_MAZE_SIZE;
    map->size_x = size_x;
    map->size_y = size_y;
    memset(map->walls, 0, sizeof(map->walls));
    maze_map_reset_distances(map);
}

void maze_map_init_empty(MazeMap *map, uint8_t size_x, uint8_t size_y) {
    maze_map_init(map, size_x, size_y);
    for (uint8_t y = 0; y < size_y; ++y) {
        for (uint8_t x = 0; x < size_x; ++x) {
            if (x == 0) {
                maze_map_set_wall(map, x, y, DIR_WEST);
            }
            if (x == size_x - 1) {
                maze_map_set_wall(map, x, y, DIR_EAST);
            }
            if (y == 0) {
                maze_map_set_wall(map, x, y, DIR_SOUTH);
            }
            if (y == size_y - 1) {
                maze_map_set_wall(map, x, y, DIR_NORTH);
            }
        }
    }
}

void maze_map_set_wall(MazeMap *map, uint8_t x, uint8_t y, Direction dir) {
    if (!map || x >= map->size_x || y >= map->size_y || dir >= DIR_COUNT) {
        return;
    }

    uint16_t idx = maze_cell_index(map->size_x, map->size_y, x, y);
    map->walls[idx] |= WALL_MASKS[dir];

    // Set reciprocal wall on adjacent cell if within bounds
    switch (dir) {
        case DIR_NORTH:
            if (y + 1 < map->size_y) {
                map->walls[maze_cell_index(map->size_x, map->size_y, x, y + 1)] |= RECIPROCAL_MASKS[DIR_NORTH];
            }
            break;
        case DIR_EAST:
            if (x + 1 < map->size_x) {
                map->walls[maze_cell_index(map->size_x, map->size_y, x + 1, y)] |= RECIPROCAL_MASKS[DIR_EAST];
            }
            break;
        case DIR_SOUTH:
            if (y > 0) {
                map->walls[maze_cell_index(map->size_x, map->size_y, x, y - 1)] |= RECIPROCAL_MASKS[DIR_SOUTH];
            }
            break;
        case DIR_WEST:
            if (x > 0) {
                map->walls[maze_cell_index(map->size_x, map->size_y, x - 1, y)] |= RECIPROCAL_MASKS[DIR_WEST];
            }
            break;
        default:
            break;
    }
}

bool maze_map_has_wall(const MazeMap *map, uint8_t x, uint8_t y, Direction dir) {
    if (!map || x >= map->size_x || y >= map->size_y || dir >= DIR_COUNT) {
        return true; // Out of bounds treated as walled
    }
    uint16_t idx = maze_cell_index(map->size_x, map->size_y, x, y);
    return (map->walls[idx] & WALL_MASKS[dir]) != 0;
}

void maze_map_set_visited(MazeMap *map, uint8_t x, uint8_t y) {
    if (!map || x >= map->size_x || y >= map->size_y) return;
    map->walls[maze_cell_index(map->size_x, map->size_y, x, y)] |= CELL_VISITED;
}

bool maze_map_is_visited(const MazeMap *map, uint8_t x, uint8_t y) {
    if (!map || x >= map->size_x || y >= map->size_y) return false;
    return (map->walls[maze_cell_index(map->size_x, map->size_y, x, y)] & CELL_VISITED) != 0;
}

void maze_map_reset_distances(MazeMap *map) {
    if (!map) return;
    for (size_t i = 0; i < MICROMOUSE_MAX_CELLS; ++i) {
        map->distances[i] = DISTANCE_UNREACHABLE;
    }
}

uint8_t maze_map_get_centers(const MazeMap *map, uint8_t out_x[4], uint8_t out_y[4]) {
    if (!map || !out_x || !out_y) return 0;
    uint8_t mid_x = map->size_x / 2U;
    uint8_t mid_y = map->size_y / 2U;

    if (map->size_x % 2U == 1U && map->size_y % 2U == 1U) {
        out_x[0] = mid_x;
        out_y[0] = mid_y;
        return 1U;
    }

    out_x[0] = mid_x - 1U; out_y[0] = mid_y - 1U;
    out_x[1] = mid_x;      out_y[1] = mid_y - 1U;
    out_x[2] = mid_x - 1U; out_y[2] = mid_y;
    out_x[3] = mid_x;      out_y[3] = mid_y;
    return 4U;
}
