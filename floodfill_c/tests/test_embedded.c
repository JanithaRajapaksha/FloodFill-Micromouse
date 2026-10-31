#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include "maze_map.h"
#include "floodfill_core.h"
#include "sensor_interface.h"
#include "navigator.h"
#include "motor_controller.h"
#include "mazes.h"

static int g_tests_run = 0;
static int g_tests_failed = 0;

#define TEST_ASSERT(cond, msg) do { \
    g_tests_run++; \
    if (!(cond)) { \
        printf("FAILED: %s (line %d): %s\n", __func__, __LINE__, msg); \
        g_tests_failed++; \
        return; \
    } \
} while (0)

static void test_static_memory_footprint(void) {
    size_t map_size = sizeof(MazeMap);
    size_t nav_size = sizeof(Navigator);
    size_t sensor_size = sizeof(ProximitySensorArray);
    size_t motor_size = sizeof(MotorCommand);

    printf("  [Memory Check] sizeof(MazeMap):              %zu bytes\n", map_size);
    printf("  [Memory Check] sizeof(Navigator):            %zu bytes\n", nav_size);
    printf("  [Memory Check] sizeof(ProximitySensorArray): %zu bytes\n", sensor_size);
    printf("  [Memory Check] sizeof(MotorCommand):         %zu bytes\n", motor_size);

    TEST_ASSERT(map_size <= 600, "MazeMap must be under 600 bytes for MCU suitability");
    TEST_ASSERT(nav_size <= 600, "Navigator must be under 600 bytes for MCU suitability");
    printf("PASS: test_static_memory_footprint\n");
}

static void test_maze_map_and_reciprocal_walls(void) {
    MazeMap map;
    maze_map_init(&map, 5);

    TEST_ASSERT(!maze_map_has_wall(&map, 1, 1, DIR_NORTH), "Initial wall must be clear");
    TEST_ASSERT(!maze_map_has_wall(&map, 1, 2, DIR_SOUTH), "Initial wall must be clear");

    maze_map_set_wall(&map, 1, 1, DIR_NORTH);
    TEST_ASSERT(maze_map_has_wall(&map, 1, 1, DIR_NORTH), "North wall should be set");
    TEST_ASSERT(maze_map_has_wall(&map, 1, 2, DIR_SOUTH), "Reciprocal South wall should be set");

    maze_map_set_wall(&map, 1, 1, DIR_EAST);
    TEST_ASSERT(maze_map_has_wall(&map, 1, 1, DIR_EAST), "East wall should be set");
    TEST_ASSERT(maze_map_has_wall(&map, 2, 1, DIR_WEST), "Reciprocal West wall should be set");

    char code[5];
    maze_map_get_wall_code(&map, 1, 1, code);
    TEST_ASSERT(strcmp(code, "EN") == 0, "Wall code for East+North must be 'EN'");

    // Boundary walls test
    MazeMap empty_map;
    maze_map_init_empty(&empty_map, 5);
    TEST_ASSERT(maze_map_has_wall(&empty_map, 0, 0, DIR_WEST), "Perimeter West wall missing");
    TEST_ASSERT(maze_map_has_wall(&empty_map, 0, 0, DIR_SOUTH), "Perimeter South wall missing");
    TEST_ASSERT(maze_map_has_wall(&empty_map, 4, 4, DIR_EAST), "Perimeter East wall missing");
    TEST_ASSERT(maze_map_has_wall(&empty_map, 4, 4, DIR_NORTH), "Perimeter North wall missing");

    printf("PASS: test_maze_map_and_reciprocal_walls\n");
}

static void test_proximity_sensor_interface(void) {
    // 1. Binary Digital Sensor
    ProximitySensorArray bin_arr = sensor_make_binary(true, false, true);
    DetectedWalls bin_walls = sensor_interface_evaluate(&bin_arr);
    TEST_ASSERT(bin_walls.wall_front == true, "Binary front sensor must detect wall");
    TEST_ASSERT(bin_walls.wall_left == false, "Binary left sensor must be clear");
    TEST_ASSERT(bin_walls.wall_right == true, "Binary right sensor must detect wall");

    // 2. ToF Millimeter Sensor (Threshold: 120 mm)
    // Front: 80 mm (wall), Left: 180 mm (clear), Right: 110 mm (wall)
    ProximitySensorArray tof_arr = sensor_make_tof_mm(80, 180, 110, 120);
    DetectedWalls tof_walls = sensor_interface_evaluate(&tof_arr);
    TEST_ASSERT(tof_walls.wall_front == true, "ToF 80mm <= 120mm must detect wall");
    TEST_ASSERT(tof_walls.wall_left == false, "ToF 180mm > 120mm must be clear");
    TEST_ASSERT(tof_walls.wall_right == true, "ToF 110mm <= 120mm must detect wall");

    // 3. Ultrasonic Centimeter Sensor (Threshold: 15 cm)
    // Front: 25 cm (clear), Left: 10 cm (wall), Right: 14 cm (wall)
    ProximitySensorArray ultra_arr = sensor_make_ultrasonic_cm(25, 10, 14, 15);
    DetectedWalls ultra_walls = sensor_interface_evaluate(&ultra_arr);
    TEST_ASSERT(ultra_walls.wall_front == false, "Ultrasonic 25cm > 15cm must be clear");
    TEST_ASSERT(ultra_walls.wall_left == true, "Ultrasonic 10cm <= 15cm must detect wall");
    TEST_ASSERT(ultra_walls.wall_right == true, "Ultrasonic 14cm <= 15cm must detect wall");

    // 4. Analog ADC Sensor (higher = closer, Threshold: 500)
    // Front: 700 (wall), Left: 200 (clear), Right: 550 (wall)
    ProximitySensorArray adc_arr = sensor_make_analog_adc(700, 200, 550, 500, true);
    DetectedWalls adc_walls = sensor_interface_evaluate(&adc_arr);
    TEST_ASSERT(adc_walls.wall_front == true, "ADC 700 >= 500 must detect wall");
    TEST_ASSERT(adc_walls.wall_left == false, "ADC 200 < 500 must be clear");
    TEST_ASSERT(adc_walls.wall_right == true, "ADC 550 >= 500 must detect wall");

    printf("PASS: test_proximity_sensor_interface\n");
}

static void test_motor_controller_translation(void) {
    MotorController controller;
    motor_controller_init(&controller, NULL);

    // Forward
    MotorCommand fwd = motor_controller_translate(&controller, NAV_CMD_MOVE_FORWARD);
    TEST_ASSERT(fwd.left_dir == MOTOR_DIR_FORWARD && fwd.right_dir == MOTOR_DIR_FORWARD, "Forward directions");
    TEST_ASSERT(fwd.turn_angle_deg == 0, "Forward turn angle must be 0");
    TEST_ASSERT(fwd.move_distance_mm == 180, "Forward distance must be 180mm");

    // Left
    MotorCommand left = motor_controller_translate(&controller, NAV_CMD_TURN_LEFT);
    TEST_ASSERT(left.left_dir == MOTOR_DIR_REVERSE && left.right_dir == MOTOR_DIR_FORWARD, "Turn left directions");
    TEST_ASSERT(left.turn_angle_deg == -90, "Turn left angle must be -90");

    // Right
    MotorCommand right = motor_controller_translate(&controller, NAV_CMD_TURN_RIGHT);
    TEST_ASSERT(right.left_dir == MOTOR_DIR_FORWARD && right.right_dir == MOTOR_DIR_REVERSE, "Turn right directions");
    TEST_ASSERT(right.turn_angle_deg == 90, "Turn right angle must be 90");

    // Around
    MotorCommand around = motor_controller_translate(&controller, NAV_CMD_TURN_AROUND);
    TEST_ASSERT(around.left_dir == MOTOR_DIR_REVERSE && around.right_dir == MOTOR_DIR_FORWARD, "Turn around directions");
    TEST_ASSERT(around.turn_angle_deg == 180, "Turn around angle must be 180");

    // Stop
    MotorCommand stop = motor_controller_translate(&controller, NAV_CMD_STOP);
    TEST_ASSERT(stop.left_dir == MOTOR_DIR_BRAKE && stop.right_dir == MOTOR_DIR_BRAKE, "Stop brake directions");
    TEST_ASSERT(stop.left_pwm_percent == 0 && stop.right_pwm_percent == 0, "Stop PWM must be 0");

    printf("PASS: test_motor_controller_translation\n");
}

static void test_floodfill_gradient_distances(void) {
    MazeMap map5, map6, map10, map16;
    build_preset_maze(&map5, 5);
    build_preset_maze(&map6, 6);
    build_preset_maze(&map10, 10);
    build_preset_maze(&map16, 16);

    uint8_t gx[4], gy[4];
    uint8_t ng;

    // 5x5
    ng = maze_map_get_centers(&map5, gx, gy);
    floodfill_compute(&map5, gx, gy, ng);
    TEST_ASSERT(map5.distances[maze_cell_index(5, 0, 0)] == 6, "5x5 distance at (0, 0) must be 6");
    TEST_ASSERT(map5.distances[maze_cell_index(5, 2, 2)] == 0, "5x5 center distance must be 0");

    // 6x6
    ng = maze_map_get_centers(&map6, gx, gy);
    floodfill_compute(&map6, gx, gy, ng);
    TEST_ASSERT(map6.distances[maze_cell_index(6, 0, 0)] == 8, "6x6 distance at (0, 0) must be 8");

    // 10x10
    ng = maze_map_get_centers(&map10, gx, gy);
    floodfill_compute(&map10, gx, gy, ng);
    TEST_ASSERT(map10.distances[maze_cell_index(10, 0, 0)] == 8, "10x10 distance at (0, 0) must be 8");

    // 16x16
    ng = maze_map_get_centers(&map16, gx, gy);
    floodfill_compute(&map16, gx, gy, ng);
    TEST_ASSERT(map16.distances[maze_cell_index(16, 0, 0)] == 44, "16x16 distance at (0, 0) must be 44");

    printf("PASS: test_floodfill_gradient_distances\n");
}

static void test_end_to_end_navigation_trajectories(void) {
    // 5x5 Maze Trajectory Test
    {
        MazeMap ground_truth;
        build_preset_maze(&ground_truth, 5);

        Navigator nav;
        navigator_init(&nav, 5, 0, 0, DIR_NORTH);

        static const int expected_5x5[6][3] = {
            {0, 1, 0},
            {1, 1, 1},
            {1, 2, 0},
            {1, 3, 0},
            {2, 3, 1},
            {2, 2, 2}
        };

        int steps = 0;
        while (steps < 20) {
            bool f = maze_map_has_wall(&ground_truth, nav.x, nav.y, nav.orientation);
            bool l = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 3U) % 4U));
            bool r = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 1U) % 4U));

            ProximitySensorArray sensors = sensor_make_binary(f, l, r);
            DetectedWalls walls = sensor_interface_evaluate(&sensors);

            NavCommand cmd = navigator_step(&nav, &walls);
            if (cmd == NAV_CMD_STOP) {
                break;
            }

            TEST_ASSERT((int)nav.x == expected_5x5[steps][0] &&
                        (int)nav.y == expected_5x5[steps][1] &&
                        (int)nav.orientation == expected_5x5[steps][2],
                        "5x5 trajectory step mismatch");
            steps++;
        }
        TEST_ASSERT(steps == 6, "5x5 must finish in exactly 6 steps");
        TEST_ASSERT(nav.x == 2 && nav.y == 2, "5x5 must terminate at center (2, 2)");
    }

    // 10x10 Maze Trajectory Test
    {
        MazeMap ground_truth;
        build_preset_maze(&ground_truth, 10);

        Navigator nav;
        navigator_init(&nav, 10, 0, 0, DIR_NORTH);

        static const int expected_10x10[10][3] = {
            {0, 1, 0},
            {0, 2, 0},
            {0, 3, 0},
            {1, 3, 1},
            {1, 4, 0},
            {1, 5, 0},
            {2, 5, 1},
            {2, 4, 2},
            {3, 4, 1},
            {4, 4, 1}
        };

        int steps = 0;
        while (steps < 30) {
            bool f = maze_map_has_wall(&ground_truth, nav.x, nav.y, nav.orientation);
            bool l = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 3U) % 4U));
            bool r = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 1U) % 4U));

            ProximitySensorArray sensors = sensor_make_binary(f, l, r);
            DetectedWalls walls = sensor_interface_evaluate(&sensors);

            NavCommand cmd = navigator_step(&nav, &walls);
            if (cmd == NAV_CMD_STOP) {
                break;
            }

            TEST_ASSERT((int)nav.x == expected_10x10[steps][0] &&
                        (int)nav.y == expected_10x10[steps][1] &&
                        (int)nav.orientation == expected_10x10[steps][2],
                        "10x10 trajectory step mismatch");
            steps++;
        }
        TEST_ASSERT(steps == 10, "10x10 must finish in exactly 10 steps");
        TEST_ASSERT(nav.x == 4 && nav.y == 4, "10x10 must terminate at center (4, 4)");
    }

    // 16x16 Maze Trajectory Test
    {
        MazeMap ground_truth;
        build_preset_maze(&ground_truth, 16);

        Navigator nav;
        navigator_init(&nav, 16, 0, 0, DIR_NORTH);

        int steps = 0;
        while (steps < 200) {
            bool f = maze_map_has_wall(&ground_truth, nav.x, nav.y, nav.orientation);
            bool l = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 3U) % 4U));
            bool r = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 1U) % 4U));

            ProximitySensorArray sensors = sensor_make_binary(f, l, r);
            DetectedWalls walls = sensor_interface_evaluate(&sensors);

            NavCommand cmd = navigator_step(&nav, &walls);
            if (cmd == NAV_CMD_STOP) {
                break;
            }
            steps++;
        }
        TEST_ASSERT(steps == 100, "16x16 must finish in exactly 100 steps");
        TEST_ASSERT(nav.x == 7 && nav.y == 7, "16x16 must terminate at center (7, 7)");
    }

    printf("PASS: test_end_to_end_navigation_trajectories\n");
}

int main(void) {
    printf("=========================================\n");
    printf("Running Embedded Flood-Fill Test Suite...\n");
    printf("=========================================\n");

    test_static_memory_footprint();
    test_maze_map_and_reciprocal_walls();
    test_proximity_sensor_interface();
    test_motor_controller_translation();
    test_floodfill_gradient_distances();
    test_end_to_end_navigation_trajectories();

    printf("\nTotal assertions checked: %d\n", g_tests_run);
    if (g_tests_failed == 0) {
        printf(">>> ALL EMBEDDED TESTS PASSED SUCCESSFULLY! <<<\n");
        return 0;
    } else {
        printf(">>> TESTS FAILED: %d <<<\n", g_tests_failed);
        return 1;
    }
}
