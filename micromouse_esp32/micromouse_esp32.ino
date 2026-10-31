/**
 * @file micromouse_esp32.ino
 * @brief ESP32 Embedded Test Harness for Micromouse Flood-Fill Navigation.
 *
 * Provides two testing modes:
 * 1. Benchmark Simulation Mode: Solves pre-set 10x10 and 16x16 mazes entirely on the
 *    ESP32 chip, benchmarks step solving time in microseconds, and checks heap integrity.
 * 2. Live Sensor Mode: Reads 3 physical proximity sensors (Front, Left, Right) from
 *    configurable GPIO pins and prints real-time navigation and motor decisions.
 */

#include <Arduino.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "maze_map.h"
#include "floodfill_core.h"
#include "sensor_interface.h"
#include "navigator.h"
#include "motor_controller.h"
#include "mazes.h"

#ifdef __cplusplus
}
#endif

// ============================================================================
// GPIO PIN CONFIGURATION (For Live Sensor Mode)
// ============================================================================
#define PIN_SENSOR_FRONT  32  // Digital IR / ToF XSHUT or GPIO input
#define PIN_SENSOR_LEFT   33  // Digital IR / ToF GPIO input
#define PIN_SENSOR_RIGHT  34  // Digital IR / ToF GPIO input

// Digital IR modules typically output LOW (0V) when a wall is detected
#define SENSOR_ACTIVE_STATE LOW

// ============================================================================
// GLOBAL STATE
// ============================================================================
static Navigator g_live_nav;
static MotorController g_live_motor;
static bool g_live_initialized = false;

// Simulated hardware motor callback
static void esp32_motor_driver_callback(const MotorCommand *cmd, void *user_data) {
    (void)user_data;
    // In actual firmware, you attach your PWM Timer and Direction GPIOs here:
    // e.g., ledcWrite(LEFT_PWM_CHANNEL, cmd->left_pwm_percent * 255 / 100);
}

// ============================================================================
// TEST 1: BENCHMARK SIMULATION (10x10 and 16x16)
// ============================================================================
void run_maze_benchmark(uint8_t maze_size) {
    Serial.printf("\n==================================================\n");
    Serial.printf("  ESP32 Benchmark: %ux%u Maze Flood-Fill Test\n", maze_size, maze_size);
    Serial.printf("==================================================\n");

    MazeMap ground_truth;
    if (!build_preset_maze(&ground_truth, maze_size)) {
        Serial.printf("Error: Unsupported maze size %u\n", maze_size);
        return;
    }

    Navigator nav;
    navigator_init(&nav, maze_size, 0, 0, DIR_NORTH);

    MotorController motor;
    motor_controller_init(&motor, NULL);
    motor_controller_set_driver(&motor, esp32_motor_driver_callback, NULL);

    uint32_t initial_heap = ESP.getFreeHeap();
    uint32_t start_us = micros();
    uint32_t step_count = 0;

    while (true) {
        // 1. Observe ground-truth maze with 3 sensors (Front, Left, Right)
        bool f = maze_map_has_wall(&ground_truth, nav.x, nav.y, nav.orientation);
        bool l = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 3U) % 4U));
        bool r = maze_map_has_wall(&ground_truth, nav.x, nav.y, (Direction)((nav.orientation + 1U) % 4U));

        // 2. Standardized sensor data interface (No rear sensor needed)
        ProximitySensorArray sensors = sensor_make_binary(f, l, r);
        DetectedWalls walls = sensor_interface_evaluate(&sensors);

        // 3. Navigation step
        uint32_t step_start = micros();
        NavCommand cmd = navigator_step(&nav, &walls);
        uint32_t step_time = micros() - step_start;

        // 4. Translate to motor command
        MotorCommand m_cmd = motor_controller_execute(&motor, cmd);

        if (cmd == NAV_CMD_STOP) {
            Serial.printf("[Step %2u] Goal reached at (%u, %u)!\n", step_count, nav.x, nav.y);
            break;
        }

        step_count++;
        Serial.printf("[Step %2u] Pose: (%2u, %2u) Dir: %u | Action: %-12s | Mot L:%3u%% R:%3u%% Turn:%4d deg (%u us)\n",
                      step_count, nav.x, nav.y, (uint8_t)nav.orientation,
                      nav_command_to_string(cmd),
                      m_cmd.left_pwm_percent, m_cmd.right_pwm_percent,
                      m_cmd.turn_angle_deg,
                      step_time);
    }

    uint32_t total_us = micros() - start_us;
    uint32_t final_heap = ESP.getFreeHeap();

    Serial.printf("--------------------------------------------------\n");
    Serial.printf("Execution Results:\n");
    Serial.printf("  Total Steps:      %u steps\n", step_count);
    Serial.printf("  Total Time:       %u us (%.3f ms)\n", total_us, total_us / 1000.0f);
    Serial.printf("  Avg per Step:     %.2f us\n", (float)total_us / (step_count > 0 ? step_count : 1));
    Serial.printf("  Memory Footprint: sizeof(MazeMap)=%u bytes, sizeof(Navigator)=%u bytes\n",
                  (unsigned)sizeof(MazeMap), (unsigned)sizeof(Navigator));
    Serial.printf("  Free Heap delta:  %d bytes (0 bytes heap used = NO LEAKS!)\n",
                  (int)(final_heap - initial_heap));
    Serial.printf("==================================================\n\n");
}

// ============================================================================
// TEST 2: LIVE 3-SENSOR HARDWARE TESTING
// ============================================================================
void init_live_sensor_mode() {
    pinMode(PIN_SENSOR_FRONT, INPUT);
    pinMode(PIN_SENSOR_LEFT, INPUT);
    pinMode(PIN_SENSOR_RIGHT, INPUT);

    navigator_init(&g_live_nav, 16, 0, 0, DIR_NORTH);
    motor_controller_init(&g_live_motor, NULL);
    motor_controller_set_driver(&g_live_motor, esp32_motor_driver_callback, NULL);

    g_live_initialized = true;

    Serial.println("\n--- Live 3-Sensor Hardware Mode Active ---");
    Serial.printf("Configured Pins: Front=GPIO%d, Left=GPIO%d, Right=GPIO%d\n",
                  PIN_SENSOR_FRONT, PIN_SENSOR_LEFT, PIN_SENSOR_RIGHT);
    Serial.println("Wave an obstacle in front of your sensors to see real-time decisions:\n");
}

void run_live_sensor_step() {
    if (!g_live_initialized) {
        init_live_sensor_mode();
    }

    // Read physical GPIO pins
    bool front_wall = (digitalRead(PIN_SENSOR_FRONT) == SENSOR_ACTIVE_STATE);
    bool left_wall  = (digitalRead(PIN_SENSOR_LEFT)  == SENSOR_ACTIVE_STATE);
    bool right_wall = (digitalRead(PIN_SENSOR_RIGHT) == SENSOR_ACTIVE_STATE);

    // Standardized 3-sensor array
    ProximitySensorArray sensors = sensor_make_binary(front_wall, left_wall, right_wall);
    DetectedWalls walls = sensor_interface_evaluate(&sensors);

    // Step navigator and motor controller
    NavCommand cmd = navigator_step(&g_live_nav, &walls);
    MotorCommand m_cmd = motor_controller_execute(&g_live_motor, cmd);

    Serial.printf("Sensors [L:%s F:%s R:%s] -> Pose (%u,%u,dir=%u) -> Decision: %-12s | Motor PWM: L=%u%% R=%u%%\n",
                  walls.wall_left  ? "WALL " : "OPEN ",
                  walls.wall_front ? "WALL " : "OPEN ",
                  walls.wall_right ? "WALL " : "OPEN ",
                  g_live_nav.x, g_live_nav.y, (uint8_t)g_live_nav.orientation,
                  nav_command_to_string(cmd),
                  m_cmd.left_pwm_percent, m_cmd.right_pwm_percent);
}

// ============================================================================
// MAIN ARDUINO SETUP & LOOP
// ============================================================================
void print_menu() {
    Serial.println("==================================================");
    Serial.println("  ESP32 Micromouse Flood-Fill Test Console");
    Serial.println("==================================================");
    Serial.println("Commands:");
    Serial.println("  '1' : Run 10x10 Maze Benchmark Test");
    Serial.println("  '2' : Run 16x16 Full Competition Maze Benchmark");
    Serial.println("  '3' : Step Live Sensors once (GPIO 32, 33, 34)");
    Serial.println("  'r' : Reset / Restart Navigator");
    Serial.println("  'h' : Print this Menu");
    Serial.println("==================================================");
}

void setup() {
    Serial.begin(115200);
    delay(1500); // Wait for USB Serial Monitor to open

    print_menu();

    // Auto-run 10x10 benchmark once on startup
    Serial.println("\n[Auto-Test] Running 10x10 Benchmark on startup...");
    run_maze_benchmark(10);
}

void loop() {
    if (Serial.available() > 0) {
        char ch = (char)Serial.read();

        // Discard newline characters
        if (ch == '\r' || ch == '\n') return;

        switch (ch) {
            case '1':
                run_maze_benchmark(10);
                break;
            case '2':
                run_maze_benchmark(16);
                break;
            case '3':
                run_live_sensor_step();
                break;
            case 'r':
                init_live_sensor_mode();
                Serial.println("Navigator state reset to (0, 0, DIR_NORTH).");
                break;
            case 'h':
                print_menu();
                break;
            default:
                Serial.printf("Unknown command '%c'. Type 'h' for menu.\n", ch);
                break;
        }
    }
}

