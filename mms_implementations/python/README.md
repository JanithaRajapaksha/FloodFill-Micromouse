# MMS-Compatible Python Flood-Fill Micromouse

A standalone Micromouse flood-fill navigation algorithm adapted for the official [MMS Micromouse Simulator](https://github.com/mackorone/mms).

## Architecture

This implementation is adapted from the project's Python reference engine (`floodfill_py/`) while replacing the Pygame visual harness with native MMS protocol calls:
- **`API.py`**: Official MMS Python interface wrapping simulator stdin/stdout commands.
- **`cell.py`**: Grid and cell structures maintaining discovered walls, coordinates, and reciprocal wall connections.
- **`mouse.py`**: Robot kinematics model tracking $(x, y)$ position and orientation, querying MMS sensors, and executing turns and forward moves.
- **`floodFill.py`**: BFS shortest-path solver with strict North-East-South-West deterministic tie-breaking.
- **`main.py`**: Standalone entrypoint running blind exploration with dynamic reset handling.

## Requirements

- Python 3.7+ (uses standard library only: `sys`, `collections`, `typing`; no `pygame` required).

## MMS Configuration

In the MMS Simulator:
1. Click the **+** (Add) button under the **Mouse Algorithm** panel.
2. Fill in the fields:
   - **Name**: `FloodFill-Python`
   - **Directory**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/python`
   - **Build Command**: `cmd.exe /c echo Done`
   - **Run Command**: `C:/Users/JANITHA/AppData/Local/Programs/Python/Python310/python.exe main.py`
3. Click **Save**.
4. Select `FloodFill-Python` from the algorithm dropdown, choose a maze, and click **Run**.

## Simulator Features Used

- **Blind Exploration**: Robot starts at `(0, 0)` facing North with zero hidden maze knowledge.
- **Wall Sensing**: Uses `API.wallFront()`, `API.wallLeft()`, and `API.wallRight()`.
- **Visualization**:
  - Live discovered walls rendered via `API.setWall()`.
  - Visited path trail colored with `API.setColor(x, y, 'a')`.
  - Center goal cells highlighted with `API.setColor(gx, gy, 'G')`.
  - Dynamic Manhattan distance values displayed using `API.setText()`.
- **Reset Handling**: Detects GUI resets through `API.wasReset()`, acknowledges via `API.ackReset()`, and resets state to restart exploration from origin.
