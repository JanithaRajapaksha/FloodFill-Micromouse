# FloodFill-Micromouse

A modular, hardware-independent, and embedded-friendly implementation of the classic **Micromouse flood-fill algorithm** designed for autonomous mobile maze-solving robots.

The repository includes:
1. **Embedded C Library (`floodfill_c/`)**: An ultra-compact (< 600 bytes RAM), zero-dynamic-memory (zero `malloc`) navigation engine ready for microcontrollers (STM32, ESP32, RP2040, AVR).
2. **ESP32 Firmware Harness (`micromouse_esp32/`)**: A ready-to-flash test harness for Arduino IDE and PlatformIO with serial benchmarking and live 3-sensor hardware support.
3. **Python Reference & Simulation (`floodfill_py/`)**: A reference implementation featuring a clean Pygame visual simulation scaling to arbitrary maze dimensions.

---

## Architecture Overview

The system strictly decouples the three core robotics domains:

```
               ┌────────────────────────────────────────────────────────┐
               │              Proximity Sensors (Hardware)              │
               │            (IR, ToF VL53L0X, Ultrasonic HC-SR04)       │
               └───────────────────────────┬────────────────────────────┘
                                           │ Raw measurement
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │    Standardized Sensor Interface (sensor_interface)    │
               └───────────────────────────┬────────────────────────────┘
                                           │ Evaluated relative walls
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │        Navigation Decision Engine (navigator)          │
               │   ┌─────────────────────┐    ┌─────────────────────┐   │
               │   │  Compact Maze Map   │◄──►│  Flood-Fill Engine  │   │
               │   │     (maze_map)      │    │  (floodfill_core)   │   │
               │   └─────────────────────┘    └─────────────────────┘   │
               └───────────────────────────┬────────────────────────────┘
                                           │ High-level NavCommand
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │       Abstract Motor Controller (motor_controller)     │
               └───────────────────────────┬────────────────────────────┘
                                           │ Actuation command (PWM, angle, dist)
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │           Hardware Abstraction Layer (HAL Hook)        │
               │            (Timer PWM Compare & GPIO Direction)        │
               └────────────────────────────────────────────────────────┘
```

- **Sensor Layer (`sensor_interface`)**: Determines *what is around the robot*. Normalizes binary obstacle detections, distance readings (mm/cm), or raw ADC values into standard wall detections.
- **Navigation Layer (`navigator` + `floodfill_core` + `maze_map`)**: Determines *where the robot should go*. Maintains a bitfield maze map, updates Manhattan distance gradients, and outputs discrete navigation decisions (`MOVE_FORWARD`, `TURN_LEFT`, `TURN_RIGHT`, `TURN_AROUND`, `STOP`).
- **Motor Control Layer (`motor_controller`)**: Determines *how the robot moves*. Translates abstract navigation commands into differential drive signals (PWM %, motor directions, linear distance, and angular pivot).

---

## Key Features

- **Embedded-Ready & Memory-Safe**:
  - Exactly **513 bytes** of RAM for a full $16 \times 16$ competition maze map.
  - Zero heap allocation (`malloc`/`free`) throughout the entire embedded C pipeline.
  - Validated clean under GCC/Clang AddressSanitizer and UndefinedBehaviorSanitizer.
- **Standardized Multi-Sensor Interface**:
  - Supports digital IR proximity sensors, optical analog IR, Time-of-Flight (ToF) distance sensors, and ultrasonic sensors.
  - Operates using only 3 forward-facing channels (**Front, Left, Right**). No rear sensor required.
- **Hardware Agnostic**:
  - Core navigation logic is decoupled from microcontroller registers. Works with any MCU via a simple callback hook.
- **Interactive ESP32 Harness**:
  - Live benchmarking console measuring flood-fill steps in microseconds with zero heap degradation.
- **Python Graphical Visualization**:
  - Real-time animated Pygame demo that dynamically scales to any maze size.

---

## Repository Directory Structure

```text
FloodFill-Micromouse/
├── Makefile                 # Root Makefile to build and test both C and Python
├── README.md                # Project documentation
├── .gitignore               # Clean Git exclusion rules
├── floodfill_c/             # Production embedded C library
│   ├── include/             # Public C headers (maze_map, floodfill_core, sensor_interface, etc.)
│   ├── src/                 # C source implementations
│   ├── tests/               # C unit test suite (63 assertions)
│   ├── Makefile             # C library build system (all, test, run, asan, clean)
│   └── README.md            # Embedded C module documentation
├── floodfill_cpp/           # Build wrapper forwarding targets to floodfill_c
│   ├── Makefile             # Delegating Makefile
│   └── README.md            # Forwarding documentation
├── floodfill_py/            # Python reference implementation & visual demo
│   ├── cell.py              # Grid and Cell representation
│   ├── mouse.py             # Mouse kinematics model
│   ├── mazes.py             # Preset benchmark wall configurations (5x5, 6x6, 10x10, 16x16)
│   ├── floodFill.py         # BFS flood-fill algorithm
│   ├── ui.py                # Unified Pygame visualization
│   ├── main.py              # Python demonstration entrypoint
│   └── README.md            # Python module documentation
├── micromouse_esp32/        # Ready-to-flash ESP32 firmware project
│   ├── micromouse_esp32.ino # Arduino sketch with interactive serial test harness
│   ├── platformio.ini       # PlatformIO configuration
│   └── README.md            # ESP32 wiring and flashing guide
└── tests/                   # Python regression test suite
    └── test_floodfill.py    # 12-test suite verifying algorithm correctness
```

---

## Technology Stack

- **C**: C99 standard, portable across GCC, Clang, Xtensa GCC (ESP32), and ARM GCC (STM32/RP2040).
- **Python**: Python 3.8+ (using standard library `collections.deque`; optional `pygame` for UI).
- **Embedded Platforms**: ESP32 (Arduino / PlatformIO / ESP-IDF), STM32 (STM32CubeIDE / Keil / IAR).

---

## Quick Start & Build Instructions

### Prerequisites
- **For C**: GCC or Clang with GNU Make.
- **For Python**: Python 3.8+ (optional: `pip install pygame` for the visual UI).
- **For ESP32**: Arduino IDE or VS Code with PlatformIO.

### 1. Build and Run the C Library
```bash
# Build the C library and test binaries
make all

# Run the 10x10 demonstration simulation in C
make run

# Clean build artifacts
make clean
```

### 2. Run the Full Test Suite
Runs both the C embedded test suite (63 assertions) and the Python test suite (12 tests):
```bash
make test
```

### 3. Run Memory Safety Verification (AddressSanitizer)
```bash
make asan
```

### 4. Run the Python Simulation
```bash
# CLI demo (10x10 maze)
python3 floodfill_py/main.py

# Graphical Pygame demo (default 10x10)
python3 floodfill_py/ui.py

# Graphical demo with 16x16 maze
python3 floodfill_py/ui.py 16
```

### 5. Flash to an ESP32
1. Open [`micromouse_esp32/micromouse_esp32.ino`](micromouse_esp32/micromouse_esp32.ino) in **Arduino IDE**.
2. Select your board (e.g. `ESP32 Dev Module`) and COM port.
3. Click **Upload** and open the **Serial Monitor** at **115200 baud**.
4. Type `1`, `2`, or `3` to run benchmarks or test live sensors.

---

## Verification & Output Equivalence

Both the Python reference and the embedded C implementation produce 100% byte-for-byte identical output for equivalent benchmark inputs:

```text
( 0 ,  1 )    0
( 0 ,  2 )    0
( 0 ,  3 )    0
( 1 ,  3 )    1
( 1 ,  4 )    0
( 1 ,  5 )    0
( 2 ,  5 )    1
( 2 ,  4 )    2
( 3 ,  4 )    1
( 4 ,  4 )    1
Goal reached at (4, 4)!
```

### Benchmark Metrics

| Metric | Python Reference | Embedded C Library | ESP32 Hardware (240 MHz) |
| :--- | :---: | :---: | :---: |
| **RAM Footprint (16x16)** | ~14 KB | **513 bytes** | **513 bytes** |
| **Dynamic Allocations** | Per-step | **0 (Zero malloc)** | **0 (Zero malloc)** |
| **10x10 Solve Time** | ~2 ms | **~35 μs** | **~420 μs** |
| **16x16 Solve Time (100 steps)** | ~18 ms | **~320 μs** | **~4.1 ms** |

---

## Development Status & Future Roadmap

- [x] Python modular refactoring with optimized BFS deque.
- [x] Unified, dynamic Pygame visualization.
- [x] Zero-malloc C99 embedded library (< 600 bytes RAM).
- [x] Decoupled multi-sensor proximity interface (binary, ToF, ultrasonic, ADC).
- [x] Abstract motor control interface with platform HAL hook.
- [x] Automated test suites with sanitizer checks.
- [x] Ready-to-flash ESP32 test harness.
- [ ] Diagonal / smooth-turn speed run trajectory generation.
- [ ] STM32 HAL reference firmware template.

---

## License

This project is licensed under the MIT License.
