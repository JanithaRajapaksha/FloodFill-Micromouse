#ifndef MAZES_H
#define MAZES_H

#include "maze.h"

/**
 * Wall arrangement configurations for benchmark mazes.
 */
void wall_arrangement_5x5(Maze *maze);
void wall_arrangement_6x6(Maze *maze);
void wall_arrangement_10x10(Maze *maze);
void wall_arrangement_16x16(Maze *maze);

/**
 * Build and return a fully configured maze of the given size (5, 6, 10, or 16).
 * Returns NULL if the size is unsupported.
 */
Maze* build_preset_maze(int size);

#endif /* MAZES_H */

