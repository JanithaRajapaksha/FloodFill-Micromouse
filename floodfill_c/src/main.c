#include <stdio.h>
#include "maze.h"
#include "mouse.h"
#include "floodfill.h"
#include "mazes.h"

int main(void) {
    const int maze_size = 10;
    Maze *maze = build_preset_maze(maze_size);
    if (!maze) {
        fprintf(stderr, "Failed to create maze of size %d\n", maze_size);
        return 1;
    }

    // Initial flood fill from center goals
    Cell *centers[4];
    int num_centers = maze_get_centers(maze, centers);
    flood_fill(maze, centers, num_centers);

    Mouse mouse;
    mouse_init(&mouse, 0, 0, DIR_NORTH);

    Path *path = navigate(&mouse, maze, true);

    path_destroy(path);
    maze_destroy(maze);
    return 0;
}

