#include <stdlib.h>
#include "mazes.h"

#define SET_N(m, x, y) cell_set_north_wall(maze_get_cell((m), (x), (y)), (m))
#define SET_S(m, x, y) cell_set_south_wall(maze_get_cell((m), (x), (y)), (m))
#define SET_E(m, x, y) cell_set_east_wall(maze_get_cell((m), (x), (y)), (m))
#define SET_W(m, x, y) cell_set_west_wall(maze_get_cell((m), (x), (y)), (m))

void wall_arrangement_5x5(Maze *maze) {
    if (!maze) return;
    SET_E(maze, 0, 0);
    SET_N(maze, 2, 0);
    SET_E(maze, 2, 0);
    SET_N(maze, 3, 0);
    SET_N(maze, 2, 1);
    SET_E(maze, 2, 1);
    SET_S(maze, 0, 2);
    SET_E(maze, 0, 2);
    SET_E(maze, 1, 2);
    SET_N(maze, 3, 2);
    SET_E(maze, 3, 2);
    SET_N(maze, 0, 3);
    SET_E(maze, 1, 4);
    SET_S(maze, 3, 4);
    SET_S(maze, 4, 4);
    maze_update_all_wall_codes(maze);
}

void wall_arrangement_6x6(Maze *maze) {
    if (!maze) return;
    SET_N(maze, 2, 0);
    SET_N(maze, 3, 0);
    SET_E(maze, 4, 0);
    SET_W(maze, 5, 0);
    SET_E(maze, 0, 1);
    SET_N(maze, 2, 1);
    SET_N(maze, 3, 1);
    SET_W(maze, 4, 1);
    SET_W(maze, 5, 1);
    SET_E(maze, 0, 2);
    SET_E(maze, 1, 2);
    SET_E(maze, 3, 2);
    SET_N(maze, 4, 2);
    SET_N(maze, 5, 2);
    SET_N(maze, 1, 3);
    SET_E(maze, 1, 3);
    SET_N(maze, 2, 3);
    SET_E(maze, 3, 3);
    SET_N(maze, 1, 4);
    SET_N(maze, 2, 4);
    SET_N(maze, 3, 4);
    SET_E(maze, 4, 4);
    SET_E(maze, 4, 5);
    maze_update_all_wall_codes(maze);
}

void wall_arrangement_10x10(Maze *maze) {
    if (!maze) return;
    // Row 0
    SET_E(maze, 0, 1);
    SET_N(maze, 0, 3);
    SET_W(maze, 0, 4);
    SET_E(maze, 0, 6);
    // Row 1
    SET_E(maze, 1, 0);
    SET_E(maze, 1, 2);
    SET_N(maze, 1, 5);
    SET_W(maze, 1, 6);
    // Row 2
    SET_N(maze, 2, 1);
    SET_E(maze, 2, 3);
    SET_W(maze, 2, 4);
    SET_W(maze, 2, 6);
    // Row 3
    SET_E(maze, 3, 2);
    SET_N(maze, 3, 3);
    SET_N(maze, 3, 4);
    SET_W(maze, 3, 5);
    SET_E(maze, 3, 7);
    // Row 4
    SET_E(maze, 4, 2);
    SET_N(maze, 4, 3);
    SET_N(maze, 4, 4);
    SET_W(maze, 4, 5);
    SET_W(maze, 4, 7);
    // Row 5
    SET_E(maze, 5, 2);
    SET_S(maze, 5, 3);
    SET_S(maze, 5, 4);
    SET_W(maze, 5, 5);
    SET_W(maze, 5, 8);
    // Row 6
    SET_N(maze, 6, 3);
    SET_W(maze, 6, 4);
    SET_E(maze, 6, 6);
    SET_E(maze, 6, 7);
    // Row 7
    SET_N(maze, 7, 1);
    SET_N(maze, 7, 3);
    SET_N(maze, 7, 5);
    SET_W(maze, 7, 8);
    // Row 8
    SET_N(maze, 8, 2);
    SET_E(maze, 8, 4);
    SET_E(maze, 8, 6);
    SET_E(maze, 8, 7);
    // Row 9
    SET_N(maze, 9, 0);
    SET_W(maze, 9, 5);
    SET_N(maze, 9, 8);
    // Guard the center goal cells
    SET_S(maze, 4, 4);
    SET_S(maze, 4, 5);
    SET_N(maze, 5, 4);
    SET_N(maze, 5, 5);
    SET_W(maze, 4, 3);
    SET_E(maze, 4, 6);
    SET_W(maze, 5, 3);
    SET_E(maze, 5, 6);
    maze_update_all_wall_codes(maze);
}

void wall_arrangement_16x16(Maze *maze) {
    if (!maze) return;
    // Column 0
    SET_E(maze, 0, 0);
    SET_E(maze, 0, 1);
    SET_E(maze, 0, 4);
    SET_E(maze, 0, 5);
    SET_E(maze, 0, 6);
    SET_E(maze, 0, 7);
    SET_E(maze, 0, 8);
    SET_E(maze, 0, 9);
    SET_E(maze, 0, 10);
    SET_E(maze, 0, 11);
    SET_E(maze, 0, 14);
    SET_E(maze, 0, 15);
    // Column 1
    SET_E(maze, 1, 1);
    SET_E(maze, 1, 2);
    SET_N(maze, 1, 2);
    SET_E(maze, 1, 3);
    SET_E(maze, 1, 4);
    SET_E(maze, 1, 5);
    SET_E(maze, 1, 6);
    SET_E(maze, 1, 7);
    SET_E(maze, 1, 8);
    SET_E(maze, 1, 9);
    SET_E(maze, 1, 10);
    SET_E(maze, 1, 11);
    SET_E(maze, 1, 12);
    SET_N(maze, 1, 12);
    SET_E(maze, 1, 13);
    SET_E(maze, 1, 14);
    // Column 2
    SET_N(maze, 2, 0);
    SET_N(maze, 2, 1);
    SET_E(maze, 2, 3);
    SET_E(maze, 2, 4);
    SET_E(maze, 2, 5);
    SET_E(maze, 2, 6);
    SET_E(maze, 2, 8);
    SET_E(maze, 2, 9);
    SET_E(maze, 2, 10);
    SET_E(maze, 2, 11);
    SET_E(maze, 2, 12);
    SET_N(maze, 2, 13);
    SET_N(maze, 2, 14);
    // Column 3
    SET_N(maze, 3, 0);
    SET_N(maze, 3, 1);
    SET_N(maze, 3, 2);
    SET_E(maze, 3, 4);
    SET_E(maze, 3, 5);
    SET_E(maze, 3, 6);
    SET_E(maze, 3, 8);
    SET_E(maze, 3, 9);
    SET_E(maze, 3, 10);
    SET_E(maze, 3, 11);
    SET_N(maze, 3, 12);
    SET_N(maze, 3, 13);
    SET_N(maze, 3, 14);
    // Column 4
    SET_N(maze, 4, 1);
    SET_N(maze, 4, 2);
    SET_N(maze, 4, 3);
    SET_N(maze, 4, 4);
    SET_E(maze, 4, 5);
    SET_E(maze, 4, 6);
    SET_E(maze, 4, 8);
    SET_E(maze, 4, 9);
    SET_E(maze, 4, 10);
    SET_N(maze, 4, 11);
    SET_N(maze, 4, 12);
    SET_N(maze, 4, 13);
    SET_N(maze, 4, 14);
    // Column 5
    SET_N(maze, 5, 0);
    SET_N(maze, 5, 1);
    SET_N(maze, 5, 2);
    SET_N(maze, 5, 3);
    SET_N(maze, 5, 4);
    SET_E(maze, 5, 5);
    SET_E(maze, 5, 6);
    SET_E(maze, 5, 8);
    SET_E(maze, 5, 9);
    SET_N(maze, 5, 10);
    SET_N(maze, 5, 11);
    SET_N(maze, 5, 12);
    SET_N(maze, 5, 13);
    SET_N(maze, 5, 14);
    // Column 6
    SET_N(maze, 6, 0);
    SET_N(maze, 6, 1);
    SET_N(maze, 6, 2);
    SET_N(maze, 6, 3);
    SET_N(maze, 6, 4);
    SET_N(maze, 6, 5);
    SET_E(maze, 6, 8);
    SET_N(maze, 6, 9);
    SET_N(maze, 6, 10);
    SET_N(maze, 6, 11);
    SET_N(maze, 6, 12);
    SET_N(maze, 6, 13);
    SET_N(maze, 6, 14);
    // Column 7
    SET_N(maze, 7, 0);
    SET_N(maze, 7, 1);
    SET_E(maze, 7, 1);
    SET_N(maze, 7, 2);
    SET_N(maze, 7, 3);
    SET_N(maze, 7, 4);
    SET_N(maze, 7, 5);
    SET_N(maze, 7, 6);
    SET_N(maze, 7, 8);
    SET_N(maze, 7, 9);
    SET_N(maze, 7, 10);
    SET_E(maze, 7, 10);
    SET_N(maze, 7, 11);
    SET_E(maze, 7, 11);
    SET_N(maze, 7, 12);
    SET_N(maze, 7, 14);
    // Column 8
    SET_N(maze, 8, 0);
    SET_N(maze, 8, 2);
    SET_N(maze, 8, 4);
    SET_N(maze, 8, 6);
    SET_E(maze, 8, 7);
    SET_E(maze, 8, 8);
    SET_N(maze, 8, 8);
    SET_N(maze, 8, 9);
    SET_N(maze, 8, 10);
    SET_N(maze, 8, 11);
    SET_N(maze, 8, 12);
    SET_N(maze, 8, 13);
    SET_N(maze, 8, 14);
    // Column 9
    SET_N(maze, 9, 0);
    SET_N(maze, 9, 1);
    SET_N(maze, 9, 2);
    SET_N(maze, 9, 3);
    SET_N(maze, 9, 4);
    SET_N(maze, 9, 5);
    SET_E(maze, 9, 6);
    SET_E(maze, 9, 7);
    SET_E(maze, 9, 8);
    SET_E(maze, 9, 9);
    SET_N(maze, 9, 9);
    SET_N(maze, 9, 10);
    SET_N(maze, 9, 11);
    SET_N(maze, 9, 12);
    SET_N(maze, 9, 13);
    // Column 10
    SET_N(maze, 10, 0);
    SET_N(maze, 10, 1);
    SET_N(maze, 10, 2);
    SET_N(maze, 10, 3);
    SET_N(maze, 10, 4);
    SET_E(maze, 10, 5);
    SET_E(maze, 10, 6);
    SET_E(maze, 10, 8);
    SET_E(maze, 10, 9);
    SET_E(maze, 10, 10);
    SET_N(maze, 10, 10);
    SET_N(maze, 10, 11);
    SET_E(maze, 10, 13);
    SET_N(maze, 10, 13);
    SET_N(maze, 10, 14);
    // Column 11
    SET_N(maze, 11, 0);
    SET_N(maze, 11, 1);
    SET_N(maze, 11, 2);
    SET_N(maze, 11, 3);
    SET_E(maze, 11, 4);
    SET_E(maze, 11, 5);
    SET_E(maze, 11, 6);
    SET_E(maze, 11, 7);
    SET_E(maze, 11, 8);
    SET_E(maze, 11, 10);
    SET_E(maze, 11, 11);
    SET_N(maze, 11, 11);
    SET_N(maze, 11, 12);
    SET_N(maze, 11, 14);
    // Column 12
    SET_N(maze, 12, 0);
    SET_N(maze, 12, 1);
    SET_N(maze, 12, 2);
    SET_E(maze, 12, 2);
    SET_E(maze, 12, 3);
    SET_E(maze, 12, 4);
    SET_E(maze, 12, 5);
    SET_E(maze, 12, 6);
    SET_E(maze, 12, 7);
    SET_E(maze, 12, 8);
    SET_E(maze, 12, 9);
    SET_E(maze, 12, 10);
    SET_E(maze, 12, 11);
    SET_N(maze, 12, 11);
    SET_E(maze, 12, 12);
    SET_N(maze, 12, 12);
    SET_N(maze, 12, 13);
    // Column 13
    SET_N(maze, 13, 0);
    SET_N(maze, 13, 1);
    SET_E(maze, 13, 2);
    SET_E(maze, 13, 3);
    SET_E(maze, 13, 4);
    SET_E(maze, 13, 5);
    SET_E(maze, 13, 7);
    SET_E(maze, 13, 8);
    SET_E(maze, 13, 9);
    SET_E(maze, 13, 10);
    SET_E(maze, 13, 11);
    SET_E(maze, 13, 12);
    SET_E(maze, 13, 13);
    SET_N(maze, 13, 13);
    SET_N(maze, 13, 14);
    // Column 14
    SET_N(maze, 14, 0);
    SET_N(maze, 14, 1);
    SET_E(maze, 14, 2);
    SET_E(maze, 14, 3);
    SET_E(maze, 14, 5);
    SET_E(maze, 14, 6);
    SET_E(maze, 14, 7);
    SET_E(maze, 14, 8);
    SET_E(maze, 14, 9);
    SET_E(maze, 14, 10);
    SET_E(maze, 14, 11);
    SET_E(maze, 14, 12);
    SET_E(maze, 14, 13);
    SET_E(maze, 14, 14);
    SET_N(maze, 14, 14);
    // Unparsed: PRESET_CONFIGURATIONS = {
    // Unparsed: 5: wall_arrangement_x5,
    // Unparsed: 6: wall_arrangement_x6,
    // Unparsed: 10: wall_arrangement_10x10,
    // Unparsed: 16: wall_arrangement_16x16,
    // Unparsed: }
    maze_update_all_wall_codes(maze);
}

Maze* build_preset_maze(int size) {
    Maze *maze = maze_create_empty(size);
    if (!maze) return NULL;

    switch (size) {
        case 5:
            wall_arrangement_5x5(maze);
            break;
        case 6:
            wall_arrangement_6x6(maze);
            break;
        case 10:
            wall_arrangement_10x10(maze);
            break;
        case 16:
            wall_arrangement_16x16(maze);
            break;
        default:
            maze_destroy(maze);
            return NULL;
    }
    return maze;
}
