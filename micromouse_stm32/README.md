# STM32 Micromouse Flood-Fill Firmware (STM32CubeIDE Project)

This directory contains a complete, ready-to-import **STM32CubeIDE** project for the **STM32F103C8T6 (Blue Pill)** microcontroller.

---

## What is Included

This is a native STM32CubeIDE workspace containing the full embedded C flood-fill navigation engine, closed-loop motor control, and interactive UART communication:

```text
micromouse_stm32/
├── .cproject                    # STM32CubeIDE / Eclipse CDT compiler & toolchain settings
├── .project                     # STM32CubeIDE project descriptor
├── .mxproject                   # STM32CubeMX configuration descriptor
├── micromouse_stm32.ioc         # STM32CubeMX device configuration (peripherals, clock, pins)
├── STM32F103C8TX_FLASH.ld       # GNU ARM linker script for STM32F103C8
├── Core/
│   ├── Inc/                     # C header files
│   │   ├── main.h               # Main system declarations
│   │   ├── stm32f1xx_hal_conf.h # HAL module enable flags
│   │   ├── stm32f1xx_it.h       # Interrupt service routine headers
│   │   ├── floodfill_core.h     # Manhattan gradient flood-fill algorithm
│   │   ├── floodfill_runner.h   # Live blind navigation & benchmark runner
│   │   ├── maze_map.h           # 16x16 bitfield maze map (<600 bytes RAM)
│   │   ├── navigator.h          # High-level navigation decision state machine
│   │   ├── sensor_interface.h   # Multi-sensor evaluation & wall extraction
│   │   ├── motor_controller.h   # Dual TB6612FNG motor driver & PI closed-loop controller
│   │   ├── motor_config.h       # Encoder calibration and PI gain tunings
│   │   ├── telemetry_cmd.h      # UART command line interface & real-time telemetry streaming
│   │   └── mazes.h              # Static benchmark maze configurations (6x6, 10x10, 16x16)
│   ├── Src/                     # C source implementations
│   │   ├── main.c               # Clock configuration, peripheral init, main loop
│   │   ├── stm32f1xx_hal_msp.c  # HAL peripheral MSP initialization
│   │   ├── stm32f1xx_it.c       # SysTick, Timer, and USART interrupt handlers
│   │   ├── system_stm32f1xx.c   # CMSIS Cortex-M3 system initialization (72 MHz)
│   │   ├── syscalls.c / sysmem.c# Standard C library stub implementations
│   │   ├── floodfill_core.c     # Flood-fill BFS algorithm
│   │   ├── floodfill_runner.c   # Step-by-step blind cell navigation & DWT microsecond timing
│   │   ├── maze_map.c           # Compact wall bitfield operations
│   │   ├── navigator.c          # Navigation decision engine
│   │   ├── sensor_interface.c   # Sensor normalization
│   │   ├── motor_controller.c   # Closed-loop PI speed control & targeted moves
│   │   ├── telemetry_cmd.c      # Live UART protocol parser
│   │   └── mazes.c              # Preset benchmark wall configurations
│   └── Startup/
│       └── startup_stm32f103c8tx.s # Vector table and reset handler
├── Drivers/
│   ├── CMSIS/                   # ARM Cortex-M3 CMSIS core and device headers
│   └── STM32F1xx_HAL_Driver/    # STMicroelectronics HAL peripheral drivers (GPIO, TIM, UART, RCC)
└── README.md                    # This documentation
```

---

## How to Open in STM32CubeIDE

1. Launch **STM32CubeIDE**.
2. Select **File -> Import...** from the top menu.
3. In the import wizard, expand **General** and select **Existing Projects into Workspace**, then click **Next**.
4. In the **Select root directory** field, click **Browse...** and select this directory:
   ```text
   FloodFill-Micromouse/micromouse_stm32
   ```
5. Ensure `micromouse_stm32` is checked in the Projects list, and click **Finish**.
6. The project will appear in your Project Explorer view ready to build and debug.

---

## How to Build

1. In STM32CubeIDE, right-click the `micromouse_stm32` project in the Project Explorer.
2. Click **Build Project** (or press `Ctrl + B`).
3. The GNU ARM toolchain (`arm-none-eabi-gcc`) will compile the project:
   - Output binary: `Debug/micromouse_stm32.elf`
   - Flash size: ~**14 KB**
   - RAM usage: ~**3 KB** (of 20 KB available on STM32F103C8)

---

## How to Flash / Debug with ST-Link

1. Connect your **ST-Link V2** programmer to the 4-pin SWD header on the Blue Pill:
   - `GND` -> `GND`
   - `3.3V` -> `3.3V`
   - `SWDIO` -> `PA13`
   - `SWCLK` -> `PA14`
2. Connect the ST-Link USB to your PC.
3. In STM32CubeIDE, click **Run -> Run** (or press `Ctrl + F11`) to flash the firmware.
4. To step through the flood-fill code with breakpoints, click **Run -> Debug** (or press `F11`).

---

## Interactive Serial Console & Commands

Connect a USB-to-UART adapter to **USART2** (`PA2` TX, `PA3` RX) at **115200 baud, 8-N-1**:

| Command | Action |
| :--- | :--- |
| `BLIND_START <size>` | Runs blind cell-by-cell maze navigation (simulated motion with Python oracle) |
| `BLIND_RUN <size>` | Runs blind maze navigation with **real motors** driven via encoder feedback |
| `6` / `1` / `2` | Run 6x6 / 10x10 / 16x16 preset benchmark simulation |
| `m` | Shortcut to run 6x6 with live motors |
| `w` / `s` | Drive forward / backward |
| `a` / `d` | Spin left / right |
| `f` / `b` | Advance 1 cell forward / backward |
| `j` / `k` | Turn 90° left / right |
| `u` | Turn 180° around |
| `r` | Reset encoder totals and origin pose |
| `x` / `Space` | Immediate emergency motor stop |
| `h` | Print help menu |

---

## Hardware Pinout (STM32F103C8T6 Blue Pill)

| Function | Pin | Hardware Peripheral | Description |
| :--- | :---: | :---: | :--- |
| **USART2 TX** | `PA2` | USART2 | Telemetry / Blind Navigation stream |
| **USART2 RX** | `PA3` | USART2 | Command receiver |
| **Left Motor PWM** | `PA8` | TIM1_CH1 | Left motor speed control |
| **Right Motor PWM** | `PA9` | TIM1_CH2 | Right motor speed control |
| **Motor AIN1 / AIN2** | `PB0` / `PB1` | GPIO Output | Left motor direction (TB6612FNG) |
| **Motor BIN1 / BIN2** | `PB10` / `PB11` | GPIO Output | Right motor direction (TB6612FNG) |
| **Motor Standby (STBY)**| `PB12` | GPIO Output | TB6612FNG enable pin (HIGH = enabled) |
| **Encoder Left A / B** | `PA0` / `PA1` | TIM2 (Encoder Mode) | Left wheel quadrature encoder |
| **Encoder Right A / B**| `PA6` / `PA7` | TIM3 (Encoder Mode) | Right wheel quadrature encoder |
| **Diagnostic LED** | `PC13` | GPIO Output | Built-in Blue Pill LED (Active LOW) |
| **SWDIO / SWCLK** | `PA13` / `PA14`| SWD Debug | ST-Link flashing and debugging |
| **Power** | `3.3V` / `GND` | Power | 3.3V logic supply |

---

## Performance Characteristics (72 MHz ARM Cortex-M3)

- **Memory Safety**: Exactly **0 bytes** dynamic memory allocation (`malloc`/`free` are never called).
- **RAM Footprint**: Under **600 bytes** for entire navigation state, cell bitfield, and Manhattan distance gradients.
- **Compute Latency**:
  - 6x6 maze average step solve: **~12–20 microseconds**.
  - 10x10 maze average step solve: **~20–35 microseconds**.
  - 16x16 competition maze average step solve: **~35–50 microseconds**.
- **Timing Source**: Measured in microsecond precision via Cortex-M **DWT CYCCNT** (Data Watchpoint and Trace).
