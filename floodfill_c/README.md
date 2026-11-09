# Embedded C Micromouse Flood-Fill Library

A lightweight, portable, hardware-independent C99 implementation of the classic Micromouse flood-fill algorithm designed for resource-constrained microcontrollers (e.g. STM32, ESP32, RP2040, AVR).

---

## Key Features

- **Zero Dynamic Allocation**: 100% static memory. No calls to `malloc`, `calloc`, `realloc`, or `free`.
- **Ultra-Low RAM Footprint**:
  - `MazeMap`: **513 bytes** total (1 byte/cell for walls & visited flag, 1 byte/cell for distance).
  - `Navigator`: **528 bytes** (includes robot pose and full internal map).
  - Fits comfortably within microcontrollers with as little as 2 KB of SRAM.
- **Hardware-Decoupled Architecture**:
  - **Sensor Interface**: Standardizes digital IR, ToF (mm), ultrasonic (cm), and analog ADC inputs into normalized wall detections.
  - **Decision Engine**: Emits high-level abstract motion commands (`MOVE_FORWARD`, `TURN_LEFT`, `TURN_RIGHT`, `TURN_AROUND`, `STOP`).
  - **Motor Controller**: Translates navigation decisions into target motor directions, PWM duty cycles, travel distances, and turn angles.
  - **HAL Hook**: Simple callback hook for attaching target MCU timer PWM and GPIO drivers.

---

## Directory Structure

```text
floodfill_c/
├── include/
│   ├── maze_map.h          # Bit-packed maze representation and coordinate indexing
│   ├── floodfill_core.h    # Static-memory BFS distance gradient solver
│   ├── sensor_interface.h  # Standardized multi-sensor proximity abstraction
│   ├── navigator.h         # Robot pose tracking and navigation decision logic
│   ├── motor_controller.h  # Abstract motor commands and HAL callback interface
│   └── mazes.h             # CompactMaze bitmask struct, presets (5, 6, 10, 16, MMS), and file loaders
├── src/
│   ├── maze_map.c          # Wall bitmask operations and reciprocal wall linking
│   ├── floodfill_core.c    # Deterministic O(N²) ring-buffer flood fill
│   ├── sensor_interface.c  # Proximity evaluation (binary, ToF, ultrasonic, ADC)
│   ├── navigator.c         # Pose update, gradient step, and command generation
│   ├── motor_controller.c  # NavCommand -> MotorCommand translation
│   ├── mazes.c             # Compact 68-byte bitmask presets & .bin / .num loaders
│   └── main.c              # Demonstration and benchmarking simulation runner
├── mazes/                  # Benchmark test mazes (.num and compact .bin)
├── tests/
│   └── test_embedded.c     # Comprehensive unit test suite (7,200+ assertions)
└── Makefile                # Build configuration with AddressSanitizer support
```

---

## Build and Testing

```bash
# Build the simulation binary and test suite
make all

# Run the 63-assertion unit test suite
make test

# Run the 10x10 benchmark simulation
make run

# Run with AddressSanitizer and UndefinedBehaviorSanitizer
make asan

# Clean build artifacts
make clean
```

---

## Microcontroller Integration Example

```c
#include "navigator.h"
#include "sensor_interface.h"
#include "motor_controller.h"

static Navigator g_nav;
static MotorController g_motors;

// 1. Hardware Motor Callback (e.g. for STM32 HAL)
void stm32_motor_driver(const MotorCommand *cmd, void *user_data) {
    if (cmd->turn_angle_deg != 0) {
        // Execute in-place pivot using gyro / wheel encoders
        robot_turn_degrees(cmd->turn_angle_deg, cmd->left_pwm_percent);
    }
    if (cmd->move_distance_mm > 0) {
        // Drive straight for 1 cell pitch (180 mm)
        robot_drive_forward(cmd->move_distance_mm, cmd->left_pwm_percent);
    }
    if (cmd->left_dir == MOTOR_DIR_BRAKE) {
        robot_stop();
    }
}

void robot_init(void) {
    navigator_init(&g_nav, 16, 0, 0, DIR_NORTH);
    motor_controller_init(&g_motors, NULL);
    motor_controller_set_driver(&g_motors, stm32_motor_driver, NULL);
}

// 2. Call this function each time the robot arrives at the center of a cell
void robot_step(void) {
    // Read your physical sensors (e.g. 3 ToF sensors)
    uint16_t front_mm = read_front_sensor();
    uint16_t left_mm  = read_left_sensor();
    uint16_t right_mm = read_right_sensor();

    // Standardized 3-sensor array (threshold: 120 mm)
    ProximitySensorArray sensors = sensor_make_tof_mm(front_mm, left_mm, right_mm, 120);
    DetectedWalls walls = sensor_interface_evaluate(&sensors);

    // Compute next action and dispatch directly to motor driver
    NavCommand cmd = navigator_step(&g_nav, &walls);
    motor_controller_execute(&g_motors, cmd);
}
```

---

## Compact Maze Representation & Presets

For microcontrollers with strict Flash ROM constraints (e.g. STM32 Blue Pill with 64 KB Flash), mazes can be represented in `CompactMaze` format (68 bytes per 16×16 maze, instead of 256 bytes):

```c
#include "mazes.h"

// 1. Initialize from built-in presets:
MazeMap map;
build_preset_maze(&map, 16);               // Standard 5x5, 6x6, 10x10, 16x16
build_preset_mms_maze(&map, "example2");   // "blank", "example1" - "example5"

// 2. Unpack custom compact bitmasks:
static const CompactMaze MY_MAZE = {
    16, 16,
    { 0xffff, 0x23cd, /* ... 17 uint16_t values ... */ }, // h_walls
    { 0xffff, 0xf1e4, /* ... 17 uint16_t values ... */ }  // v_walls
};
compact_maze_apply(&MY_MAZE, &map);

// 3. File loading (simulator / desktop builds):
maze_map_load_bin_file(&map, "mazes/example2.bin");
maze_map_load_num_file(&map, "mazes/example2.num");
```

