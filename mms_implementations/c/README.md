# MMS-Compatible C Flood-Fill Micromouse

A standalone, embedded-style Micromouse flood-fill algorithm adapted for the official [MMS Micromouse Simulator](https://github.com/mackorone/mms).

## Architecture

This implementation is adapted from the project's embedded C engine (`floodfill_c/`) while strictly isolating all hardware/HAL dependencies:
- **`API.h` / `API.c`**: Official MMS simulator standard I/O communication interface.
- **`maze_map.h` / `maze_map.c`**: Zero-allocation bitfield maze map tracking discovered walls and flood-fill Manhattan distances.
- **`floodfill_core.h` / `floodfill_core.c`**: BFS distance gradient solver using static queue buffers and strict North-East-South-West deterministic tie-breaking.
- **`navigator.h` / `navigator.c`**: Blind exploration state machine integrating sensor queries, wall projection, goal checking, and turn/step actuation.
- **`main.c`**: Main execution loop with reset detection and graceful termination.

## Building

### Windows (MinGW GCC):
```cmd
gcc -Wall -Wextra -O2 -std=c99 -I. API.c maze_map.c floodfill_core.c navigator.c main.c -o mouse.exe
```

Or using `make` / `mingw32-make` / `gmake`:
```cmd
make
```

### Linux / macOS:
```bash
gcc -Wall -Wextra -O2 -std=c99 -I. API.c maze_map.c floodfill_core.c navigator.c main.c -o mouse
```

## MMS Configuration

In the MMS Simulator:
1. Click the **+** (Add) button under the **Mouse Algorithm** panel.
2. Fill in the fields:
   - **Name**: `FloodFill-C`
   - **Directory**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/c`
   - **Build Command**: `cmd.exe /c echo Done`
   - **Run Command**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/c/mouse.exe`
3. Click **Save**.
4. Select `FloodFill-C` from the algorithm dropdown, choose a maze, and press **Run**.

## Simulator Features Used

- **Blind Exploration**: Robot starts at `(0, 0)` facing North with only perimeter boundary walls known.
- **Wall Sensing**: Uses `API_wallFront()`, `API_wallLeft()`, `API_wallRight()` to detect walls in the current cell.
- **Visualization**:
  - Discovered walls drawn in real-time via `API_setWall()`.
  - Explored cell trails colored with `API_setColor(x, y, 'a')`.
  - Goal tiles highlighted with `API_setColor(gx, gy, 'G')`.
  - Live flood-fill distance values displayed on cells via `API_setText()`.
- **Reset Handling**: Detects GUI reset events via `API_wasReset()`, acknowledges with `API_ackReset()`, clears graphics, and restarts search from origin without restarting process.
