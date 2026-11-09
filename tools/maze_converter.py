#!/usr/bin/env python3
"""
Micromouse Maze Converter Utility.

Converts between:
- MMS .num format (~8-10 KB ASCII text)
- Compact .bin format (70 bytes binary bitmask)
- C/Python embeddable static arrays
"""

import argparse
import os
import struct
import sys
from typing import List, Tuple


def read_bmp_file(filepath: str) -> Tuple[int, int, List[int], List[int]]:
    """Reads a 194x194 Micromouse competition BMP image (NTF format) into bitmasks."""
    from PIL import Image
    with Image.open(filepath) as img:
        pixels = img.load()
        width, height = 16, 16
        h_walls = [0] * (height + 1)
        v_walls = [0] * (width + 1)

        for y in range(height + 1):
            r_line = 16 - y
            y_pixel = 12 * r_line + 1
            for x in range(width):
                x_pixel = 12 * x + 6
                r, g, b = pixels[x_pixel, y_pixel][:3]
                if r > 128 and g < 60 and b < 60:
                    h_walls[y] |= (1 << x)

        for x in range(width + 1):
            c_line = x
            x_pixel = 12 * c_line + 1
            for y in range(height):
                y_pixel = 12 * (15 - y) + 6
                r, g, b = pixels[x_pixel, y_pixel][:3]
                if r > 128 and g < 60 and b < 60:
                    v_walls[x] |= (1 << y)

    return width, height, h_walls, v_walls


def read_num_file(filepath: str) -> Tuple[int, int, List[int], List[int]]:
    """Reads an MMS .num file and returns (width, height, h_walls, v_walls)."""
    width = 16
    height = 16
    h_walls = [0] * (height + 1)
    v_walls = [0] * (width + 1)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 6:
                x, y, n, e, s, w = map(int, parts)
                if n:
                    h_walls[y + 1] |= (1 << x)
                if e:
                    v_walls[x + 1] |= (1 << y)
                if s:
                    h_walls[y] |= (1 << x)
                if w:
                    v_walls[x] |= (1 << y)
            elif len(parts) == 4:
                x, y, d, has_wall = map(int, parts)
                if has_wall:
                    if d == 0:  # North
                        h_walls[y + 1] |= (1 << x)
                    elif d == 1:  # East
                        v_walls[x + 1] |= (1 << y)
                    elif d == 2:  # South
                        h_walls[y] |= (1 << x)
                    elif d == 3:  # West
                        v_walls[x] |= (1 << y)
    return width, height, h_walls, v_walls


def read_bin_file(filepath: str) -> Tuple[int, int, List[int], List[int]]:
    """Reads a compact .bin file and returns (width, height, h_walls, v_walls)."""
    with open(filepath, 'rb') as f:
        data = f.read()
    if len(data) < 2:
        raise ValueError("Invalid binary maze file: too short")

    width, height = data[0], data[1]
    offset = 2
    h_count = height + 1
    v_count = width + 1

    h_walls = list(struct.unpack_from(f'<{h_count}H', data, offset))
    offset += h_count * 2
    v_walls = list(struct.unpack_from(f'<{v_count}H', data, offset))
    return width, height, h_walls, v_walls


def write_bin_file(filepath: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> None:
    """Writes a compact .bin file."""
    data = bytearray([width, height])
    for val in h_walls:
        data.extend(struct.pack('<H', val))
    for val in v_walls:
        data.extend(struct.pack('<H', val))
    with open(filepath, 'wb') as f:
        f.write(data)


def write_num_file(filepath: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> None:
    """Writes an MMS .num file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for x in range(width):
            for y in range(height):
                n = 1 if (h_walls[y + 1] & (1 << x)) else 0
                e = 1 if (v_walls[x + 1] & (1 << y)) else 0
                s = 1 if (h_walls[y] & (1 << x)) else 0
                w = 1 if (v_walls[x] & (1 << y)) else 0

                f.write(f"{x} {y} 0 {n}\n")
                f.write(f"{x} {y} 1 {e}\n")
                f.write(f"{x} {y} 2 {s}\n")
                f.write(f"{x} {y} 3 {w}\n")


def generate_c_code(name: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> str:
    """Generates C CompactMaze definition."""
    h_str = ", ".join(f"0x{val:x}" for val in h_walls)
    v_str = ", ".join(f"0x{val:x}" for val in v_walls)
    return (
        f"static const CompactMaze PRESET_COMPACT_{name.upper()} = {{\n"
        f"    {width}, {height},\n"
        f"    {{ {h_str} }},\n"
        f"    {{ {v_str} }}\n"
        f"}};\n"
    )


def generate_py_code(name: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> str:
    """Generates Python CompactMaze definition."""
    h_str = ", ".join(f"0x{val:x}" for val in h_walls)
    v_str = ", ".join(f"0x{val:x}" for val in v_walls)
    return (
        f"PRESET_COMPACT_{name.upper()} = CompactMaze(\n"
        f"    {width}, {height},\n"
        f"    [{h_str}],\n"
        f"    [{v_str}]\n"
        f")\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Micromouse Maze Converter Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Convert command
    conv_parser = subparsers.add_parser("convert", help="Convert between .num, .bin, and .bmp formats")
    conv_parser.add_argument("input_file", help="Input maze file (.num, .bin, or NTF .bmp)")
    conv_parser.add_argument("output_file", help="Output maze file (.num or .bin)")

    # To C code
    c_parser = subparsers.add_parser("to-c", help="Export maze to embeddable C CompactMaze struct")
    c_parser.add_argument("input_file", help="Input maze file (.num or .bin)")
    c_parser.add_argument("--name", default="CUSTOM", help="Identifier name for the preset")

    # To Python code
    py_parser = subparsers.add_parser("to-py", help="Export maze to Python CompactMaze object")
    py_parser.add_argument("input_file", help="Input maze file (.num or .bin)")
    py_parser.add_argument("--name", default="CUSTOM", help="Identifier name for the preset")

    # Info command
    info_parser = subparsers.add_parser("info", help="Display maze metrics and storage statistics")
    info_parser.add_argument("input_file", help="Input maze file (.num or .bin)")

    args = parser.parse_args()

    # Load input
    in_ext = os.path.splitext(args.input_file)[1].lower()
    if in_ext == ".bin":
        w, h, hw, vw = read_bin_file(args.input_file)
    elif in_ext == ".num":
        w, h, hw, vw = read_num_file(args.input_file)
    elif in_ext == ".bmp":
        w, h, hw, vw = read_bmp_file(args.input_file)
    else:
        # Fallback detection
        try:
            w, h, hw, vw = read_bin_file(args.input_file)
        except Exception:
            try:
                w, h, hw, vw = read_bmp_file(args.input_file)
            except Exception:
                w, h, hw, vw = read_num_file(args.input_file)

    if args.command == "convert":
        out_ext = os.path.splitext(args.output_file)[1].lower()
        if out_ext == ".bin":
            write_bin_file(args.output_file, w, h, hw, vw)
        elif out_ext == ".num":
            write_num_file(args.output_file, w, h, hw, vw)
        else:
            print(f"Error: Unsupported output extension '{out_ext}'. Use .bin or .num")
            sys.exit(1)
        in_size = os.path.getsize(args.input_file)
        out_size = os.path.getsize(args.output_file)
        print(f"Converted '{args.input_file}' ({in_size} bytes) -> '{args.output_file}' ({out_size} bytes)")

    elif args.command == "to-c":
        print(generate_c_code(args.name, w, h, hw, vw))

    elif args.command == "to-py":
        print(generate_py_code(args.name, w, h, hw, vw))

    elif args.command == "info":
        in_size = os.path.getsize(args.input_file)
        total_cells = w * h
        h_wall_count = sum(bin(val).count("1") for val in hw)
        v_wall_count = sum(bin(val).count("1") for val in vw)
        compact_size = 2 + (h + 1) * 2 + (w + 1) * 2
        print(f"Maze Information: {args.input_file}")
        print(f"  Dimensions:        {w} x {h} ({total_cells} cells)")
        print(f"  Horizontal Walls:  {h_wall_count} segments")
        print(f"  Vertical Walls:    {v_wall_count} segments")
        print(f"  Total Wall Segs:   {h_wall_count + v_wall_count}")
        print(f"  Current File Size: {in_size} bytes")
        print(f"  Compact .bin Size: {compact_size} bytes ({100 - (compact_size / in_size * 100):.1f}% reduction)")


if __name__ == "__main__":
    main()
