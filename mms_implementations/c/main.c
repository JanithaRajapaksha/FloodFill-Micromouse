#include <stdio.h>
#include <stdbool.h>
#include "API.h"
#include "navigator.h"

int main(void) {
    fprintf(stderr, "=== MMS Micromouse C Flood-Fill Solver Started ===\n");

    int width = API_mazeWidth();
    int height = API_mazeHeight();

    if (width <= 0) width = 16;
    if (height <= 0) height = 16;

    fprintf(stderr, "[INFO] Maze dimensions reported: %d x %d\n", width, height);

    Navigator nav;
    navigator_init(&nav, (uint8_t)width, (uint8_t)height, 0, 0, DIR_NORTH);

    // Initial visualization for start tile
    API_setColor(0, 0, 'c'); // 'c' = Cyan start
    API_setText(0, 0, "start");

    uint32_t step_count = 0;

    while (true) {
        // 1. Check if user pressed the simulator Reset button
        if (API_wasReset()) {
            fprintf(stderr, "[RESET] Simulator reset acknowledged. Reinitializing state...\n");
            fflush(stderr);
            API_ackReset();
            API_clearAllColor();
            API_clearAllText();
            navigator_init(&nav, (uint8_t)width, (uint8_t)height, 0, 0, DIR_NORTH);
            API_setColor(0, 0, 'c');
            API_setText(0, 0, "start");
            step_count = 0;
            continue;
        }

        // 2. Perform blind exploration step
        NavCommand cmd = navigator_step_mms(&nav);
        step_count++;

        // 3. Handle termination conditions
        if (nav.state == NAV_STATE_GOAL_REACHED) {
            fprintf(stderr, "[SUCCESS] Center goal reached at (%d, %d) in %u steps!\n", nav.x, nav.y, step_count);
            fflush(stderr);
            break;
        }

        if (nav.state == NAV_STATE_NO_PATH) {
            fprintf(stderr, "[FAIL] No path to goal exists. Exploration halted.\n");
            break;
        }

        if (nav.state == NAV_STATE_CRASHED) {
            fprintf(stderr, "[FAIL] Collision detected. Exploration halted.\n");
            break;
        }

        if (cmd == NAV_CMD_STOP) {
            fprintf(stderr, "[INFO] Navigator issued STOP command.\n");
            break;
        }
    }

    fprintf(stderr, "=== MMS Micromouse C Solver Finished ===\n");
    return 0;
}
