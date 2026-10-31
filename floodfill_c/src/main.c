#include <stdio.h>
#include "maze_map.h"
#include "floodfill_core.h"
#include "sensor_interface.h"
#include "navigator.h"
#include "motor_controller.h"
#include "mazes.h"

int main(void) {
    const uint8_t maze_size = 10;

    // Ground-truth environment representation (for simulation)
    MazeMap ground_truth;
    if (!build_preset_maze(&ground_truth, maze_size)) {
        fprintf(stderr, "Failed to initialize preset maze\n");
        return 1;
    }

    // Initial flood fill on ground truth from center goal cells
    uint8_t centers_x[4];
    uint8_t centers_y[4];
    uint8_t num_centers = maze_map_get_centers(&ground_truth, centers_x, centers_y);
    floodfill_compute(&ground_truth, centers_x, centers_y, num_centers);

    // Embedded navigation and motor controller modules
    Navigator nav;
    navigator_init(&nav, maze_size, 0, 0, DIR_NORTH);

    MotorController motor;
    motor_controller_init(&motor, NULL);

    while (true) {
        // 1. Proximity sensors observe environment around current robot pose
        bool f = maze_map_has_wall(&ground_truth, nav.x, nav.y, nav.orientation);
        bool l = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 3U) % 4U));
        bool r = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 1U) % 4U));

        // 2. Standardized sensor data interface
        ProximitySensorArray sensors = sensor_make_binary(f, l, r);
        DetectedWalls walls = sensor_interface_evaluate(&sensors);

        // 3. Navigation decision engine determines next action
        NavCommand cmd = navigator_step(&nav, &walls);

        // 4. Motor controller translates decision into actuation commands
        MotorCommand m_cmd = motor_controller_translate(&motor, cmd);
        (void)m_cmd; // Motor command ready for HAL driver dispatch

        if (cmd == NAV_CMD_STOP) {
            printf("Goal reached at (%d, %d)!\n", nav.x, nav.y);
            break;
        }

        // Print step in canonical format
        printf("( %d ,  %d )    %d\n", nav.x, nav.y, (int)nav.orientation);
    }

    return 0;
}
