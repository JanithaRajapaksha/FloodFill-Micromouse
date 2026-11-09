# Python Micromouse Flood-Fill Simulation

A modular Python reference implementation and graphical simulation of the Micromouse flood-fill algorithm.

---

## Directory Structure

```text
floodfill_py/
├── cell.py        # Cell and Maze classes with reciprocal wall linking
├── mouse.py       # Mouse agent kinematics and sensor update logic
├── mazes.py       # Compact bitmask presets (5, 6, 10, 16, MMS), CompactMaze class, and loaders
├── floodFill.py   # Core BFS flood-fill algorithm and navigation runner
├── main.py        # Command-line navigation demonstration (10x10 benchmark)
├── ui.py          # Unified interactive PyQt6 simulator (Fog of War, Speed Run, MMS console)
└── ui_assets/     # Graphic assets (MMS icons, turtle/rabbit icons, mouse sprite)

# Mazes are stored in the unified root directory:
../mazes/
├── bin/
│   ├── janitha_mazes/ # 5x5, 6x6, 10x10, 16x16
│   ├── mms_mazes/     # blank, example1..5
│   └── japan_ntf/     # 103 All-Japan competition mazes
└── num/
    ├── janitha_mazes/ # 5x5, 6x6, 10x10, 16x16
    ├── mms_mazes/     # blank, example1..5
    └── japan_ntf/     # 103 All-Japan competition mazes
```

---

## Usage

### Command-Line Demonstration
```bash
python3 floodfill_py/main.py
```

### Graphical PyQt6 UI Demonstration
```bash
# Run with default interactive simulator
python floodfill_py/ui.py

# Run with arbitrary maze preset (e.g. example2, 16, or 6)
python floodfill_py/ui.py example2
python floodfill_py/ui.py 10

# Run with any historical Japanese championship maze (103 available)
python floodfill_py/ui.py AllJapan_001_1980_classic
python floodfill_py/ui.py Other_World85Fin_1985_classic
```
*(Requires `PyQt6` for the modern dark desktop interface).*

---

## Testing
Run the automated test suite from the repository root:
```bash
python3 -m unittest discover -s tests
```

---

## Maze Presets & Compact Bitmask Format

Mazes can be loaded by preset name, from standard MMS `.num` ASCII files, or from compact 70-byte `.bin` binary files:

```python
from mazes import build_preset_maze, load_bin_maze, load_num_maze, save_bin_maze

# 1. Load by preset name (supports 5, 6, 10, 16, "blank", "example1" - "example5")
maze = build_preset_maze("example2")

# 2. Load from compact binary file (70 bytes):
maze = load_bin_maze("mazes/example2.bin")

# 3. Load from MMS text file:
maze = load_num_maze("mazes/example2.num")

# 4. Save any maze to compact binary format:
save_bin_maze(maze, "my_custom_maze.bin")
```

