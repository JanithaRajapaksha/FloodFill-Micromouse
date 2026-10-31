# Python Micromouse Flood-Fill Simulation

A modular Python reference implementation and graphical simulation of the Micromouse flood-fill algorithm.

---

## Directory Structure

```text
floodfill_py/
├── cell.py        # Cell and Maze classes with reciprocal wall linking
├── mouse.py       # Mouse agent kinematics and sensor update logic
├── mazes.py       # Preset wall arrangements for 5x5, 6x6, 10x10, and 16x16 mazes
├── floodFill.py   # Core BFS flood-fill algorithm and navigation runner
├── main.py        # Command-line navigation demonstration (10x10 benchmark)
├── ui.py          # Unified Pygame visualization dynamically scaling to any maze size
├── ui2.py         # 6x6 UI demonstration entrypoint
├── ui_maze10.py   # 10x10 UI demonstration entrypoint
├── ui_maze16.py   # 16x16 UI demonstration entrypoint
└── ui_assets/
    └── mouse.png  # Graphic asset for mouse sprite
```

---

## Usage

### Command-Line Demonstration
```bash
python3 floodfill_py/main.py
```

### Graphical Pygame UI Demonstration
```bash
# Run with default 10x10 maze
python3 floodfill_py/ui.py

# Run with arbitrary maze dimension (e.g. 16x16 or 6x6)
python3 floodfill_py/ui.py 16
python3 floodfill_py/ui.py 6
```
*(If Pygame is not installed, the UI gracefully falls back to console output).*

---

## Testing
Run the automated test suite from the repository root:
```bash
python3 -m unittest discover -s tests
```
