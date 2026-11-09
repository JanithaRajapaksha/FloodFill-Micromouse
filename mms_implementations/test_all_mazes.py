"""
Test suite validating both C and Python flood-fill algorithms across all test mazes:
- MMS .num test mazes: blank, example1, example2, example3, example4, example5
- Classic benchmark presets: 5x5, 6x6, 10x10, 16x16
"""

import os
import sys
import subprocess

# Add python implementation to module path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PY_DIR = os.path.join(SCRIPT_DIR, "python")
C_DIR = os.path.join(SCRIPT_DIR, "c")
MAZES_DIR = os.path.join(SCRIPT_DIR, "mazes")

sys.path.insert(0, PY_DIR)
from mazes import load_num_maze, get_mms_preset_maze, build_preset_maze
from cell import Maze, create_empty_maze
from mouse import Mouse
from floodFill import flood_fill


class StandaloneSim:
    """Mock MMS simulator communicating via stdin/stdout."""
    def __init__(self, maze: Maze):
        self.maze = maze
        self.width = maze.width
        self.height = maze.height
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.moves = 0
        self.turns = 0

    def run(self, cmd: list, cwd: str, max_steps: int = 1500):
        proc = subprocess.Popen(
            cmd, cwd=cwd,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1
        )

        centers = set()
        for c in self.maze.get_centers():
            centers.add((c.x, c.y))

        goal_reached = False

        while self.moves < max_steps:
            line = proc.stdout.readline()
            if not line:
                break
            tokens = line.strip().split()
            if not tokens:
                continue

            cname = tokens[0]
            if cname == "mazeWidth":
                proc.stdin.write(f"{self.width}\n")
                proc.stdin.flush()
            elif cname == "mazeHeight":
                proc.stdin.write(f"{self.height}\n")
                proc.stdin.flush()
            elif cname == "wasReset":
                proc.stdin.write("false\n")
                proc.stdin.flush()
            elif cname in ("wallFront", "wallLeft", "wallRight", "wallBack"):
                dir_offset = 0
                if cname == "wallRight":
                    dir_offset = 1
                elif cname == "wallBack":
                    dir_offset = 2
                elif cname == "wallLeft":
                    dir_offset = 3

                abs_dir = (self.orientation + dir_offset) % 4
                cell = self.maze[self.x, self.y]
                has_wall = cell.has_wall(abs_dir)
                proc.stdin.write("true\n" if has_wall else "false\n")
                proc.stdin.flush()
            elif cname == "turnLeft":
                self.orientation = (self.orientation - 1) % 4
                self.turns += 1
                proc.stdin.write("ack\n")
                proc.stdin.flush()
            elif cname == "turnRight":
                self.orientation = (self.orientation + 1) % 4
                self.turns += 1
                proc.stdin.write("ack\n")
                proc.stdin.flush()
            elif cname == "moveForward":
                cell = self.maze[self.x, self.y]
                if cell.has_wall(self.orientation):
                    proc.stdin.write("crash\n")
                    proc.stdin.flush()
                    break

                deltas = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                dx, dy = deltas[self.orientation]
                self.x += dx
                self.y += dy
                self.moves += 1
                proc.stdin.write("ack\n")
                proc.stdin.flush()

                if (self.x, self.y) in centers:
                    goal_reached = True

        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)
        return {
            "goal_reached": goal_reached,
            "final_pos": (self.x, self.y),
            "moves": self.moves,
            "turns": self.turns
        }


def main():
    print("=" * 60)
    print("     TESTING ALGORITHMS AGAINST MMS .NUM TEST MAZES     ")
    print("=" * 60)

    num_files = [
        "blank.num",
        "example1.num",
        "example2.num",
        "example3.num",
        "example4.num",
        "example5.num",
    ]

    c_exe = os.path.join(C_DIR, "mouse.exe")
    py_cmd = [sys.executable, os.path.join(PY_DIR, "main.py")]

    all_passed = True

    for nfile in num_files:
        fpath = os.path.join(MAZES_DIR, nfile)
        maze = load_num_maze(fpath)
        print(f"\n[MAZE] {nfile} ({maze.width}x{maze.height}):")

        # Test C
        sim_c = StandaloneSim(maze)
        rc = sim_c.run([c_exe], cwd=C_DIR)

        # Test Python
        sim_py = StandaloneSim(maze)
        rpy = sim_py.run(py_cmd, cwd=PY_DIR)

        print(f"  C:      Goal={rc['goal_reached']}, Pos={rc['final_pos']}, Moves={rc['moves']}, Turns={rc['turns']}")
        print(f"  Python: Goal={rpy['goal_reached']}, Pos={rpy['final_pos']}, Moves={rpy['moves']}, Turns={rpy['turns']}")

        if rc['goal_reached'] and rpy['goal_reached'] and rc['moves'] == rpy['moves'] and rc['turns'] == rpy['turns']:
            print(f"  => PASS (100% exact parity: {rc['moves']} moves, {rc['turns']} turns)")
        else:
            print("  => FAIL")
            all_passed = False

    print("\n" + "=" * 60)
    print("   TESTING CLASSIC PRESET BENCHMARKS (5x5, 6x6, 10x10)   ")
    print("=" * 60)

    for dim in [5, 6, 10]:
        maze = build_preset_maze(dim)
        print(f"\n[BENCHMARK] {dim}x{dim}:")

        # Test C
        sim_c = StandaloneSim(maze)
        rc = sim_c.run([c_exe], cwd=C_DIR)

        # Test Python
        sim_py = StandaloneSim(maze)
        rpy = sim_py.run(py_cmd, cwd=PY_DIR)

        print(f"  C:      Goal={rc['goal_reached']}, Pos={rc['final_pos']}, Moves={rc['moves']}, Turns={rc['turns']}")
        print(f"  Python: Goal={rpy['goal_reached']}, Pos={rpy['final_pos']}, Moves={rpy['moves']}, Turns={rpy['turns']}")

        if rc['goal_reached'] and rpy['goal_reached'] and rc['moves'] == rpy['moves'] and rc['turns'] == rpy['turns']:
            print(f"  => PASS (100% exact parity: {rc['moves']} moves, {rc['turns']} turns)")
        else:
            print("  => FAIL")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("         ALL TEST MAZES PASSED WITH 100% PARITY!        ")
    else:
        print("                   SOME TESTS FAILED!                   ")
    print("=" * 60)


if __name__ == "__main__":
    main()
