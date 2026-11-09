"""
Flood-fill algorithm and Micromouse navigation solver.

Contains the complete algorithmic engine for:
- Breadth-First-Search (BFS) flood-fill distance calculations.
- Real-time sensor-based exploration and maze mapping.
- Optimal speed-run trajectory planning strictly restricted to explored cells.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Union

try:
    from cell import Cell, Maze, create_empty_maze
    from mouse import Mouse
    from mazes import build_preset_maze
except ImportError:
    from .cell import Cell, Maze, create_empty_maze
    from .mouse import Mouse
    from .mazes import build_preset_maze


# ============================================================================
# Core Flood-Fill Solver
# ============================================================================

def flood_fill(
    maze: Maze,
    goal_points: Union[Cell, List[Cell]],
    allowed_cells: Optional[Set[Tuple[int, int]]] = None,
) -> None:
    """
    Perform BFS flood-fill from goal cell(s) through the maze, assigning
    Manhattan distance values to each reachable cell.

    If `allowed_cells` is provided, BFS expansion is strictly restricted
    to cells within `allowed_cells` (used for speed-run planning through
    explored territory only).
    """
    q = deque()

    if hasattr(goal_points, "__iter__"):
        for goal in goal_points:
            if allowed_cells is None or (goal.x, goal.y) in allowed_cells:
                goal.value = 0
                q.append((goal, 0))
    else:
        if allowed_cells is None or (goal_points.x, goal_points.y) in allowed_cells:
            goal_points.value = 0
            q.append((goal_points, 0))

    size = maze.size
    while q:
        current_cell, dist = q.popleft()
        cx, cy = current_cell.x, current_cell.y
        next_dist = dist + 1

        # Check neighbors in fixed order: North, East, South, West
        # North
        if cy + 1 < size and not current_cell.is_north_wall:
            if allowed_cells is None or (cx, cy + 1) in allowed_cells:
                neighbor = maze[cx, cy + 1]
                if neighbor.value == -1:
                    neighbor.value = next_dist
                    q.append((neighbor, next_dist))

        # East
        if cx + 1 < size and not current_cell.is_east_wall:
            if allowed_cells is None or (cx + 1, cy) in allowed_cells:
                neighbor = maze[cx + 1, cy]
                if neighbor.value == -1:
                    neighbor.value = next_dist
                    q.append((neighbor, next_dist))

        # South
        if cy - 1 >= 0 and not current_cell.is_south_wall:
            if allowed_cells is None or (cx, cy - 1) in allowed_cells:
                neighbor = maze[cx, cy - 1]
                if neighbor.value == -1:
                    neighbor.value = next_dist
                    q.append((neighbor, next_dist))

        # West
        if cx - 1 >= 0 and not current_cell.is_west_wall:
            if allowed_cells is None or (cx - 1, cy) in allowed_cells:
                neighbor = maze[cx - 1, cy]
                if neighbor.value == -1:
                    neighbor.value = next_dist
                    q.append((neighbor, next_dist))


def compute_speed_run_path(
    empty_maze: Maze,
    goal_cells: List[Cell],
    explored_cells: Set[Tuple[int, int]],
) -> List[Tuple[int, int, int]]:
    """
    Extract the optimal speed-run trajectory from start (0, 0) to goal.

    Rule: Must strictly traverse ONLY cells that were visited during
    the exploration/search phase (explored_cells).
    """
    empty_maze.reset_values()
    flood_fill(empty_maze, goal_cells, allowed_cells=explored_cells)

    path: List[Tuple[int, int, int]] = []
    cx, cy = 0, 0
    goal_coords = {(g.x, g.y) for g in goal_cells}

    while (cx, cy) not in goal_coords:
        cur = empty_maze[cx, cy]
        if cur.value <= 0:
            break

        neighs = []
        if cy + 1 < empty_maze.size and not cur.is_north_wall and (cx, cy + 1) in explored_cells:
            neighs.append((cx, cy + 1, Mouse.NORTH))
        if cx + 1 < empty_maze.size and not cur.is_east_wall and (cx + 1, cy) in explored_cells:
            neighs.append((cx + 1, cy, Mouse.EAST))
        if cy - 1 >= 0 and not cur.is_south_wall and (cx, cy - 1) in explored_cells:
            neighs.append((cx, cy - 1, Mouse.SOUTH))
        if cx - 1 >= 0 and not cur.is_west_wall and (cx - 1, cy) in explored_cells:
            neighs.append((cx - 1, cy, Mouse.WEST))

        nxt = next((n for n in neighs if empty_maze[n[0], n[1]].value == cur.value - 1), None)
        if nxt is None:
            break

        path.append(nxt)
        cx, cy, _ = nxt

    return path


# ============================================================================
# Micromouse Algorithmic Engine (Decoupled from UI)
# ============================================================================

class MicromouseEngine:
    """
    Self-contained navigation engine for a Micromouse robot.
    Decoupled from any GUI framework.
    """

    MODE_SEARCH = "SEARCH"
    MODE_SPEED_RUN = "SPEED_RUN"

    def __init__(self, ground_truth: Maze):
        self.ground_truth = ground_truth
        self.size = ground_truth.size

        self.empty_maze = create_empty_maze(self.size)
        self.goal_cells = self.empty_maze.get_centers()
        self.mouse = Mouse(0, 0, Mouse.NORTH)

        self.explored_cells: Set[Tuple[int, int]] = {(0, 0)}
        self.mode = self.MODE_SEARCH

        self.step_count = 0
        self.search_steps = 0
        self.speed_steps = 0

        self.speed_run_path: List[Tuple[int, int, int]] = []
        self.speed_run_index = 0
        self.speed_visited: Set[Tuple[int, int]] = set()

        self.is_finished = False

        # Initial sense & flood fill
        self._sense_and_recalc()

    def reset(self) -> None:
        """Reset state machine with the current ground truth maze."""
        self.__init__(self.ground_truth)

    def _sense_and_recalc(self) -> None:
        """Sense walls at current cell, update internal map, and rerun flood fill."""
        self.mouse.update_sensors(self.ground_truth)
        self.mouse.update_maze_walls(self.empty_maze)
        self.empty_maze.reset_values()
        flood_fill(self.empty_maze, self.goal_cells)

    def start_speed_run(self) -> bool:
        """
        Transition to Phase 2: High-speed run.
        Computes the shortest path strictly through explored cells and resets
        the mouse to (0, 0) facing North.
        """
        if not self.speed_run_path:
            self.speed_run_path = compute_speed_run_path(
                self.empty_maze, self.goal_cells, self.explored_cells
            )

        if not self.speed_run_path:
            return False

        self.mode = self.MODE_SPEED_RUN
        self.mouse.x = 0
        self.mouse.y = 0
        self.mouse.orientation = Mouse.NORTH
        self.speed_run_index = 0
        self.speed_steps = 0
        self.speed_visited = {(0, 0)}
        self.is_finished = False
        return True

    def step(self) -> Dict:
        """
        Execute a single algorithmic step.
        Returns a structured event dictionary describing the step outcome.
        """
        if self.is_finished:
            return {"type": "FINISHED", "is_finished": True}

        # ---------------------------------------------------------------------
        # SPEED RUN PHASE (Strictly along explored route)
        # ---------------------------------------------------------------------
        if self.mode == self.MODE_SPEED_RUN:
            if self.speed_run_index < len(self.speed_run_path):
                nxt_x, nxt_y, nxt_orient = self.speed_run_path[self.speed_run_index]
                prev_x, prev_y = self.mouse.x, self.mouse.y

                self.mouse.x = nxt_x
                self.mouse.y = nxt_y
                self.mouse.orientation = nxt_orient
                self.speed_steps += 1
                self.speed_run_index += 1
                self.speed_visited.add((nxt_x, nxt_y))

                is_goal = (self.speed_run_index >= len(self.speed_run_path))
                if is_goal:
                    self.is_finished = True

                return {
                    "type": "SPEED_RUN_COMPLETE" if is_goal else "SPEED_RUN_STEP",
                    "mode": self.MODE_SPEED_RUN,
                    "prev_pos": (prev_x, prev_y),
                    "pos": (nxt_x, nxt_y),
                    "orientation": nxt_orient,
                    "step_num": self.speed_steps,
                    "is_finished": self.is_finished,
                    "total_speed_steps": self.speed_steps,
                    "search_steps": self.search_steps,
                }
            else:
                self.is_finished = True
                return {"type": "SPEED_RUN_COMPLETE", "is_finished": True}

        # ---------------------------------------------------------------------
        # SEARCH & EXPLORATION PHASE
        # ---------------------------------------------------------------------
        current_cell = self.empty_maze[self.mouse.x, self.mouse.y]

        # Check goal reached
        if current_cell.value == 0:
            self.is_finished = True
            self.search_steps = self.step_count
            self.speed_run_path = compute_speed_run_path(
                self.empty_maze, self.goal_cells, self.explored_cells
            )
            return {
                "type": "SEARCH_COMPLETE",
                "mode": self.MODE_SEARCH,
                "pos": (self.mouse.x, self.mouse.y),
                "orientation": self.mouse.orientation,
                "step_num": self.step_count,
                "is_finished": True,
                "search_steps": self.search_steps,
                "speed_path_length": len(self.speed_run_path),
            }

        next_val = current_cell.value - 1
        accessible_neighbors = []

        if self.mouse.y + 1 < self.size and not current_cell.is_north_wall:
            accessible_neighbors.append(self.empty_maze[self.mouse.x, self.mouse.y + 1])
        if self.mouse.x + 1 < self.size and not current_cell.is_east_wall:
            accessible_neighbors.append(self.empty_maze[self.mouse.x + 1, self.mouse.y])
        if self.mouse.y - 1 >= 0 and not current_cell.is_south_wall:
            accessible_neighbors.append(self.empty_maze[self.mouse.x, self.mouse.y - 1])
        if self.mouse.x - 1 >= 0 and not current_cell.is_west_wall:
            accessible_neighbors.append(self.empty_maze[self.mouse.x - 1, self.mouse.y])

        next_cell = next((n for n in accessible_neighbors if n.value == next_val), None)

        # Local minimum fallback: re-flood from current position
        if next_cell is None:
            self.empty_maze.reset_values()
            flood_fill(self.empty_maze, current_cell)
            accessible_neighbors.clear()
            if self.mouse.y + 1 < self.size and not current_cell.is_north_wall:
                accessible_neighbors.append(self.empty_maze[self.mouse.x, self.mouse.y + 1])
            if self.mouse.x + 1 < self.size and not current_cell.is_east_wall:
                accessible_neighbors.append(self.empty_maze[self.mouse.x + 1, self.mouse.y])
            if self.mouse.y - 1 >= 0 and not current_cell.is_south_wall:
                accessible_neighbors.append(self.empty_maze[self.mouse.x, self.mouse.y - 1])
            if self.mouse.x - 1 >= 0 and not current_cell.is_west_wall:
                accessible_neighbors.append(self.empty_maze[self.mouse.x - 1, self.mouse.y])
            next_cell = next((n for n in accessible_neighbors if n.value == next_val), None)

        if next_cell is None:
            self.is_finished = True
            return {"type": "ERROR", "message": "No path available", "is_finished": True}

        # Execute physical movement
        prev_x, prev_y = self.mouse.x, self.mouse.y
        self.mouse.update_mouse_orientation(current_cell, next_cell)
        self.mouse.move_forward()
        self.step_count += 1
        self.explored_cells.add((self.mouse.x, self.mouse.y))

        # Re-sense in new cell
        self._sense_and_recalc()

        is_goal = (self.empty_maze[self.mouse.x, self.mouse.y].value == 0)
        if is_goal:
            self.is_finished = True
            self.search_steps = self.step_count
            self.speed_run_path = compute_speed_run_path(
                self.empty_maze, self.goal_cells, self.explored_cells
            )
            return {
                "type": "SEARCH_COMPLETE",
                "mode": self.MODE_SEARCH,
                "prev_pos": (prev_x, prev_y),
                "pos": (self.mouse.x, self.mouse.y),
                "orientation": self.mouse.orientation,
                "step_num": self.step_count,
                "is_finished": True,
                "search_steps": self.search_steps,
                "speed_path_length": len(self.speed_run_path),
            }

        return {
            "type": "SEARCH_STEP",
            "mode": self.MODE_SEARCH,
            "prev_pos": (prev_x, prev_y),
            "pos": (self.mouse.x, self.mouse.y),
            "orientation": self.mouse.orientation,
            "step_num": self.step_count,
            "dist": next_cell.value,
            "is_finished": False,
        }


# ============================================================================
# Backwards-Compatible Standalone Functions
# ============================================================================

def navigate(mouse: Mouse, testing_maze: Maze, verbose: bool = True) -> List[List[int]]:
    """Legacy navigation runner maintaining backwards compatibility with tests."""
    engine = MicromouseEngine(testing_maze)
    path: List[List[int]] = []

    while not engine.is_finished:
        evt = engine.step()
        if evt["type"] in ("SEARCH_STEP", "SEARCH_COMPLETE"):
            pos = evt["pos"]
            orient = evt["orientation"]
            if verbose:
                print(f"({pos[0]}, {pos[1]})   {orient}")
            path.append([pos[0], pos[1], orient])

    if verbose and engine.is_finished:
        print(f"Goal reached at ({engine.mouse.x}, {engine.mouse.y})!")

    return path


def navigate_ui(mouse: Mouse, testing_maze: Maze) -> List[List[int]]:
    """Silent navigation wrapper returning the full path for UI consumption."""
    return navigate(mouse, testing_maze, verbose=False)
