# MMS Micromouse Flood-Fill Algorithms (C & Python)

This directory provides two standalone, independent implementations of the classic Micromouse flood-fill algorithm ready to run inside the official [mackorone/mms](https://github.com/mackorone/mms) simulator:

1. **C Implementation** (`mms_implementations/c/`): Fast, memory-efficient, embedded C architecture.
2. **Python Implementation** (`mms_implementations/python/`): Clean, object-oriented reference architecture using the standard library.

Both implementations perform **100% blind maze exploration**, obey strict **North-East-South-West** deterministic tie-breaking, update live MMS visualization graphics, and handle dynamic simulator resets.

---

## Algorithm Registration in MMS

Open the MMS Simulator and configure each algorithm in the **Mouse Algorithms** settings dialog (click the `+` button in the left panel):

### 1. Register the C Algorithm (`FloodFill-C`)

- **Name**: `FloodFill-C`
- **Directory**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/c`
- **Build Command**: `cmd.exe /c echo Done`
- **Run Command**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/c/mouse.exe`

### 2. Register the Python Algorithm (`FloodFill-Python`)

- **Name**: `FloodFill-Python`
- **Directory**: `C:/DATA/FYP/ST/bluepill_motor_test/FloodFill-Micromouse/mms_implementations/python`
- **Build Command**: `cmd.exe /c echo Done`  
  *(Or: `C:/Users/JANITHA/AppData/Local/Programs/Python/Python310/python.exe -m py_compile main.py`)*
- **Run Command**: `C:/Users/JANITHA/AppData/Local/Programs/Python/Python310/python.exe main.py`

---

## Switching Between Implementations in MMS

1. In the MMS main window, locate the **Mouse Algorithm** drop-down menu on the left control panel.
2. Select either **`FloodFill-C`** or **`FloodFill-Python`**.
3. Select any maze (e.g. from the **Maze** dropdown, or load a `.num` file from `mms/src/resources/mazes/`).
4. Click **Build** (or click **Run**, which builds automatically if needed).
5. Watch the mouse explore blindly, discover walls, update flood-fill distances, and solve the maze to the center!
6. Click **Reset** at any time during a run: both implementations will catch `wasReset()`, call `ackReset()`, clear their internal state and graphics, and restart exploration from `(0, 0)`.

---

## Comparative Verification

| Feature | C Implementation (`mms_implementations/c`) | Python Implementation (`mms_implementations/python`) |
| :--- | :--- | :--- |
| **API Protocol** | `API.h` / `API.c` via standard I/O | `API.py` via standard I/O |
| **Starting State** | `(0, 0)` facing North | `(0, 0)` facing North |
| **Blind Exploration** | Zero preloaded walls (perimeter only) | Zero preloaded walls (perimeter only) |
| **Tie-Breaking** | Strict North -> East -> South -> West | Strict North -> East -> South -> West |
| **Coordinates** | Cartesian: (0,0) bottom-left | Cartesian: (0,0) bottom-left |
| **Visualization** | `API_setWall`, `API_setColor`, `API_setText` | `API.setWall`, `API.setColor`, `API.setText` |
| **Reset Handling** | `API_wasReset()` + `API_ackReset()` | `API.wasReset()` + `API.ackReset()` |
| **External Dependencies** | None (pure C99 standard library) | None (pure Python 3 standard library) |
