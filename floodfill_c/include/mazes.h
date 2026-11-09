#ifndef MAZES_H
#define MAZES_H

#include <stdint.h>
#include <stdbool.h>
#include "maze_map.h"

/**
 * Compact Micromouse Maze representation.
 * Encodes horizontal and vertical wall bitmasks:
 * - h_walls[y] has bit x set if there is a horizontal wall below cell (x, y).
 * - v_walls[x] has bit y set if there is a vertical wall left of cell (x, y).
 * Requires only 70 bytes for a full 16x16 maze (vs 256 bytes for uint8_t[16][16], or ~10KB for .num).
 */
typedef struct {
    uint8_t width;
    uint8_t height;
    uint16_t h_walls[17];
    uint16_t v_walls[17];
} CompactMaze;

/**
 * Apply a compact maze bitmask to a MazeMap.
 */
void compact_maze_apply(const CompactMaze *cm, MazeMap *map);

/**
 * Static benchmark maze configurations.
 * Statically populates an existing MazeMap instance without any dynamic allocations.
 */
void wall_arrangement_5x5(MazeMap *map);
void wall_arrangement_6x6(MazeMap *map);
void wall_arrangement_10x10(MazeMap *map);
void wall_arrangement_16x16(MazeMap *map);

/**
 * Initialize and populate a MazeMap with a preset configuration (5, 6, 10, or 16).
 * Returns true if the size is supported and initialized, false otherwise.
 */
bool build_preset_maze(MazeMap *map, uint8_t size);


void wall_arrangement_blank(MazeMap *map);
void wall_arrangement_example1(MazeMap *map);
void wall_arrangement_example2(MazeMap *map);
void wall_arrangement_example3(MazeMap *map);
void wall_arrangement_example4(MazeMap *map);
void wall_arrangement_example5(MazeMap *map);

/**
 * Initialize and populate a MazeMap with an MMS preset ("example1", "example2", "example3", "example4", "example5", "blank").
 */
bool build_preset_mms_maze(MazeMap *map, const char *name);

/**
 * Load an MMS .num formatted file into a MazeMap.
 */
bool maze_map_load_num_file(MazeMap *map, const char *filepath);

/**
 * Load a compact binary (.bin) maze file into a MazeMap.
 */
bool maze_map_load_bin_file(MazeMap *map, const char *filepath);

/**
 * Save a MazeMap to a compact binary (.bin) maze file.
 */
bool maze_map_save_bin_file(const MazeMap *map, const char *filepath);

#endif /* MAZES_H */

