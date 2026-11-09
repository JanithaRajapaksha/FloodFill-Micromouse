"""
Standalone MMS-compatible entrypoint for the Python Micromouse flood-fill solver.
"""

import sys
import API
from cell import create_empty_maze
from mouse import Mouse
from floodFill import explore_step_mms


def log(msg: str) -> None:
    """Print diagnostics to stderr so stdout remains clean for the MMS protocol."""
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()


def main() -> None:
    log("=== MMS Micromouse Python Flood-Fill Solver Started ===")

    width = API.mazeWidth()
    height = API.mazeHeight()

    if width is None or width <= 0:
        width = 16
    if height is None or height <= 0:
        height = 16

    log(f"[INFO] Maze dimensions reported: {width} x {height}")

    maze = create_empty_maze(width, height)
    goal_cells = maze.get_centers()
    mouse = Mouse(x=0, y=0, orientation=Mouse.NORTH)

    # Initial visualization for start tile
    API.setColor(0, 0, 'c')
    API.setText(0, 0, "start")

    while True:
        # 1. Check if user pressed the simulator Reset button
        if API.wasReset():
            log("[RESET] Simulator reset acknowledged. Reinitializing state...")
            API.ackReset()
            API.clearAllColor()
            API.clearAllText()
            maze = create_empty_maze(width, height)
            goal_cells = maze.get_centers()
            mouse.reset_pose(x=0, y=0, orientation=Mouse.NORTH)
            API.setColor(0, 0, 'c')
            API.setText(0, 0, "start")
            continue

        # 2. Perform blind exploration step
        try:
            status = explore_step_mms(mouse, maze, goal_cells)
        except API.MouseCrashedError:
            log("[FAIL] Mouse crashed during movement. Halting.")
            break

        # 3. Handle termination conditions
        if status == 'GOAL_REACHED':
            log(f"[SUCCESS] Center goal reached at ({mouse.x}, {mouse.y})!")
            break

        if status == 'NO_PATH':
            log("[FAIL] No path to goal exists. Exploration halted.")
            break

    log("=== MMS Micromouse Python Solver Finished ===")


if __name__ == "__main__":
    main()
