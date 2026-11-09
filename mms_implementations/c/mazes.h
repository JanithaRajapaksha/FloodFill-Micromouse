#ifndef MAZES_H
#define MAZES_H

#include <stdint.h>
#include <stdbool.h>
#include "maze_map.h"

/**
 * Load walls from an MMS .num formatted file into a MazeMap.
 * Format per line: "x y north east south west"
 */
bool maze_map_load_num_file(MazeMap *map, const char *filepath);

/**
 * Load an MMS preset maze by name:
 * "example1", "example2", "example3", "example4", "example5", "blank"
 */
bool maze_map_load_preset(MazeMap *map, const char *preset_name);

/**
 * Standard embedded benchmark configurations.
 */
void wall_arrangement_5x5(MazeMap *map);
void wall_arrangement_6x6(MazeMap *map);
void wall_arrangement_10x10(MazeMap *map);

/**
 * Factory to construct a preset maze by dimension (5, 6, 10, 16).
 */
bool build_preset_maze(MazeMap *map, uint8_t size);

#endif /* MAZES_H */
