# ESP32 Micromouse Flood-Fill Test Project

This directory contains a standalone, ready-to-flash test harness for the **ESP32** microcontroller.

---

## What is Included

- **`micromouse_esp32.ino`**: Arduino sketch with an interactive serial console for running 10x10 and 16x16 maze benchmarks and testing live 3-sensor hardware.
- **Embedded C Library**: Statically-sized, zero-`malloc` navigation modules (`maze_map`, `floodfill_core`, `sensor_interface`, `navigator`, `motor_controller`, `mazes`).
- **`platformio.ini`**: Configuration file for VS Code / PlatformIO.

---

## Option A: Using Arduino IDE

1. Open **Arduino IDE**.
2. Go to **File -> Open...** and select `micromouse_esp32/micromouse_esp32.ino`.
3. Select your ESP32 board under **Tools -> Board -> ESP32 Arduino** (e.g., `ESP32 Dev Module`).
4. Select the serial port under **Tools -> Port**.
5. Click **Upload** (or press `Ctrl + U`).
6. Open **Tools -> Serial Monitor** and set baud rate to **`115200`**.

---

## Option B: Using VS Code + PlatformIO

1. Open VS Code with the PlatformIO extension.
2. Open the `micromouse_esp32/` folder as a project.
3. Click **PlatformIO: Build** (`Ctrl + Alt + B`) and **Upload**.
4. Open the Serial Monitor (`Ctrl + Alt + S`).

---

## Interactive Serial Commands

When the ESP32 boots, it automatically runs the 10x10 maze benchmark once and waits for commands on the Serial Monitor at **115200 baud**:

- Send **`1`**: Run the 10x10 maze benchmark.
- Send **`2`**: Run the full 16x16 competition maze benchmark (100 steps).
- Send **`3`**: Read physical GPIO sensors (Front, Left, Right) once and print decision.
- Send **`r`**: Reset the navigator to start position (0, 0, North).
- Send **`h`**: Show menu.

---

## Connecting Physical Sensors (Optional Live Test)

By default, 3 digital proximity sensors (IR / ToF obstacle sensors) can be connected to the ESP32:

| Sensor | ESP32 GPIO Pin | Description |
| :--- | :---: | :--- |
| **Front Sensor** | `GPIO 32` | Digital Output from Front Sensor |
| **Left Sensor**  | `GPIO 33` | Digital Output from Left Sensor |
| **Right Sensor** | `GPIO 34` | Digital Output from Right Sensor |
| **VCC**          | `3.3V` or `VIN` | Sensor Power Supply |
| **GND**          | `GND` | Common Ground |

*(Pins can be changed in `micromouse_esp32.ino` via `#define PIN_SENSOR_*`)*

