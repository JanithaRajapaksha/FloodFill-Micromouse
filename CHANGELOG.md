# Changelog & Submodule Integration Guide

This document records architectural updates, memory optimizations, and API additions for downstream repositories consuming **FloodFill-Micromouse** as a Git submodule.

---

## [Unreleased / Latest Updates] - 2026-11-09

### Highlights
* **Zero Breaking Changes**: All previous function signatures (`wall_arrangement_5x5`, `build_preset_maze`, etc.) and data structures (`MazeMap`, `Navigator`, `Cell`, `Maze`) remain 100% backward compatible.
* **68-Byte Compact Bitmask Representation**: Replaced ~2,500 lines of verbose matrix arrays with physical horizontal/vertical wall bit arrays. Reduces Flash ROM footprint per 16x16 maze from 256 bytes to 68 bytes.
* **Compact Binary (`.bin`) Maze Format**: Introduced standard 70-byte binary format (98% smaller than 10KB `.num` files).
* **MMS Simulator Mazes & Presets**: Integrated `blank`, `example1`–`example5` test mazes into both C and Python.
* **103 Official All-Japan NTF Competition Mazes (1980–2012)**: Converted all historical competition mazes from the New Technology Foundation archive (`https://www.ntf.or.jp/mouse/history/`) into both compact `.bin` (70 bytes) and MMS `.num` formats across Python, C, and MMS folders. 100% verified solvable.
* **BMP Image Maze Parser & Importer**: Added native 194x194 BMP parser into `tools/maze_converter.py` and batch automation in `tools/fetch_ntf_mazes.py`.
* **Converter CLI Utility (`tools/maze_converter.py`)**: Convert between `.num`, `.bin`, and `.bmp`, inspect maze statistics, and export ready-to-paste C/Python definitions.

---

### Detailed Changes by Subsystem

#### 1. Embedded C Library (`floodfill_c/`)
* **Header Additions (`floodfill_c/include/mazes.h`)**:
  * Added `CompactMaze` struct:
    ```c
    typedef struct {
        uint8_t width;
        uint8_t height;
        uint16_t h_walls[17]; // Bit x = horizontal wall below cell (x, y)
        uint16_t v_walls[17]; // Bit y = vertical wall left of cell (x, y)
    } CompactMaze;
    ```
  * Added `compact_maze_apply(const CompactMaze *cm, MazeMap *map)`: Unpacks a 68-byte compact bitmask directly into a `MazeMap`.
  * Added MMS preset wrappers:
    * `wall_arrangement_blank(MazeMap *map)`
    * `wall_arrangement_example1(MazeMap *map)`
    * `wall_arrangement_example2(MazeMap *map)`
    * `wall_arrangement_example3(MazeMap *map)`
    * `wall_arrangement_example4(MazeMap *map)`
    * `wall_arrangement_example5(MazeMap *map)`
    * `build_preset_mms_maze(MazeMap *map, const char *name)`
  * Added Binary File I/O (desktop/simulator builds):
    * `bool maze_map_load_bin_file(MazeMap *map, const char *filepath)`
    * `bool maze_map_save_bin_file(const MazeMap *map, const char *filepath)`
  * Added `.num` File Loader:
    * `bool maze_map_load_num_file(MazeMap *map, const char *filepath)` (supports both 6-value MMS format and 4-value format).
* **Internal Source Optimization (`floodfill_c/src/mazes.c`)**:
  * Shrink from 1,290 lines to ~270 lines.
  * Replaced 256-byte `uint8_t[16][16]` cell arrays with 68-byte `CompactMaze` static definitions (`PRESET_COMPACT_...`).

#### 2. Python Reference & Simulation (`floodfill_py/`)
* **Module Additions (`floodfill_py/mazes.py`)**:
  * Added `CompactMaze` class with:
    * `apply_to(maze: Maze) -> None`
    * `to_bytes() -> bytes`
    * `from_bytes(data: bytes) -> CompactMaze`
    * `from_maze(maze: Maze) -> CompactMaze`
  * Added binary file loaders:
    * `load_bin_maze(filepath: str) -> Maze`
    * `save_bin_maze(maze: Maze, filepath: str) -> None`
  * Added MMS `.num` loader:
    * `load_num_maze(filepath: str) -> Maze`
  * Updated `build_preset_maze(size_or_name)`:
    * Accepts integer sizes: `5`, `6`, `10`, `16`
    * Accepts string names: `"5"`, `"6"`, `"10"`, `"16"`, `"blank"`, `"example1"`–`"example5"`
* **Code Size Optimization**:
  * Reduced `mazes.py` from 1,313 lines to ~230 lines while preserving all public functions.

#### 3. New Tools & Standalone Implementations
* **`tools/maze_converter.py`**:
  * `info <file>`: Inspects dimensions, wall segment counts, and byte sizes.
  * `convert <input> <output>`: Converts between `.num` and `.bin`.
  * `to-c <file> [--name NAME]`: Generates static C `CompactMaze` definition.
  * `to-py <file> [--name NAME]`: Generates Python `CompactMaze` definition.
* **`mms_implementations/`**:
  * `mms_implementations/c/`: Standalone C implementation wired to official MMS simulator API.
  * `mms_implementations/python/`: Standalone Python implementation for MMS simulator.
  * Multi-maze test runner `test_all_mazes.py` validating 100% trajectory parity across both.

---

### Submodule Migration & Integration Guide

#### For C Projects (e.g., STM32 Blue Pill, ESP32, AVR):
1. **Pulling the Submodule**:
   ```bash
   git submodule update --remote --merge
   ```
2. **Backward Compatibility**:
   * If your firmware project already calls `build_preset_maze(&map, 16)` or `wall_arrangement_16x16(&map)`, **no code changes are needed**. It will build and run as before with a smaller Flash ROM footprint.
3. **Using Compact Mazes in Low-Flash Microcontrollers**:
   * If you need to store multiple benchmark mazes in MCU Flash (e.g. STM32F103 with 64KB Flash), use `CompactMaze` instead of 256-byte matrices:
     ```c
     #include "mazes.h"

     // Each maze takes only 68 bytes of Flash ROM!
     MazeMap map;
     build_preset_mms_maze(&map, "example2");

     // Or unpack your own custom compact maze:
     compact_maze_apply(&MY_CUSTOM_COMPACT_MAZE, &map);
     ```

#### For Python Projects:
1. **Using Presets or Binary Files**:
   ```python
   from floodfill_py.mazes import build_preset_maze, load_bin_maze

   # Load by preset name:
   maze1 = build_preset_maze("example2")

   # Load from compact 70-byte binary file:
   maze2 = load_bin_maze("floodfill_py/mazes/example3.bin")
   ```
