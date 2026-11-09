"""
Unified Interactive Micromouse Flood-Fill Simulator & Visualizer.

Features:
- Dynamic map switching (5x5, 6x6, 10x10, 16x16, MMS example1-example5, blank).
- Active Fog-of-War (unseen walls faint/hidden, discovered walls vibrant red).
- MMS-style real-time scrolling terminal log panel.
- Interactive playback controls: Play/Pause, Step, Reset, Speed Adjustment (0.5x to Max).
- Visited cell tracking, goal highlights, and optional distance gradient overlay.
- Keyboard shortcuts for all operations.
"""

import os
import sys
import time
from typing import List, Optional, Set, Tuple

# Enable local package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cell import Cell, Maze, create_empty_maze
from mouse import Mouse
from floodFill import flood_fill
from mazes import build_preset_maze, MAZE_PRESETS

try:
    import pygame
except ImportError:
    pygame = None


# ============================================================================
# Color Palette (Modern Dark / Terminal Slate Theme)
# ============================================================================

COLOR_BG = (11, 15, 25)            # Deep navy black
COLOR_PANEL = (17, 24, 39)         # Dark slate panel
COLOR_PANEL_BORDER = (31, 41, 55)  # Border gray
COLOR_GRID = (30, 41, 59)          # Subtle grid line
COLOR_CELL_BG = (15, 23, 42)       # Empty cell background

# Cells
COLOR_VISITED = (30, 58, 138)      # Blue visited tint
COLOR_CURRENT = (59, 130, 246)     # Bright electric blue
COLOR_GOAL = (5, 150, 105)         # Emerald green goal
COLOR_START = (79, 70, 229)        # Indigo start cell

# Walls
COLOR_WALL_KNOWN = (239, 68, 68)   # Solid red (discovered walls)
COLOR_WALL_FOG = (51, 65, 85)      # Faint slate (unseen / fog of war)
COLOR_WALL_OUTER = (148, 163, 184) # Light slate perimeter

# Text & Accents
COLOR_TEXT_MAIN = (241, 245, 249)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_TEXT_ACCENT = (56, 189, 248) # Cyan

# Log Tags
COLOR_LOG_INFO = (148, 163, 184)   # Slate
COLOR_LOG_STEP = (56, 189, 248)    # Cyan
COLOR_LOG_SENSE = (252, 211, 77)   # Yellow/Amber
COLOR_LOG_MOVE = (96, 165, 250)    # Soft Blue
COLOR_LOG_SUCCESS = (74, 222, 128) # Bright Green
COLOR_LOG_WARN = (248, 113, 113)   # Red


# ============================================================================
# Simulation Engine
# ============================================================================

class SimulationState:
    """Manages real-time step-by-step Micromouse exploration state."""

    SPEED_STEPS_PER_SEC = [2, 5, 10, 25, 100]  # 0.5x, 1x, 2x, 5x, Max
    SPEED_LABELS = ["0.5x", "1x", "2x", "5x", "Max"]

    def __init__(self, map_preset: str = "example2"):
        self.map_preset = map_preset
        self.ground_truth: Maze = None
        self.empty_maze: Maze = None
        self.size: int = 16
        self.mouse: Mouse = None
        self.goal_cells: List[Cell] = []
        self.visited: Set[Tuple[int, int]] = set()

        self.step_count: int = 0
        self.paused: bool = True
        self.finished: bool = False
        self.fog_of_war: bool = True
        self.show_distances: bool = True
        self.speed_idx: int = 1  # Default 1x (5 steps/sec)

        self.logs: List[Tuple[str, Tuple[int, int, int]]] = []
        self.log_scroll: int = 0

        self.load_map(map_preset)

    def log(self, message: str, color: Tuple[int, int, int] = COLOR_LOG_INFO) -> None:
        """Add an event message to the live log."""
        self.logs.append((message, color))
        # Autoscroll to bottom
        self.log_scroll = max(0, len(self.logs) - 22)

    def load_map(self, preset: str) -> None:
        """Initialize or switch to a new preset maze."""
        self.map_preset = str(preset)
        self.ground_truth = build_preset_maze(preset)
        self.size = self.ground_truth.size
        self.empty_maze = create_empty_maze(self.size)
        self.goal_cells = self.empty_maze.get_centers()

        self.mouse = Mouse(0, 0, Mouse.NORTH)
        self.visited = {(0, 0)}
        self.step_count = 0
        self.paused = True
        self.finished = False

        self.logs.clear()
        self.log(f"=== MMS Micromouse Simulator Initialized ===", COLOR_TEXT_ACCENT)
        self.log(f"[INFO] Map: '{self.map_preset}' ({self.size}x{self.size})", COLOR_LOG_INFO)
        self.log(f"[INFO] Goal located at center coordinates", COLOR_LOG_INFO)

        # Initial sense & flood fill
        self._sense_and_recalc()
        cur_cell = self.empty_maze[0, 0]
        self.log(f"[START] Position: (0, 0), facing NORTH, dist={cur_cell.value}", COLOR_LOG_STEP)

    def reset(self) -> None:
        """Reset current maze exploration from beginning."""
        self.load_map(self.map_preset)

    def _sense_and_recalc(self) -> None:
        """Read ground truth sensors, update discovered map, and rerun flood fill."""
        self.mouse.update_sensors(self.ground_truth)
        self.mouse.update_maze_walls(self.empty_maze)
        self.empty_maze.reset_values()
        flood_fill(self.empty_maze, self.goal_cells)

    def step(self) -> bool:
        """
        Execute a single exploration step.
        Returns True if simulation is ongoing, False if goal reached or blocked.
        """
        if self.finished:
            return False

        current_cell = self.empty_maze[self.mouse.x, self.mouse.y]

        # Check goal reached
        if current_cell.value == 0:
            self.finished = True
            self.paused = True
            self.log(f"[SUCCESS] Goal reached at ({self.mouse.x}, {self.mouse.y}) in {self.step_count} steps!", COLOR_LOG_SUCCESS)
            return False

        # Read sensors and update discovered maze
        f_wall = self.mouse.is_on_front_sensor
        l_wall = self.mouse.is_on_left_sensor
        r_wall = self.mouse.is_on_right_sensor

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

        # Pick neighbor along descending gradient
        next_cell = next((n for n in accessible_neighbors if n.value == next_val), None)

        # Fallback if in local minimum
        if next_cell is None:
            self.log(f"[NAV] Local minimum at ({self.mouse.x}, {self.mouse.y}). Recalculating...", COLOR_LOG_WARN)
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
            self.finished = True
            self.paused = True
            self.log(f"[ERROR] No path available from ({self.mouse.x}, {self.mouse.y})!", COLOR_LOG_WARN)
            return False

        # Execute turn and move forward
        prev_x, prev_y = self.mouse.x, self.mouse.y
        self.mouse.update_mouse_orientation(current_cell, next_cell)
        self.mouse.move_forward()
        self.step_count += 1
        self.visited.add((self.mouse.x, self.mouse.y))

        # Re-sense in new cell
        self._sense_and_recalc()

        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]
        orient_str = orient_names[self.mouse.orientation]
        self.log(
            f"[{self.step_count:03d}] Move: ({prev_x},{prev_y}) -> ({self.mouse.x},{self.mouse.y}) {orient_str} (d={next_cell.value})",
            COLOR_LOG_MOVE
        )

        if self.empty_maze[self.mouse.x, self.mouse.y].value == 0:
            self.finished = True
            self.paused = True
            self.log(f"[SUCCESS] Goal reached at ({self.mouse.x}, {self.mouse.y}) in {self.step_count} steps!", COLOR_LOG_SUCCESS)
            return False

        return True


# ============================================================================
# Interactive UI Components (Pygame)
# ============================================================================

class Button:
    """Clickable UI button with hover effects and state toggles."""

    def __init__(self, rect: Tuple[int, int, int, int], text: str, callback, active: bool = False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.active = active
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.active:
            bg_color = (37, 99, 235)       # Active blue
            border_color = (96, 165, 250)
            text_color = (255, 255, 255)
        elif self.hovered:
            bg_color = (55, 65, 81)        # Hover gray
            border_color = (148, 163, 184)
            text_color = (255, 255, 255)
        else:
            bg_color = (31, 41, 55)        # Normal dark
            border_color = (75, 85, 99)
            text_color = (209, 213, 219)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=4)

        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# ============================================================================
# Main Visualizer Application
# ============================================================================

def run_simulation(
    maze_size: int = 16,
    maze: Optional[Maze] = None,
    step_delay: float = 0.2,
    window_size: int = 800,
    preset_name: Optional[str] = None,
) -> None:
    """
    Unified entrypoint for the Micromouse graphical simulation.
    Supports backwards-compatible invocations from CLI or other modules.
    """
    if pygame is None:
        print("Pygame is not installed. Please install it with: pip install pygame")
        return

    pygame.init()
    pygame.font.init()

    # Window geometry
    WIN_WIDTH = 1180
    WIN_HEIGHT = 740
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Micromouse Flood-Fill Simulator (MMS Mode)")

    font_main = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13)
    font_bold = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
    font_title = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
    font_mono = pygame.font.SysFont("Consolas, Courier New, monospace", 12)

    # Initialize simulation state
    init_preset = preset_name or (str(maze_size) if maze is None else "example1")
    sim = SimulationState(init_preset)

    # Try loading custom mouse sprite
    mouse_asset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets", "mouse.png")
    raw_mouse_img = None
    if os.path.exists(mouse_asset_path):
        try:
            raw_mouse_img = pygame.image.load(mouse_asset_path)
        except Exception:
            raw_mouse_img = None

    # Maze render viewport
    MAZE_X = 20
    MAZE_Y = 60
    MAZE_VIEW_SIZE = 660

    # Log panel viewport
    LOG_X = 700
    LOG_Y = 60
    LOG_WIDTH = 460
    LOG_HEIGHT = 660

    # -------------------------------------------------------------------------
    # Buttons setup
    # -------------------------------------------------------------------------
    buttons: List[Button] = []

    def make_map_btn(x, y, w, h, name):
        def cb():
            sim.load_map(name)
            update_active_buttons()
        return Button((x, y, w, h), name, cb)

    # Top Bar - Presets
    map_presets = ["5", "6", "10", "16", "example2", "example3", "example4", "example5", "blank"]
    btn_x = 20
    for p in map_presets:
        label = f"{p}x{p}" if p.isdigit() else p
        btn_w = 60 if len(label) <= 5 else 74
        buttons.append(make_map_btn(btn_x, 15, btn_w, 30, p))
        btn_x += btn_w + 6

    # Action Buttons
    def toggle_play():
        if sim.finished:
            sim.reset()
        sim.paused = not sim.paused
        update_active_buttons()

    def do_step():
        sim.paused = True
        sim.step()
        update_active_buttons()

    def do_reset():
        sim.reset()
        update_active_buttons()

    def toggle_fog():
        sim.fog_of_war = not sim.fog_of_war
        update_active_buttons()

    def toggle_dist():
        sim.show_distances = not sim.show_distances
        update_active_buttons()

    def cycle_speed():
        sim.speed_idx = (sim.speed_idx + 1) % len(sim.SPEED_STEPS_PER_SEC)
        update_active_buttons()

    btn_play = Button((700, 15, 75, 30), "Play", toggle_play)
    btn_step = Button((782, 15, 65, 30), "Step", do_step)
    btn_reset = Button((854, 15, 65, 30), "Reset", do_reset)
    btn_speed = Button((926, 15, 70, 30), f"Speed", cycle_speed)
    btn_fog = Button((1003, 15, 80, 30), "Fog: ON", toggle_fog)
    btn_dist = Button((1090, 15, 70, 30), "Dist: ON", toggle_dist)

    action_buttons = [btn_play, btn_step, btn_reset, btn_speed, btn_fog, btn_dist]
    buttons.extend(action_buttons)

    def update_active_buttons():
        btn_play.text = "Pause" if not sim.paused else "Play"
        btn_play.active = not sim.paused
        btn_fog.text = f"Fog: {'ON' if sim.fog_of_war else 'OFF'}"
        btn_fog.active = sim.fog_of_war
        btn_dist.text = f"Dist: {'ON' if sim.show_distances else 'OFF'}"
        btn_dist.active = sim.show_distances
        btn_speed.text = f"{sim.SPEED_LABELS[sim.speed_idx]}"

        for b in buttons:
            if b.text in map_presets or b.text == f"{sim.map_preset}x{sim.map_preset}":
                b.active = (b.text == sim.map_preset or b.text == f"{sim.map_preset}x{sim.map_preset}")

    update_active_buttons()

    # -------------------------------------------------------------------------
    # Render Loop
    # -------------------------------------------------------------------------
    clock = pygame.time.Clock()
    last_step_time = time.time()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        now = time.time()

        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Handle button clicks
            handled = False
            for b in buttons:
                if b.handle_event(event):
                    handled = True
                    break

            if handled:
                continue

            # Keyboard Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    toggle_play()
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_s:
                    do_step()
                elif event.key == pygame.K_r:
                    do_reset()
                elif event.key == pygame.K_f:
                    toggle_fog()
                elif event.key == pygame.K_d:
                    toggle_dist()
                elif event.key == pygame.K_UP or event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    sim.speed_idx = min(len(sim.SPEED_STEPS_PER_SEC) - 1, sim.speed_idx + 1)
                    update_active_buttons()
                elif event.key == pygame.K_DOWN or event.key == pygame.K_MINUS:
                    sim.speed_idx = max(0, sim.speed_idx - 1)
                    update_active_buttons()
                elif event.key == pygame.K_1:
                    sim.load_map("5"); update_active_buttons()
                elif event.key == pygame.K_2:
                    sim.load_map("6"); update_active_buttons()
                elif event.key == pygame.K_3:
                    sim.load_map("10"); update_active_buttons()
                elif event.key == pygame.K_4:
                    sim.load_map("16"); update_active_buttons()
                elif event.key == pygame.K_5:
                    sim.load_map("example2"); update_active_buttons()
                elif event.key == pygame.K_6:
                    sim.load_map("example3"); update_active_buttons()
                elif event.key == pygame.K_7:
                    sim.load_map("example4"); update_active_buttons()
                elif event.key == pygame.K_8:
                    sim.load_map("example5"); update_active_buttons()
                elif event.key == pygame.K_0:
                    sim.load_map("blank"); update_active_buttons()

            # Mouse wheel scrolling in log panel
            elif event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                if LOG_X <= mouse_pos[0] <= LOG_X + LOG_WIDTH and LOG_Y <= mouse_pos[1] <= LOG_Y + LOG_HEIGHT:
                    sim.log_scroll = max(0, min(len(sim.logs) - 1, sim.log_scroll - event.y))

        # Simulation Step Update
        if not sim.paused and not sim.finished:
            target_rate = sim.SPEED_STEPS_PER_SEC[sim.speed_idx]
            step_interval = 1.0 / target_rate
            if now - last_step_time >= step_interval:
                sim.step()
                last_step_time = now
                update_active_buttons()

        # =====================================================================
        # Rendering
        # =====================================================================
        screen.fill(COLOR_BG)

        # 1. Render Top Control Bar
        for b in buttons:
            b.draw(screen, font_main)

        # 2. Render Maze Grid
        cell_size = MAZE_VIEW_SIZE // sim.size
        actual_grid_size = cell_size * sim.size
        grid_origin_x = MAZE_X + (MAZE_VIEW_SIZE - actual_grid_size) // 2
        grid_origin_y = MAZE_Y + (MAZE_VIEW_SIZE - actual_grid_size) // 2

        # Maze Container Box
        pygame.draw.rect(
            screen,
            COLOR_PANEL,
            (grid_origin_x - 4, grid_origin_y - 4, actual_grid_size + 8, actual_grid_size + 8),
            border_radius=4
        )

        font_dist = pygame.font.SysFont("Segoe UI, Arial", max(10, cell_size // 3))

        # Draw Cells
        for y in range(sim.size):
            for x in range(sim.size):
                cx = grid_origin_x + x * cell_size
                cy = grid_origin_y + (sim.size - 1 - y) * cell_size

                cell_rect = pygame.Rect(cx, cy, cell_size, cell_size)

                # Shading based on state
                is_goal = (sim.empty_maze[x, y].value == 0) or any(g.x == x and g.y == y for g in sim.goal_cells)
                is_start = (x == 0 and y == 0)
                is_current = (x == sim.mouse.x and y == sim.mouse.y)
                is_visited = (x, y) in sim.visited

                if is_current:
                    pygame.draw.rect(screen, COLOR_CURRENT, cell_rect)
                elif is_goal:
                    pygame.draw.rect(screen, COLOR_GOAL, cell_rect)
                elif is_start:
                    pygame.draw.rect(screen, COLOR_START, cell_rect)
                elif is_visited:
                    pygame.draw.rect(screen, COLOR_VISITED, cell_rect)
                else:
                    pygame.draw.rect(screen, COLOR_CELL_BG, cell_rect)

                # Grid boundary
                pygame.draw.rect(screen, COLOR_GRID, cell_rect, 1)

                # Optional Distance Number
                if sim.show_distances and (not sim.fog_of_war or is_visited or is_goal or is_start):
                    dist_val = sim.empty_maze[x, y].value
                    if dist_val >= 0:
                        txt_col = (255, 255, 255) if (is_current or is_goal or is_start) else COLOR_TEXT_MUTED
                        dist_surf = font_dist.render(str(dist_val), True, txt_col)
                        screen.blit(dist_surf, dist_surf.get_rect(center=cell_rect.center))

        # Draw Walls
        wall_thick_known = max(3, min(6, cell_size // 8))
        wall_thick_fog = max(1, min(2, cell_size // 14))

        for y in range(sim.size):
            for x in range(sim.size):
                gt_cell = sim.ground_truth[x, y]
                disc_cell = sim.empty_maze[x, y]

                x0 = grid_origin_x + x * cell_size
                y0 = grid_origin_y + (sim.size - 1 - y) * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size

                # Outer perimeter is always solid
                is_boundary_n = (y == sim.size - 1)
                is_boundary_s = (y == 0)
                is_boundary_w = (x == 0)
                is_boundary_e = (x == sim.size - 1)

                # Helper to choose wall color
                def get_wall_style(has_gt_wall: bool, has_disc_wall: bool, is_boundary: bool):
                    if not has_gt_wall:
                        return None, 0
                    if has_disc_wall or is_boundary or not sim.fog_of_war:
                        return COLOR_WALL_KNOWN if not is_boundary else COLOR_WALL_OUTER, wall_thick_known
                    # Fog of war active & unseen: faint color
                    return COLOR_WALL_FOG, wall_thick_fog

                # North
                c, t = get_wall_style(gt_cell.is_north_wall, disc_cell.is_north_wall, is_boundary_n)
                if c: pygame.draw.line(screen, c, (x0, y0), (x1, y0), t)

                # South
                c, t = get_wall_style(gt_cell.is_south_wall, disc_cell.is_south_wall, is_boundary_s)
                if c: pygame.draw.line(screen, c, (x0, y1), (x1, y1), t)

                # West
                c, t = get_wall_style(gt_cell.is_west_wall, disc_cell.is_west_wall, is_boundary_w)
                if c: pygame.draw.line(screen, c, (x0, y0), (x0, y1), t)

                # East
                c, t = get_wall_style(gt_cell.is_east_wall, disc_cell.is_east_wall, is_boundary_e)
                if c: pygame.draw.line(screen, c, (x1, y0), (x1, y1), t)

        # Draw Mouse
        mouse_cx = grid_origin_x + sim.mouse.x * cell_size + cell_size // 2
        mouse_cy = grid_origin_y + (sim.size - 1 - sim.mouse.y) * cell_size + cell_size // 2
        mouse_scale = max(14, int(cell_size * 0.75))

        rotations = {0: 0, 1: -90, 2: 180, 3: 90}
        angle = rotations.get(sim.mouse.orientation, 0)

        if raw_mouse_img is not None:
            scaled_img = pygame.transform.scale(raw_mouse_img, (mouse_scale, mouse_scale))
            rotated_img = pygame.transform.rotate(scaled_img, angle)
            screen.blit(rotated_img, rotated_img.get_rect(center=(mouse_cx, mouse_cy)))
        else:
            # Procedural Chevron Pointer
            rad = mouse_scale // 2
            offsets = [(0, -rad), (rad * 0.75, rad), (0, rad * 0.5), (-rad * 0.75, rad)]
            # Rotate points
            pts = []
            import math
            theta = math.radians(angle)
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            for ox, oy in offsets:
                rx = ox * cos_t - oy * sin_t
                ry = ox * sin_t + oy * cos_t
                pts.append((mouse_cx + rx, mouse_cy + ry))
            pygame.draw.polygon(screen, (244, 63, 94), pts)
            pygame.draw.polygon(screen, (255, 255, 255), pts, 1)

        # 3. Render Right Terminal Log Panel
        log_panel_rect = pygame.Rect(LOG_X, LOG_Y, LOG_WIDTH, LOG_HEIGHT)
        pygame.draw.rect(screen, (9, 13, 22), log_panel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, log_panel_rect, width=1, border_radius=6)

        # Terminal Header Bar
        header_rect = pygame.Rect(LOG_X, LOG_Y, LOG_WIDTH, 34)
        pygame.draw.rect(screen, (15, 23, 42), header_rect, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (LOG_X, LOG_Y + 34), (LOG_X + LOG_WIDTH, LOG_Y + 34), 1)

        title_surf = font_bold.render("MMS SIMULATOR CONSOLE", True, COLOR_TEXT_ACCENT)
        screen.blit(title_surf, (LOG_X + 14, LOG_Y + 8))

        # Status Badge
        status_text = "FINISHED" if sim.finished else ("PAUSED" if sim.paused else "RUNNING")
        status_color = COLOR_LOG_SUCCESS if sim.finished else (COLOR_LOG_SENSE if sim.paused else COLOR_TEXT_ACCENT)
        stat_surf = font_bold.render(f"[{status_text}]", True, status_color)
        screen.blit(stat_surf, (LOG_X + LOG_WIDTH - stat_surf.get_width() - 14, LOG_Y + 8))

        # Terminal Log Entries
        line_y = LOG_Y + 44
        visible_lines = 23
        start_idx = max(0, min(sim.log_scroll, max(0, len(sim.logs) - visible_lines)))
        end_idx = min(len(sim.logs), start_idx + visible_lines)

        for i in range(start_idx, end_idx):
            msg, col = sim.logs[i]
            # Truncate if too long
            if len(msg) > 52:
                msg = msg[:49] + "..."
            txt_surf = font_mono.render(msg, True, col)
            screen.blit(txt_surf, (LOG_X + 14, line_y))
            line_y += 19

        # Dashboard / Telemetry at Bottom of Log Panel
        dash_y = LOG_Y + LOG_HEIGHT - 120
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (LOG_X, dash_y), (LOG_X + LOG_WIDTH, dash_y), 1)
        pygame.draw.rect(screen, (15, 23, 42), (LOG_X, dash_y + 1, LOG_WIDTH, 119), border_bottom_left_radius=6, border_bottom_right_radius=6)

        # Telemetry Text
        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]
        cur_orient = orient_names[sim.mouse.orientation]
        visited_pct = (len(sim.visited) / (sim.size * sim.size)) * 100

        screen.blit(font_bold.render("ROBOT TELEMETRY", True, COLOR_TEXT_MAIN), (LOG_X + 14, dash_y + 10))

        row1 = f"Position: ({sim.mouse.x}, {sim.mouse.y})  |  Heading: {cur_orient}  |  Steps: {sim.step_count}"
        row2 = f"Explored: {len(sim.visited)}/{sim.size*sim.size} cells ({visited_pct:.1f}%)"
        f_stat = "WALL" if sim.mouse.is_on_front_sensor else "OPEN"
        l_stat = "WALL" if sim.mouse.is_on_left_sensor else "OPEN"
        r_stat = "WALL" if sim.mouse.is_on_right_sensor else "OPEN"
        row3 = f"Sensors: [Front: {f_stat}] [Left: {l_stat}] [Right: {r_stat}]"

        screen.blit(font_mono.render(row1, True, COLOR_TEXT_ACCENT), (LOG_X + 14, dash_y + 36))
        screen.blit(font_mono.render(row2, True, COLOR_LOG_SUCCESS), (LOG_X + 14, dash_y + 58))
        screen.blit(font_mono.render(row3, True, COLOR_LOG_SENSE), (LOG_X + 14, dash_y + 80))

        # Bottom Hints
        hints = "Space: Pause/Play | S: Step | R: Reset | F: Fog of War | D: Distances | +/-: Speed"
        screen.blit(font_main.render(hints, True, COLOR_TEXT_MUTED), (MAZE_X, WIN_HEIGHT - 22))

        pygame.display.flip()

    pygame.quit()


def main() -> None:
    preset = "example2"
    if len(sys.argv) > 1:
        preset = sys.argv[1]
    run_simulation(preset_name=preset)


if __name__ == "__main__":
    main()
