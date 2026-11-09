#include "navigator.h"
#include "floodfill_core.h"
#include "API.h"
#include <stdio.h>

void navigator_init(
    Navigator *nav,
    uint8_t size_x,
    uint8_t size_y,
    uint8_t start_x,
    uint8_t start_y,
    Direction start_dir
) {
    if (!nav) return;
    nav->x = start_x;
    nav->y = start_y;
    nav->orientation = start_dir;
    nav->state = NAV_STATE_SEARCHING;
    maze_map_init_empty(&nav->map, size_x, size_y);
}

NavCommand navigator_step_mms(Navigator *nav) {
    if (!nav) return NAV_CMD_STOP;

    // 1. Mark current cell as visited in internal map and color it in MMS
    maze_map_set_visited(&nav->map, nav->x, nav->y);
    API_setColor(nav->x, nav->y, 'a'); // 'a' = Gray explored trail

    // 2. Query walls through official MMS API
    bool wall_front = API_wallFront();
    bool wall_left  = API_wallLeft();
    bool wall_right = API_wallRight();

    Direction front_dir = nav->orientation;
    Direction left_dir  = (Direction)((nav->orientation + 3U) % 4U);
    Direction right_dir = (Direction)((nav->orientation + 1U) % 4U);

    if (wall_front) {
        maze_map_set_wall(&nav->map, nav->x, nav->y, front_dir);
        API_setWall(nav->x, nav->y, direction_to_char(front_dir));
    }
    if (wall_left) {
        maze_map_set_wall(&nav->map, nav->x, nav->y, left_dir);
        API_setWall(nav->x, nav->y, direction_to_char(left_dir));
    }
    if (wall_right) {
        maze_map_set_wall(&nav->map, nav->x, nav->y, right_dir);
        API_setWall(nav->x, nav->y, direction_to_char(right_dir));
    }

    // 3. Compute flood-fill distance gradient from goals
    uint8_t goal_x[4];
    uint8_t goal_y[4];
    uint8_t num_goals = maze_map_get_centers(&nav->map, goal_x, goal_y);

    for (uint8_t i = 0; i < num_goals; ++i) {
        API_setColor(goal_x[i], goal_y[i], 'G'); // 'G' = Dark Green for goal
    }

    floodfill_compute(&nav->map, goal_x, goal_y, num_goals);

    // Update text on current cell with flood-fill distance
    uint16_t cur_idx = maze_cell_index(nav->map.size_x, nav->map.size_y, nav->x, nav->y);
    uint16_t cur_dist = nav->map.distances[cur_idx];
    char dist_str[16];
    snprintf(dist_str, sizeof(dist_str), "%u", cur_dist);
    API_setText(nav->x, nav->y, dist_str);

    // 4. Check if goal is reached
    if (cur_dist == 0) {
        nav->state = NAV_STATE_GOAL_REACHED;
        API_setColor(nav->x, nav->y, 'g'); // 'g' = Green on goal reached
        return NAV_CMD_STOP;
    }

    // 5. Find next cell along distance gradient (cur_dist - 1)
    uint8_t next_x = 0;
    uint8_t next_y = 0;
    Direction next_dir = DIR_NORTH;

    bool found = floodfill_get_next_cell(
        &nav->map, nav->x, nav->y,
        &next_x, &next_y, &next_dir
    );

    if (!found) {
        // Fallback for dead end / local minimum: flood fill from current cell
        uint8_t cur_x_arr[1] = { nav->x };
        uint8_t cur_y_arr[1] = { nav->y };
        floodfill_compute(&nav->map, cur_x_arr, cur_y_arr, 1);

        found = floodfill_get_next_cell(
            &nav->map, nav->x, nav->y,
            &next_x, &next_y, &next_dir
        );

        if (!found) {
            nav->state = NAV_STATE_NO_PATH;
            return NAV_CMD_STOP;
        }
    }

    // 6. Determine physical turn and movement
    uint8_t turn = (uint8_t)((next_dir - nav->orientation + 4U) % 4U);
    NavCommand cmd = NAV_CMD_MOVE_FORWARD;

    switch (turn) {
        case 0:
            cmd = NAV_CMD_MOVE_FORWARD;
            break;
        case 1:
            cmd = NAV_CMD_TURN_RIGHT;
            break;
        case 2:
            cmd = NAV_CMD_TURN_AROUND;
            break;
        case 3:
            cmd = NAV_CMD_TURN_LEFT;
            break;
        default:
            cmd = NAV_CMD_MOVE_FORWARD;
            break;
    }

    static const char* DIR_NAMES[4] = {"NORTH", "EAST", "SOUTH", "WEST"};
    fprintf(stderr, "[STEP] Pos: (%2d, %2d) %-5s | Dist: %2u | Walls: [F:%s L:%s R:%s] -> %-12s Target: (%2d, %2d)\n",
            nav->x, nav->y, DIR_NAMES[nav->orientation],
            cur_dist,
            wall_front ? "YES" : "no ",
            wall_left  ? "YES" : "no ",
            wall_right ? "YES" : "no ",
            nav_command_to_string(cmd),
            next_x, next_y);
    fflush(stderr);

    // Actuate turns
    if (turn == 1) {
        API_turnRight();
    } else if (turn == 2) {
        API_turnRight();
        API_turnRight();
    } else if (turn == 3) {
        API_turnLeft();
    }

    // 7. Advance one step in MMS
    int success = API_moveForward();
    if (!success) {
        fprintf(stderr, "[ERROR] Mouse crashed moving to (%d, %d)\n", next_x, next_y);
        nav->state = NAV_STATE_CRASHED;
        return NAV_CMD_STOP;
    }

    // 8. Update navigator pose
    nav->orientation = next_dir;
    nav->x = next_x;
    nav->y = next_y;

    return cmd;
}

const char* nav_command_to_string(NavCommand cmd) {
    switch (cmd) {
        case NAV_CMD_STOP:         return "STOP";
        case NAV_CMD_MOVE_FORWARD: return "MOVE_FORWARD";
        case NAV_CMD_TURN_LEFT:    return "TURN_LEFT";
        case NAV_CMD_TURN_RIGHT:   return "TURN_RIGHT";
        case NAV_CMD_TURN_AROUND:  return "TURN_AROUND";
        default:                   return "UNKNOWN";
    }
}
