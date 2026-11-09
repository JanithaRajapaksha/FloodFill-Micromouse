#include "mazes.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define SET_N(m, x, y) maze_map_set_wall((m), (x), (y), DIR_NORTH)
#define SET_S(m, x, y) maze_map_set_wall((m), (x), (y), DIR_SOUTH)
#define SET_E(m, x, y) maze_map_set_wall((m), (x), (y), DIR_EAST)
#define SET_W(m, x, y) maze_map_set_wall((m), (x), (y), DIR_WEST)

bool maze_map_load_num_file(MazeMap *map, const char *filepath) {
    if (!map || !filepath) return false;

    FILE *f = fopen(filepath, "r");
    if (!f) return false;

    // Scan lines to determine bounds
    char line[128];
    int max_x = 0;
    int max_y = 0;

    while (fgets(line, sizeof(line), f)) {
        int x, y, n, e, s, w;
        if (sscanf(line, "%d %d %d %d %d %d", &x, &y, &n, &e, &s, &w) == 6) {
            if (x > max_x) max_x = x;
            if (y > max_y) max_y = y;
        }
    }

    uint8_t size_x = (uint8_t)(max_x + 1);
    uint8_t size_y = (uint8_t)(max_y + 1);
    maze_map_init_empty(map, size_x, size_y);

    rewind(f);
    while (fgets(line, sizeof(line), f)) {
        int x, y, n, e, s, w;
        if (sscanf(line, "%d %d %d %d %d %d", &x, &y, &n, &e, &s, &w) == 6) {
            if (n) SET_N(map, (uint8_t)x, (uint8_t)y);
            if (e) SET_E(map, (uint8_t)x, (uint8_t)y);
            if (s) SET_S(map, (uint8_t)x, (uint8_t)y);
            if (w) SET_W(map, (uint8_t)x, (uint8_t)y);
        }
    }

    fclose(f);
    return true;
}

bool maze_map_load_preset(MazeMap *map, const char *preset_name) {
    if (!map || !preset_name) return false;

    char filename[64];
    if (strstr(preset_name, ".num")) {
        snprintf(filename, sizeof(filename), "%s", preset_name);
    } else {
        snprintf(filename, sizeof(filename), "%s.num", preset_name);
    }

    const char *search_paths[] = {
        filename,
        "mazes/",
        "../mazes/",
        "mms_implementations/mazes/",
        "../../mms_implementations/mazes/"
    };

    char full_path[256];
    for (size_t i = 0; i < sizeof(search_paths)/sizeof(search_paths[0]); ++i) {
        if (i == 0) {
            snprintf(full_path, sizeof(full_path), "%s", filename);
        } else {
            snprintf(full_path, sizeof(full_path), "%s%s", search_paths[i], filename);
        }
        if (maze_map_load_num_file(map, full_path)) {
            return true;
        }
    }

    return false;
}

void wall_arrangement_5x5(MazeMap *map) {
    if (!map) return;
    SET_E(map, 0, 0);
    SET_N(map, 2, 0);
    SET_E(map, 2, 0);
    SET_N(map, 3, 0);
    SET_N(map, 2, 1);
    SET_E(map, 2, 1);
    SET_S(map, 0, 2);
    SET_E(map, 0, 2);
    SET_E(map, 1, 2);
    SET_N(map, 3, 2);
    SET_E(map, 3, 2);
    SET_N(map, 0, 3);
    SET_E(map, 1, 4);
    SET_S(map, 3, 4);
    SET_S(map, 4, 4);
}

void wall_arrangement_6x6(MazeMap *map) {
    if (!map) return;
    SET_N(map, 2, 0);
    SET_N(map, 3, 0);
    SET_E(map, 4, 0);
    SET_W(map, 5, 0);
    SET_E(map, 0, 1);
    SET_N(map, 2, 1);
    SET_N(map, 3, 1);
    SET_W(map, 4, 1);
    SET_W(map, 5, 1);
    SET_E(map, 0, 2);
    SET_E(map, 1, 2);
    SET_E(map, 3, 2);
    SET_N(map, 4, 2);
    SET_N(map, 5, 2);
    SET_N(map, 1, 3);
    SET_E(map, 1, 3);
    SET_N(map, 2, 3);
    SET_E(map, 3, 3);
    SET_N(map, 1, 4);
    SET_N(map, 2, 4);
    SET_N(map, 3, 4);
    SET_E(map, 4, 4);
    SET_E(map, 4, 5);
}

void wall_arrangement_10x10(MazeMap *map) {
    if (!map) return;
    // Row 0
    SET_E(map, 0, 1);
    SET_N(map, 0, 3);
    SET_W(map, 0, 4);
    SET_E(map, 0, 6);

    // Row 1
    SET_E(map, 1, 0);
    SET_E(map, 1, 2);
    SET_N(map, 1, 5);
    SET_W(map, 1, 6);

    // Row 2
    SET_N(map, 2, 1);
    SET_E(map, 2, 3);
    SET_W(map, 2, 4);
    SET_W(map, 2, 6);

    // Row 3
    SET_E(map, 3, 2);
    SET_N(map, 3, 3);
    SET_N(map, 3, 4);
    SET_W(map, 3, 5);
    SET_E(map, 3, 7);

    // Row 4
    SET_E(map, 4, 2);
    SET_N(map, 4, 3);
    SET_N(map, 4, 4);
    SET_W(map, 4, 5);
    SET_W(map, 4, 7);

    // Row 5
    SET_E(map, 5, 2);
    SET_S(map, 5, 3);
    SET_S(map, 5, 4);
    SET_W(map, 5, 5);
    SET_W(map, 5, 8);

    // Row 6
    SET_N(map, 6, 3);
    SET_W(map, 6, 4);
    SET_W(map, 6, 5);
    SET_E(map, 6, 8);

    // Row 7
    SET_N(map, 7, 0);
    SET_E(map, 7, 1);
    SET_N(map, 7, 2);
    SET_N(map, 7, 3);
    SET_E(map, 7, 5);
    SET_E(map, 7, 6);
    SET_E(map, 7, 8);

    // Row 8
    SET_N(map, 8, 1);
    SET_E(map, 8, 2);
    SET_N(map, 8, 6);
    SET_E(map, 8, 7);
    SET_N(map, 8, 8);

    // Row 9
    SET_E(map, 9, 1);
    SET_E(map, 9, 2);
    SET_E(map, 9, 4);
    SET_E(map, 9, 6);
    SET_E(map, 9, 7);
    SET_E(map, 9, 8);
}

bool build_preset_maze(MazeMap *map, uint8_t size) {
    if (!map) return false;

    if (size == 5) {
        maze_map_init_empty(map, 5, 5);
        wall_arrangement_5x5(map);
        return true;
    } else if (size == 6) {
        maze_map_init_empty(map, 6, 6);
        wall_arrangement_6x6(map);
        return true;
    } else if (size == 10) {
        maze_map_init_empty(map, 10, 10);
        wall_arrangement_10x10(map);
        return true;
    } else if (size == 16) {
        return maze_map_load_preset(map, "example1");
    }

    return false;
}
