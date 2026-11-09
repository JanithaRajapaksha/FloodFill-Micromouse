#!/usr/bin/env python3
"""
Downloads and converts all 103 historical Micromouse competition mazes
from the New Technology Foundation (NTF Japan) archive:
https://www.ntf.or.jp/mouse/history/index.html

Generates:
1. Compact .bin files (70 bytes each)
2. MMS .num files (~3.5 KB each)
for Python, C, and MMS implementations.
"""

import os
import re
import struct
import urllib.request
import concurrent.futures
from io import BytesIO
from typing import List, Tuple
from PIL import Image

BASE_URL = 'https://www.ntf.or.jp/mouse/history/index.html'
IMG_BASE_URL = 'https://www.ntf.or.jp/mouse/history/'

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_NTF_DIR = os.path.join(PROJECT_ROOT, 'mazes', 'bin', 'japan_ntf')
NUM_NTF_DIR = os.path.join(PROJECT_ROOT, 'mazes', 'num', 'japan_ntf')


def clean_name(rel_url: str) -> str:
    name = os.path.basename(rel_url)
    name = re.sub(r'\.bmp$', '', name, flags=re.I)
    name = re.sub(r'_maybe$', '', name, flags=re.I)
    name = re.sub(r'[_]+16x16$', '', name, flags=re.I)
    name = name.replace('(', '_').replace(')', '_')
    name = re.sub(r'__+', '_', name)
    name = name.strip('_')
    return name


def parse_bmp_pixels(img: Image.Image) -> Tuple[int, int, List[int], List[int]]:
    """Parse 194x194 BMP pixels into 16x16 maze bitmasks (h_walls, v_walls)."""
    pixels = img.load()
    width, height = 16, 16
    h_walls = [0] * (height + 1)
    v_walls = [0] * (width + 1)

    # Horizontal walls: r_line 16 (bottom) down to 0 (top)
    for y in range(height + 1):
        r_line = 16 - y
        y_pixel = 12 * r_line + 1
        for x in range(width):
            x_pixel = 12 * x + 6
            r, g, b = pixels[x_pixel, y_pixel][:3]
            if r > 128 and g < 60 and b < 60:
                h_walls[y] |= (1 << x)

    # Vertical walls: c_line 0 (left) to 16 (right)
    for x in range(width + 1):
        c_line = x
        x_pixel = 12 * c_line + 1
        for y in range(height):
            y_pixel = 12 * (15 - y) + 6
            r, g, b = pixels[x_pixel, y_pixel][:3]
            if r > 128 and g < 60 and b < 60:
                v_walls[x] |= (1 << y)

    return width, height, h_walls, v_walls


def write_bin(filepath: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> None:
    data = bytearray([width, height])
    for val in h_walls:
        data.extend(struct.pack('<H', val))
    for val in v_walls:
        data.extend(struct.pack('<H', val))
    with open(filepath, 'wb') as f:
        f.write(data)


def write_num(filepath: str, width: int, height: int, h_walls: List[int], v_walls: List[int]) -> None:
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


def fetch_and_convert(rel_url: str) -> Tuple[str, bool, str]:
    full_url = f"{IMG_BASE_URL}{rel_url}"
    req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
    name = clean_name(rel_url)
    try:
        data = urllib.request.urlopen(req, timeout=20).read()
        img = Image.open(BytesIO(data))
        width, height, h_walls, v_walls = parse_bmp_pixels(img)

        # Basic integrity check
        if h_walls[0] != 0xFFFF or h_walls[16] != 0xFFFF or v_walls[0] != 0xFFFF or v_walls[16] != 0xFFFF:
            return name, False, "Perimeter not closed"

        # Write directly to categorized shared directories
        write_bin(os.path.join(BIN_NTF_DIR, f"{name}.bin"), width, height, h_walls, v_walls)
        write_num(os.path.join(NUM_NTF_DIR, f"{name}.num"), width, height, h_walls, v_walls)

        return name, True, "OK"
    except Exception as e:
        return name, False, str(e)


def main():
    os.makedirs(BIN_NTF_DIR, exist_ok=True)
    os.makedirs(NUM_NTF_DIR, exist_ok=True)

    print(f"Connecting to NTF Archive: {BASE_URL}...")
    req = urllib.request.Request(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

    imgs = re.findall(r'<img\s+[^>]*src=[\'"]([^\'"]+)[\'"]', html, re.I)
    maze_rel_urls = sorted(list(set(src for src in imgs if src.endswith('.bmp'))))
    print(f"Found {len(maze_rel_urls)} unique competition maze images.")

    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_and_convert, url) for url in maze_rel_urls]
        for f in concurrent.futures.as_completed(futures):
            name, ok, msg = f.result()
            if ok:
                success_count += 1
            else:
                print(f"[FAIL] {name}: {msg}")

    print(f"\n==========================================")
    print(f"Successfully converted {success_count}/{len(maze_rel_urls)} NTF mazes!")
    print(f"Binary archive: {BIN_NTF_DIR} (.bin)")
    print(f"Text archive:   {NUM_NTF_DIR} (.num)")
    print(f"==========================================")


if __name__ == '__main__':
    main()
