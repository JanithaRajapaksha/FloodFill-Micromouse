"""
Optimized and Compact Micromouse Mazes representation and presets.

Each 16x16 maze is stored as a 68-byte bitmask (horizontal + vertical wall segments).
Guarantees 100% wall symmetry, minimal memory footprint, and instantaneous unpacking.
"""

import os
import struct
from typing import Dict, List, Optional, Union
try:
    from cell import Cell, Maze, create_empty_maze
except ImportError:
    from .cell import Cell, Maze, create_empty_maze


class CompactMaze:
    """
    Compact bitmask representation of a Micromouse maze.
    - h_walls[y] has bit x set if there is a horizontal wall below cell (x, y).
    - v_walls[x] has bit y set if there is a vertical wall left of cell (x, y).
    Size for 16x16: 17 uint16 for h_walls (34 bytes) + 17 uint16 for v_walls (34 bytes) = 68 bytes!
    """

    def __init__(self, width: int, height: int, h_walls: List[int], v_walls: List[int]):
        self.width = width
        self.height = height
        self.h_walls = h_walls
        self.v_walls = v_walls

    def apply_to(self, maze: Maze) -> None:
        """Apply compact wall bitmasks to an existing Maze instance."""
        for y in range(self.height):
            for x in range(self.width):
                cell = maze[x, y]
                if self.h_walls[y + 1] & (1 << x):
                    cell.set_north_wall(maze)
                if self.h_walls[y] & (1 << x):
                    cell.set_south_wall(maze)
                if self.v_walls[x + 1] & (1 << y):
                    cell.set_east_wall(maze)
                if self.v_walls[x] & (1 << y):
                    cell.set_west_wall(maze)

    def to_bytes(self) -> bytes:
        """Serialize into compact binary format: [width, height, ...h_walls, ...v_walls]."""
        data = bytearray([self.width, self.height])
        for val in self.h_walls:
            data.extend(struct.pack('<H', val))
        for val in self.v_walls:
            data.extend(struct.pack('<H', val))
        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'CompactMaze':
        """Deserialize from compact binary format."""
        width, height = data[0], data[1]
        offset = 2
        h_count = height + 1
        v_count = width + 1
        h_walls = list(struct.unpack_from(f'<{h_count}H', data, offset))
        offset += h_count * 2
        v_walls = list(struct.unpack_from(f'<{v_count}H', data, offset))
        return cls(width, height, h_walls, v_walls)

    @classmethod
    def from_maze(cls, maze: Maze) -> 'CompactMaze':
        """Create a CompactMaze from an existing Maze object."""
        s = maze.size
        h_walls = [0] * (s + 1)
        v_walls = [0] * (s + 1)
        for y in range(s):
            for x in range(s):
                cell = maze[x, y]
                if cell.is_north_wall:
                    h_walls[y + 1] |= (1 << x)
                if cell.is_south_wall:
                    h_walls[y] |= (1 << x)
                if cell.is_east_wall:
                    v_walls[x + 1] |= (1 << y)
                if cell.is_west_wall:
                    v_walls[x] |= (1 << y)
        return cls(s, s, h_walls, v_walls)


# ============================================================================
# Compact Maze Presets
# ============================================================================

PRESET_COMPACT_5x5 = CompactMaze(
    5, 5,
    [0x1f, 0xc, 0x5, 0x8, 0x19, 0x1f],
    [0x1f, 0x5, 0x14, 0x3, 0x4, 0x1f]
)

PRESET_COMPACT_6x6 = CompactMaze(
    6, 6,
    [0x3f, 0xc, 0xc, 0x30, 0x6, 0xe, 0x3f],
    [0x3f, 0x6, 0xc, 0x0, 0xe, 0x33, 0x3f]
)

PRESET_COMPACT_10x10 = CompactMaze(
    10, 10,
    [0x3ff, 0x200, 0x84, 0x120, 0xf9, 0x38, 0xa2, 0x0, 0x0, 0x200, 0x3ff],
    [0x3ff, 0x42, 0x55, 0x28, 0xac, 0x16c, 0x54, 0x1c0, 0x0, 0xf0, 0x3ff]
)

PRESET_COMPACT_16x16 = CompactMaze(
    16, 16,
    [0xffff, 0x7fec, 0x7efc, 0x1ffa, 0xef0, 0x7f0, 0x2c0, 0x180, 0x0, 0x180, 0x3c0, 0x7e0, 0x1ff0, 0x1bfa, 0x377c, 0x6dfc, 0xffff],
    [0xffff, 0xcff3, 0x7ffe, 0x1f78, 0xf70, 0x760, 0x360, 0x100, 0xc02, 0x180, 0x3c0, 0x2760, 0xdf0, 0x1ffc, 0x3fbc, 0x7fec, 0xffff]
)

PRESET_COMPACT_BLANK = CompactMaze(
    16, 16,
    [0xffff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xffff],
    [0xffff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xffff]
)

PRESET_COMPACT_EXAMPLE2 = CompactMaze(
    16, 16,
    [0xffff, 0x23cd, 0x3020, 0x7b56, 0x36ea, 0xe174, 0x6280, 0x35cc, 0xe220, 0x61d6, 0x373b, 0x7ed6, 0x79a0, 0x8818, 0x1080, 0x237c, 0xffff],
    [0xffff, 0xf1e4, 0x70d2, 0x2f2c, 0x58d6, 0x21ea, 0x3844, 0x53a4, 0x240c, 0x38d2, 0x7126, 0xe3de, 0x47f3, 0x2000, 0x7002, 0x664e, 0xffff]
)

PRESET_COMPACT_EXAMPLE3 = CompactMaze(
    16, 16,
    [0xffff, 0x7f7c, 0x177c, 0x2b01, 0x1500, 0x2a80, 0x2440, 0xba0, 0x3c50, 0x1be6, 0x7717, 0x398e, 0x68c4, 0x37e2, 0x7ba4, 0x7f92, 0xffff],
    [0xffff, 0x79eb, 0xdc, 0xf3f8, 0x7ffc, 0x1c78, 0xcebc, 0x75c, 0x28, 0x15a0, 0x2950, 0xe28, 0x10d6, 0x48, 0x354, 0x3ffe, 0xffff]
)

PRESET_COMPACT_EXAMPLE4 = CompactMaze(
    16, 16,
    [0xffff, 0xa50c, 0x588a, 0x6624, 0x400c, 0x73c6, 0x64a2, 0x905, 0x7205, 0xa5dd, 0x21ad, 0x43d4, 0x2514, 0x1218, 0x1830, 0x73e, 0xffff],
    [0xffff, 0x3879, 0x7004, 0x2dd8, 0x9e6, 0x17de, 0x7cb6, 0x519a, 0x205c, 0x51ae, 0x2b76, 0x54d8, 0x4db6, 0x4b68, 0x548c, 0x7a40, 0xffff]
)

PRESET_COMPACT_EXAMPLE5 = CompactMaze(
    16, 16,
    [0xffff, 0x4e54, 0xa828, 0x54f0, 0x2828, 0x5678, 0x7c00, 0x380, 0xfc77, 0x16fe, 0x3930, 0x589f, 0x287c, 0x6a0a, 0xacfa, 0x6c6a, 0xffff],
    [0xffff, 0x727f, 0x147e, 0x2fa, 0xa265, 0x10ca, 0x2c60, 0x55d6, 0xfa7b, 0x7dfa, 0x2e4e, 0x7254, 0x289, 0x856, 0x76aa, 0xd54, 0xffff]
)


# ============================================================================
# Backward-Compatible Wall Arrangement Functions
# ============================================================================

def wall_arrangement_x5(maze: Maze) -> None:
    PRESET_COMPACT_5x5.apply_to(maze)

def wall_arrangement_x6(maze: Maze) -> None:
    PRESET_COMPACT_6x6.apply_to(maze)

def wall_arrangement_10x10(maze: Maze) -> None:
    PRESET_COMPACT_10x10.apply_to(maze)

def wall_arrangement_16x16(maze: Maze) -> None:
    PRESET_COMPACT_16x16.apply_to(maze)

def wall_arrangement_blank(maze: Maze) -> None:
    PRESET_COMPACT_BLANK.apply_to(maze)

def wall_arrangement_example1(maze: Maze) -> None:
    PRESET_COMPACT_16x16.apply_to(maze)

def wall_arrangement_example2(maze: Maze) -> None:
    PRESET_COMPACT_EXAMPLE2.apply_to(maze)

def wall_arrangement_example3(maze: Maze) -> None:
    PRESET_COMPACT_EXAMPLE3.apply_to(maze)

def wall_arrangement_example4(maze: Maze) -> None:
    PRESET_COMPACT_EXAMPLE4.apply_to(maze)

def wall_arrangement_example5(maze: Maze) -> None:
    PRESET_COMPACT_EXAMPLE5.apply_to(maze)


# ============================================================================
# File Loaders & Savers (.num and .bin)
# ============================================================================

def load_num_maze(filepath: str) -> Maze:
    """Load an MMS .num formatted file into a Maze instance."""
    maze = create_empty_maze(16)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 6:
                x, y, n, e, s, w = map(int, parts)
                cell = maze[x, y]
                if n: cell.set_north_wall(maze)
                if e: cell.set_east_wall(maze)
                if s: cell.set_south_wall(maze)
                if w: cell.set_west_wall(maze)
            elif len(parts) == 4:
                x, y, d, has_wall = map(int, parts)
                if has_wall:
                    cell = maze[x, y]
                    if d == 0: cell.set_north_wall(maze)
                    elif d == 1: cell.set_east_wall(maze)
                    elif d == 2: cell.set_south_wall(maze)
                    elif d == 3: cell.set_west_wall(maze)
    return maze


def load_bin_maze(filepath: str) -> Maze:
    """Load a compact binary (.bin) maze file into a Maze instance."""
    with open(filepath, 'rb') as f:
        data = f.read()
    compact = CompactMaze.from_bytes(data)
    maze = create_empty_maze(compact.width)
    compact.apply_to(maze)
    return maze


def save_bin_maze(maze: Maze, filepath: str) -> None:
    """Save a Maze instance to a compact binary (.bin) file."""
    compact = CompactMaze.from_maze(maze)
    with open(filepath, 'wb') as f:
        f.write(compact.to_bytes())


# Preset lookup dispatch
MAZE_PRESETS = {
    5: wall_arrangement_x5,
    6: wall_arrangement_x6,
    10: wall_arrangement_10x10,
    16: wall_arrangement_16x16,
    "5": wall_arrangement_x5,
    "6": wall_arrangement_x6,
    "10": wall_arrangement_10x10,
    "16": wall_arrangement_16x16,
    "example1": wall_arrangement_16x16,
    "example2": wall_arrangement_example2,
    "example3": wall_arrangement_example3,
    "example4": wall_arrangement_example4,
    "example5": wall_arrangement_example5,
    "blank": wall_arrangement_blank,
}


def build_preset_maze(size_or_name: Union[int, str]) -> Maze:
    """
    Construct and populate a Maze using a preset identifier.
    Supports integer sizes (5, 6, 10, 16) or named presets ('example1'..'example5', 'blank').
    """
    if size_or_name not in MAZE_PRESETS:
        raise ValueError(
            f"Unsupported preset: {size_or_name}. Choose from {list(MAZE_PRESETS.keys())}"
        )
    size = 16 if isinstance(size_or_name, str) and not size_or_name.isdigit() else int(size_or_name)
    maze = create_empty_maze(size)
    MAZE_PRESETS[size_or_name](maze)
    return maze
