#include "mazes.h"
#include <stdio.h>
#include <string.h>

/* ============================================================================
 * Compact Bitmask Preset Definitions
 * Each 16x16 maze is compressed to 68 bytes (17 h_walls + 17 v_walls uint16_t).
 * Each bit directly represents a wall segment, guaranteeing wall symmetry.
 * ============================================================================ */

static const CompactMaze PRESET_COMPACT_5x5 = {
    5, 5,
    { 0x1f, 0xc, 0x5, 0x8, 0x19, 0x1f },
    { 0x1f, 0x5, 0x14, 0x3, 0x4, 0x1f }
};

static const CompactMaze PRESET_COMPACT_6x6 = {
    6, 6,
    { 0x3f, 0xc, 0xc, 0x30, 0x6, 0xe, 0x3f },
    { 0x3f, 0x6, 0xc, 0x0, 0xe, 0x33, 0x3f }
};

static const CompactMaze PRESET_COMPACT_10x10 = {
    10, 10,
    { 0x3ff, 0x200, 0x84, 0x120, 0xf9, 0x38, 0xa2, 0x0, 0x0, 0x200, 0x3ff },
    { 0x3ff, 0x42, 0x55, 0x28, 0xac, 0x16c, 0x54, 0x1c0, 0x0, 0xf0, 0x3ff }
};

static const CompactMaze PRESET_COMPACT_16x16 = {
    16, 16,
    { 0xffff, 0x7fec, 0x7efc, 0x1ffa, 0xef0, 0x7f0, 0x2c0, 0x180, 0x0, 0x180, 0x3c0, 0x7e0, 0x1ff0, 0x1bfa, 0x377c, 0x6dfc, 0xffff },
    { 0xffff, 0xcff3, 0x7ffe, 0x1f78, 0xf70, 0x760, 0x360, 0x100, 0xc02, 0x180, 0x3c0, 0x2760, 0xdf0, 0x1ffc, 0x3fbc, 0x7fec, 0xffff }
};

static const CompactMaze PRESET_COMPACT_BLANK = {
    16, 16,
    { 0xffff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xffff },
    { 0xffff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xffff }
};

static const CompactMaze PRESET_COMPACT_EXAMPLE2 = {
    16, 16,
    { 0xffff, 0x23cd, 0x3020, 0x7b56, 0x36ea, 0xe174, 0x6280, 0x35cc, 0xe220, 0x61d6, 0x373b, 0x7ed6, 0x79a0, 0x8818, 0x1080, 0x237c, 0xffff },
    { 0xffff, 0xf1e4, 0x70d2, 0x2f2c, 0x58d6, 0x21ea, 0x3844, 0x53a4, 0x240c, 0x38d2, 0x7126, 0xe3de, 0x47f3, 0x2000, 0x7002, 0x664e, 0xffff }
};

static const CompactMaze PRESET_COMPACT_EXAMPLE3 = {
    16, 16,
    { 0xffff, 0x7f7c, 0x177c, 0x2b01, 0x1500, 0x2a80, 0x2440, 0xba0, 0x3c50, 0x1be6, 0x7717, 0x398e, 0x68c4, 0x37e2, 0x7ba4, 0x7f92, 0xffff },
    { 0xffff, 0x79eb, 0xdc, 0xf3f8, 0x7ffc, 0x1c78, 0xcebc, 0x75c, 0x28, 0x15a0, 0x2950, 0xe28, 0x10d6, 0x48, 0x354, 0x3ffe, 0xffff }
};

static const CompactMaze PRESET_COMPACT_EXAMPLE4 = {
    16, 16,
    { 0xffff, 0xa50c, 0x588a, 0x6624, 0x400c, 0x73c6, 0x64a2, 0x905, 0x7205, 0xa5dd, 0x21ad, 0x43d4, 0x2514, 0x1218, 0x1830, 0x73e, 0xffff },
    { 0xffff, 0x3879, 0x7004, 0x2dd8, 0x9e6, 0x17de, 0x7cb6, 0x519a, 0x205c, 0x51ae, 0x2b76, 0x54d8, 0x4db6, 0x4b68, 0x548c, 0x7a40, 0xffff }
};

static const CompactMaze PRESET_COMPACT_EXAMPLE5 = {
    16, 16,
    { 0xffff, 0x4e54, 0xa828, 0x54f0, 0x2828, 0x5678, 0x7c00, 0x380, 0xfc77, 0x16fe, 0x3930, 0x589f, 0x287c, 0x6a0a, 0xacfa, 0x6c6a, 0xffff },
    { 0xffff, 0x727f, 0x147e, 0x2fa, 0xa265, 0x10ca, 0x2c60, 0x55d6, 0xfa7b, 0x7dfa, 0x2e4e, 0x7254, 0x289, 0x856, 0x76aa, 0xd54, 0xffff }
};

/* ============================================================================
 * Unpacking Implementation
 * ============================================================================ */

void compact_maze_apply(const CompactMaze *cm, MazeMap *map) {
    if (!cm || !map) return;

    maze_map_init(map, cm->width);

    for (uint8_t y = 0; y < cm->height; y++) {
        for (uint8_t x = 0; x < cm->width; x++) {
            if (cm->h_walls[y + 1] & (1U << x)) {
                maze_map_set_wall(map, x, y, DIR_NORTH);
            }
            if (cm->h_walls[y] & (1U << x)) {
                maze_map_set_wall(map, x, y, DIR_SOUTH);
            }
            if (cm->v_walls[x + 1] & (1U << y)) {
                maze_map_set_wall(map, x, y, DIR_EAST);
            }
            if (cm->v_walls[x] & (1U << y)) {
                maze_map_set_wall(map, x, y, DIR_WEST);
            }
        }
    }
}

/* ============================================================================
 * Preset Wrappers (100% Backward Compatible)
 * ============================================================================ */

void wall_arrangement_5x5(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_5x5, map);
}

void wall_arrangement_6x6(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_6x6, map);
}

void wall_arrangement_10x10(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_10x10, map);
}

void wall_arrangement_16x16(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_16x16, map);
}

void wall_arrangement_blank(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_BLANK, map);
}

void wall_arrangement_example1(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_16x16, map);
}

void wall_arrangement_example2(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_EXAMPLE2, map);
}

void wall_arrangement_example3(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_EXAMPLE3, map);
}

void wall_arrangement_example4(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_EXAMPLE4, map);
}

void wall_arrangement_example5(MazeMap *map) {
    compact_maze_apply(&PRESET_COMPACT_EXAMPLE5, map);
}

bool build_preset_maze(MazeMap *map, uint8_t size) {
    if (!map) return false;
    switch (size) {
        case 5:
            wall_arrangement_5x5(map);
            return true;
        case 6:
            wall_arrangement_6x6(map);
            return true;
        case 10:
            wall_arrangement_10x10(map);
            return true;
        case 16:
            wall_arrangement_16x16(map);
            return true;
        default:
            return false;
    }
}

bool build_preset_mms_maze(MazeMap *map, const char *name) {
    if (!map || !name) return false;
    if (strcmp(name, "example1") == 0 || strcmp(name, "16") == 0) {
        wall_arrangement_example1(map);
        return true;
    } else if (strcmp(name, "example2") == 0) {
        wall_arrangement_example2(map);
        return true;
    } else if (strcmp(name, "example3") == 0) {
        wall_arrangement_example3(map);
        return true;
    } else if (strcmp(name, "example4") == 0) {
        wall_arrangement_example4(map);
        return true;
    } else if (strcmp(name, "example5") == 0) {
        wall_arrangement_example5(map);
        return true;
    } else if (strcmp(name, "blank") == 0) {
        wall_arrangement_blank(map);
        return true;
    }
    return false;
}

/* ============================================================================
 * File Loaders: .num (Text) and .bin (Compact Binary)
 * ============================================================================ */

bool maze_map_load_num_file(MazeMap *map, const char *filepath) {
    if (!map || !filepath) return false;

    FILE *f = fopen(filepath, "r");
    if (!f) return false;

    maze_map_init(map, 16);

    char line[128];
    while (fgets(line, sizeof(line), f)) {
        int x, y, n, e, s, w;
        int d, has_wall;
        if (sscanf(line, "%d %d %d %d %d %d", &x, &y, &n, &e, &s, &w) == 6) {
            if (x >= 0 && x < 16 && y >= 0 && y < 16) {
                if (n) maze_map_set_wall(map, (uint8_t)x, (uint8_t)y, DIR_NORTH);
                if (e) maze_map_set_wall(map, (uint8_t)x, (uint8_t)y, DIR_EAST);
                if (s) maze_map_set_wall(map, (uint8_t)x, (uint8_t)y, DIR_SOUTH);
                if (w) maze_map_set_wall(map, (uint8_t)x, (uint8_t)y, DIR_WEST);
            }
        } else if (sscanf(line, "%d %d %d %d", &x, &y, &d, &has_wall) == 4) {
            if (x >= 0 && x < 16 && y >= 0 && y < 16 && has_wall) {
                Direction dir;
                switch (d) {
                    case 0: dir = DIR_NORTH; break;
                    case 1: dir = DIR_EAST;  break;
                    case 2: dir = DIR_SOUTH; break;
                    case 3: dir = DIR_WEST;  break;
                    default: continue;
                }
                maze_map_set_wall(map, (uint8_t)x, (uint8_t)y, dir);
            }
        }
    }

    fclose(f);
    return true;
}

bool maze_map_load_bin_file(MazeMap *map, const char *filepath) {
    if (!map || !filepath) return false;

    FILE *f = fopen(filepath, "rb");
    if (!f) return false;

    uint8_t w, h;
    if (fread(&w, 1, 1, f) != 1 || fread(&h, 1, 1, f) != 1) {
        fclose(f);
        return false;
    }
    if (w > 16 || h > 16 || w == 0 || h == 0) {
        fclose(f);
        return false;
    }

    CompactMaze cm;
    memset(&cm, 0, sizeof(cm));
    cm.width = w;
    cm.height = h;

    size_t h_count = h + 1;
    size_t v_count = w + 1;

    if (fread(cm.h_walls, sizeof(uint16_t), h_count, f) != h_count ||
        fread(cm.v_walls, sizeof(uint16_t), v_count, f) != v_count) {
        fclose(f);
        return false;
    }

    fclose(f);
    compact_maze_apply(&cm, map);
    return true;
}

bool maze_map_save_bin_file(const MazeMap *map, const char *filepath) {
    if (!map || !filepath) return false;

    uint8_t size = map->size;
    if (size > 16 || size == 0) return false;

    CompactMaze cm;
    memset(&cm, 0, sizeof(cm));
    cm.width = size;
    cm.height = size;

    for (uint8_t y = 0; y < size; y++) {
        for (uint8_t x = 0; x < size; x++) {
            if (maze_map_has_wall(map, x, y, DIR_NORTH)) cm.h_walls[y + 1] |= (1U << x);
            if (maze_map_has_wall(map, x, y, DIR_SOUTH)) cm.h_walls[y]     |= (1U << x);
            if (maze_map_has_wall(map, x, y, DIR_EAST))  cm.v_walls[x + 1] |= (1U << y);
            if (maze_map_has_wall(map, x, y, DIR_WEST))  cm.v_walls[x]     |= (1U << y);
        }
    }

    FILE *f = fopen(filepath, "wb");
    if (!f) return false;

    fwrite(&size, 1, 1, f);
    fwrite(&size, 1, 1, f);
    fwrite(cm.h_walls, sizeof(uint16_t), size + 1, f);
    fwrite(cm.v_walls, sizeof(uint16_t), size + 1, f);
    fclose(f);
    return true;
}
