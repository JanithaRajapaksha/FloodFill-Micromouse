#ifndef NAVIGATOR_H
#define NAVIGATOR_H

#include <stdint.h>
#include <stdbool.h>
#include "maze_map.h"

typedef enum {
    NAV_CMD_STOP = 0,         // Reached goal destination or halted
    NAV_CMD_MOVE_FORWARD,     // Continue straight into next cell
    NAV_CMD_TURN_LEFT,        // Turn 90 degrees CCW and advance
    NAV_CMD_TURN_RIGHT,       // Turn 90 degrees CW and advance
    NAV_CMD_TURN_AROUND,      // Turn 180 degrees and advance
    NAV_CMD_COUNT
} NavCommand;

typedef enum {
    NAV_STATE_SEARCHING = 0,
    NAV_STATE_GOAL_REACHED,
    NAV_STATE_NO_PATH,
    NAV_STATE_CRASHED
} NavState;

typedef struct {
    uint8_t x;
    uint8_t y;
    Direction orientation;
    NavState state;
    MazeMap map;
} Navigator;

void navigator_init(
    Navigator *nav,
    uint8_t size_x,
    uint8_t size_y,
    uint8_t start_x,
    uint8_t start_y,
    Direction start_dir
);

/**
 * Executes one blind exploration step using the official MMS API:
 * 1. Queries walls around the current cell.
 * 2. Updates discovered maze and MMS visualization.
 * 3. Solves flood-fill distance gradient.
 * 4. Checks goal condition.
 * 5. Turns and steps forward in MMS.
 * Returns the executed NavCommand.
 */
NavCommand navigator_step_mms(Navigator *nav);

const char* nav_command_to_string(NavCommand cmd);

#endif /* NAVIGATOR_H */
