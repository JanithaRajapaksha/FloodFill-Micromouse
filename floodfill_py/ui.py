"""
Unified Interactive Micromouse Flood-Fill Simulator & Visualizer (PyQt6).

Features:
- Built with PyQt6: Modern, responsive dark-themed desktop application.
- Dynamic Map Switching: Quick dropdown / buttons for presets (5x5, 6x6, 10x10, 16x16,
  example1-example5, blank) plus custom .num and .bin file loading.
- Active Fog-of-War: Unseen walls are faint/hidden, discovered walls are vibrant crimson.
- MMS-Style Terminal Console: Rich color-coded log panel with autoscroll, clear, and copy.
- Variable Speed Slider: 1 to 100 steps/sec with Play/Pause, Step, and Reset.
- Real-Time Telemetry Dashboard: Coordinates, orientation, sensor readings, and % explored.
- Visited cell tracking, goal highlights, and optional distance gradient overlay.
- Full keyboard shortcuts.
"""

import math
import os
import sys
from typing import List, Optional, Set, Tuple

# Enable local package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
    QTransform,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSlider,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cell import Cell, Maze, create_empty_maze
from mouse import Mouse
from floodFill import flood_fill
from mazes import build_preset_maze, load_bin_maze, load_num_maze


# ============================================================================
# Color Palette & QSS Styles
# ============================================================================

DARK_THEME_QSS = """
QMainWindow {
    background-color: #0B0F19;
}
QWidget {
    background-color: #0B0F19;
    color: #F1F5F9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QFrame#panel {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
}
QPushButton {
    background-color: #1F2937;
    border: 1px solid #374151;
    border-radius: 5px;
    color: #F1F5F9;
    padding: 5px 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #374151;
    border-color: #6B7280;
}
QPushButton:pressed {
    background-color: #2563EB;
}
QPushButton#primary {
    background-color: #2563EB;
    border-color: #3B82F6;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #1D4ED8;
}
QComboBox {
    background-color: #1F2937;
    border: 1px solid #374151;
    border-radius: 5px;
    color: #F1F5F9;
    padding: 4px 10px;
    min-width: 110px;
}
QComboBox:hover {
    border-color: #6B7280;
}
QComboBox QAbstractItemView {
    background-color: #1F2937;
    border: 1px solid #374151;
    selection-background-color: #2563EB;
    color: #F1F5F9;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #1F2937;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #3B82F6;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #60A5FA;
    border: 1px solid #2563EB;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}
QCheckBox {
    spacing: 6px;
    color: #E2E8F0;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #4B5563;
    background: #1F2937;
}
QCheckBox::indicator:checked {
    background: #2563EB;
    border-color: #3B82F6;
}
QProgressBar {
    background-color: #1F2937;
    border: 1px solid #374151;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    height: 14px;
}
QProgressBar::chunk {
    background-color: #10B981;
    border-radius: 3px;
}
QTextEdit#console {
    background-color: #070A10;
    border: 1px solid #1F2937;
    border-radius: 6px;
    color: #E2E8F0;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 6px;
}
"""


# ============================================================================
# Simulation State Model
# ============================================================================

class SimulationState:
    """Manages real-time step-by-step Micromouse exploration state."""

    def __init__(self, map_preset: str = "example2"):
        self.map_preset: str = map_preset
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
        self.steps_per_sec: int = 5  # Default 5 steps/sec

        self.logs: List[Tuple[str, str]] = []  # (html_line, plain_line)

        self.load_map(map_preset)

    def log(self, message: str, color_hex: str = "#94A3B8") -> None:
        """Add a color-coded log message."""
        html = f'<span style="color:{color_hex};">{message}</span>'
        self.logs.append((html, message))

    def load_map(self, preset_or_path: str) -> None:
        """Load or switch to a preset or file-based maze."""
        self.map_preset = str(preset_or_path)

        if os.path.exists(preset_or_path):
            if preset_or_path.endswith(".bin"):
                self.ground_truth = load_bin_maze(preset_or_path)
            else:
                self.ground_truth = load_num_maze(preset_or_path)
        else:
            self.ground_truth = build_preset_maze(preset_or_path)

        self.size = self.ground_truth.size
        self.empty_maze = create_empty_maze(self.size)
        self.goal_cells = self.empty_maze.get_centers()

        self.mouse = Mouse(0, 0, Mouse.NORTH)
        self.visited = {(0, 0)}
        self.step_count = 0
        self.paused = True
        self.finished = False

        self.logs.clear()
        self.log("=== MMS Micromouse Simulator Initialized ===", "#38BDF8")
        self.log(f"[INFO] Map: '{self.map_preset}' ({self.size}x{self.size})", "#94A3B8")
        self.log("[INFO] Goal located at center coordinates", "#94A3B8")

        self._sense_and_recalc()
        start_dist = self.empty_maze[0, 0].value
        self.log(f"[START] Position: (0, 0), facing NORTH, dist={start_dist}", "#38BDF8")

    def reset(self) -> None:
        """Reset exploration from beginning."""
        self.load_map(self.map_preset)

    def _sense_and_recalc(self) -> None:
        """Sense environment, update discovered map, and rerun flood fill."""
        self.mouse.update_sensors(self.ground_truth)
        self.mouse.update_maze_walls(self.empty_maze)
        self.empty_maze.reset_values()
        flood_fill(self.empty_maze, self.goal_cells)

    def step(self) -> bool:
        """Execute a single exploration step."""
        if self.finished:
            return False

        current_cell = self.empty_maze[self.mouse.x, self.mouse.y]

        if current_cell.value == 0:
            self.finished = True
            self.paused = True
            self.log(f"[SUCCESS] Goal reached at ({self.mouse.x}, {self.mouse.y}) in {self.step_count} steps!", "#4ADE80")
            return False

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

        # Local minimum fallback
        if next_cell is None:
            self.log(f"[NAV] Local minimum at ({self.mouse.x}, {self.mouse.y}). Recalculating...", "#F87171")
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
            self.log(f"[ERROR] No path available from ({self.mouse.x}, {self.mouse.y})!", "#EF4444")
            return False

        # Execute move
        prev_x, prev_y = self.mouse.x, self.mouse.y
        self.mouse.update_mouse_orientation(current_cell, next_cell)
        self.mouse.move_forward()
        self.step_count += 1
        self.visited.add((self.mouse.x, self.mouse.y))

        self._sense_and_recalc()

        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]
        orient_str = orient_names[self.mouse.orientation]
        self.log(
            f"[{self.step_count:03d}] Move: ({prev_x},{prev_y}) -> ({self.mouse.x},{self.mouse.y}) {orient_str} (d={next_cell.value})",
            "#60A5FA"
        )

        if self.empty_maze[self.mouse.x, self.mouse.y].value == 0:
            self.finished = True
            self.paused = True
            self.log(f"[SUCCESS] Goal reached at ({self.mouse.x}, {self.mouse.y}) in {self.step_count} steps!", "#4ADE80")
            return False

        return True


# ============================================================================
# Maze Canvas Widget (QPainter)
# ============================================================================

class MazeWidget(QWidget):
    """Hardware-accelerated, high-DPI canvas rendering the Micromouse grid."""

    def __init__(self, sim: SimulationState, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.sim = sim
        self.setMinimumSize(400, 400)

        # Pre-load mouse sprite asset if present
        self.mouse_pixmap: Optional[QPixmap] = None
        asset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets", "mouse.png")
        if os.path.exists(asset_path):
            try:
                self.mouse_pixmap = QPixmap(asset_path)
            except Exception:
                self.mouse_pixmap = None

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        width = self.width()
        height = self.height()
        dim = self.sim.size

        # Fit square maze in viewport with margins
        margin = 12
        available_size = min(width, height) - margin * 2
        cell_size = max(4, available_size // dim)
        grid_pixel_size = cell_size * dim

        origin_x = (width - grid_pixel_size) // 2
        origin_y = (height - grid_pixel_size) // 2

        # 1. Background Panel
        bg_rect = QRectF(origin_x - 3, origin_y - 3, grid_pixel_size + 6, grid_pixel_size + 6)
        painter.setPen(QPen(QColor("#1F2937"), 1))
        painter.setBrush(QBrush(QColor("#111827")))
        painter.drawRoundedRect(bg_rect, 4, 4)

        # Colors
        color_visited = QColor("#1E3A8A")
        color_goal = QColor("#065F46")
        color_start = QColor("#312E81")
        color_current = QColor("#2563EB")
        color_cell = QColor("#0F172A")
        color_grid = QColor("#1E293B")

        font_dist = QFont("Segoe UI", max(7, cell_size // 3))
        painter.setFont(font_dist)

        # 2. Draw Cells
        for y in range(dim):
            for x in range(dim):
                cx = origin_x + x * cell_size
                cy = origin_y + (dim - 1 - y) * cell_size
                cell_rect = QRectF(cx, cy, cell_size, cell_size)

                is_goal = (self.sim.empty_maze[x, y].value == 0) or any(g.x == x and g.y == y for g in self.sim.goal_cells)
                is_start = (x == 0 and y == 0)
                is_current = (x == self.sim.mouse.x and y == self.sim.mouse.y)
                is_visited = (x, y) in self.sim.visited

                if is_current:
                    cell_color = color_current
                elif is_goal:
                    cell_color = color_goal
                elif is_start:
                    cell_color = color_start
                elif is_visited:
                    cell_color = color_visited
                else:
                    cell_color = color_cell

                painter.setPen(QPen(color_grid, 1))
                painter.setBrush(QBrush(cell_color))
                painter.drawRect(cell_rect)

                # Distance values
                if self.sim.show_distances and (not self.sim.fog_of_war or is_visited or is_goal or is_start):
                    dist_val = self.sim.empty_maze[x, y].value
                    if dist_val >= 0:
                        txt_color = QColor("#FFFFFF") if (is_current or is_goal or is_start) else QColor("#94A3B8")
                        painter.setPen(QPen(txt_color))
                        painter.drawText(cell_rect, Qt.AlignmentFlag.AlignCenter, str(dist_val))

        # 3. Draw Walls
        wall_thick_known = max(3.0, min(6.0, cell_size / 7.0))
        wall_thick_fog = max(1.0, min(2.0, cell_size / 14.0))

        pen_known = QPen(QColor("#EF4444"), wall_thick_known, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        pen_outer = QPen(QColor("#94A3B8"), wall_thick_known, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        pen_fog = QPen(QColor("#334155"), wall_thick_fog, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

        for y in range(dim):
            for x in range(dim):
                gt_cell = self.sim.ground_truth[x, y]
                disc_cell = self.sim.empty_maze[x, y]

                x0 = origin_x + x * cell_size
                y0 = origin_y + (dim - 1 - y) * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size

                is_boundary_n = (y == dim - 1)
                is_boundary_s = (y == 0)
                is_boundary_w = (x == 0)
                is_boundary_e = (x == dim - 1)

                def draw_wall_segment(has_gt: bool, has_disc: bool, is_boundary: bool, p0: QPointF, p1: QPointF):
                    if not has_gt:
                        return
                    if has_disc or is_boundary or not self.sim.fog_of_war:
                        painter.setPen(pen_outer if is_boundary else pen_known)
                        painter.drawLine(p0, p1)
                    elif self.sim.fog_of_war:
                        painter.setPen(pen_fog)
                        painter.drawLine(p0, p1)

                # North
                draw_wall_segment(gt_cell.is_north_wall, disc_cell.is_north_wall, is_boundary_n, QPointF(x0, y0), QPointF(x1, y0))
                # South
                draw_wall_segment(gt_cell.is_south_wall, disc_cell.is_south_wall, is_boundary_s, QPointF(x0, y1), QPointF(x1, y1))
                # West
                draw_wall_segment(gt_cell.is_west_wall, disc_cell.is_west_wall, is_boundary_w, QPointF(x0, y0), QPointF(x0, y1))
                # East
                draw_wall_segment(gt_cell.is_east_wall, disc_cell.is_east_wall, is_boundary_e, QPointF(x1, y0), QPointF(x1, y1))

        # 4. Draw Mouse (Authentic MMS 2D Vector Robot: Body Pentagon + Left/Right Wheels)
        mouse_cx = origin_x + self.sim.mouse.x * cell_size + cell_size / 2.0
        mouse_cy = origin_y + (dim - 1 - self.sim.mouse.y) * cell_size + cell_size / 2.0
        mouse_size = max(16.0, cell_size * 0.76)

        rotations = {0: 0.0, 1: 90.0, 2: 180.0, 3: 270.0}
        angle_deg = rotations.get(self.sim.mouse.orientation, 0.0)

        painter.save()
        painter.translate(mouse_cx, mouse_cy)
        painter.rotate(angle_deg)

        s = mouse_size

        # Left and Right Wheels
        wheel_w = max(2.5, s * 0.14)
        wheel_h = max(6.0, s * 0.48)
        wheel_y = -wheel_h / 2.0

        painter.setPen(QPen(QColor("#0F172A"), 1.0))
        painter.setBrush(QBrush(QColor("#1E293B")))
        # Left wheel
        painter.drawRoundedRect(QRectF(-s * 0.44, wheel_y, wheel_w, wheel_h), 1.5, 1.5)
        # Right wheel
        painter.drawRoundedRect(QRectF(s * 0.44 - wheel_w, wheel_y, wheel_w, wheel_h), 1.5, 1.5)

        # Body Pentagon with Pointed Nose (Exact geometry from MMS Mouse.cpp)
        body_pts = [
            QPointF(-s * 0.28, s * 0.32),   # Back-left
            QPointF(-s * 0.28, -s * 0.12),  # Front-left
            QPointF(0.0, -s * 0.44),        # Pointed Nose (Heading)
            QPointF(s * 0.28, -s * 0.12),   # Front-right
            QPointF(s * 0.28, s * 0.32),    # Back-right
        ]
        body_poly = QPolygonF(body_pts)
        painter.setPen(QPen(QColor("#38BDF8"), 1.5))
        painter.setBrush(QBrush(QColor("#0284C7")))
        painter.drawPolygon(body_poly)

        # Center Status LED
        led_color = QColor("#4ADE80") if not self.sim.finished else QColor("#FCD34D")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(led_color))
        painter.drawEllipse(QPointF(0.0, -s * 0.12), max(2.0, s * 0.09), max(2.0, s * 0.09))

        painter.restore()


# ============================================================================
# Main Application Window (PyQt6)
# ============================================================================

class MainWindow(QMainWindow):
    """Modern Desktop Window for Micromouse Navigation and Benchmarking."""

    def __init__(self, initial_preset: str = "example2"):
        super().__init__()
        self.setWindowTitle("Micromouse Flood-Fill Simulator (PyQt6)")
        self.resize(1200, 780)
        self.setStyleSheet(DARK_THEME_QSS)

        # Set official MMS Window Icon
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets")
        icon_path = os.path.join(assets_dir, "mms_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Simulation Model
        self.sim = SimulationState(initial_preset)

        # Timer for stepping
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)

        self._init_ui()
        self._update_all()

    def _init_ui(self) -> None:
        # Central Widget & Root Layout
        root_widget = QWidget(self)
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(14, 12, 14, 12)
        root_layout.setSpacing(10)

        # Top Control Bar
        top_bar = self._create_top_bar()
        root_layout.addWidget(top_bar)

        # Splitter: Left = Maze View, Right = Telemetry & Terminal Console
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # Left Canvas
        self.maze_widget = MazeWidget(self.sim, self)
        splitter.addWidget(self.maze_widget)
        splitter.setStretchFactor(0, 3)

        # Right Panel
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 2)

        root_layout.addWidget(splitter, stretch=1)

    def _create_top_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Map Selector
        layout.addWidget(QLabel("<b>Map:</b>"))
        self.combo_map = QComboBox()
        self.preset_options = [
            ("5x5", "5"),
            ("6x6", "6"),
            ("10x10", "10"),
            ("16x16 (Ex1)", "16"),
            ("example2", "example2"),
            ("example3", "example3"),
            ("example4", "example4"),
            ("example5", "example5"),
            ("blank", "blank"),
            ("Load Custom .bin/.num...", "custom"),
        ]
        for label, val in self.preset_options:
            self.combo_map.addItem(label, val)

        idx = next((i for i, (_, val) in enumerate(self.preset_options) if val == self.sim.map_preset), 4)
        self.combo_map.setCurrentIndex(idx)
        self.combo_map.currentIndexChanged.connect(self.on_map_changed)
        layout.addWidget(self.combo_map)

        layout.addSpacing(10)

        # Play / Pause
        self.btn_play = QPushButton("Play")
        self.btn_play.setObjectName("primary")
        self.btn_play.setFixedWidth(75)
        self.btn_play.clicked.connect(self.on_play_pause)
        layout.addWidget(self.btn_play)

        # Step
        self.btn_step = QPushButton("Step")
        self.btn_step.setFixedWidth(65)
        self.btn_step.clicked.connect(self.on_step_clicked)
        layout.addWidget(self.btn_step)

        # Reset
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedWidth(65)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        layout.addWidget(self.btn_reset)

        layout.addSpacing(10)

        # Speed Slider with MMS Turtle & Rabbit Icons
        layout.addWidget(QLabel("Speed:"))

        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets")
        turtle_path = os.path.join(assets_dir, "icons", "turtle.png")
        if os.path.exists(turtle_path):
            lbl_turtle = QLabel()
            lbl_turtle.setPixmap(QPixmap(turtle_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_turtle)

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(1, 50)  # 1 to 50 steps/sec
        self.slider_speed.setValue(self.sim.steps_per_sec)
        self.slider_speed.setFixedWidth(110)
        self.slider_speed.valueChanged.connect(self.on_speed_changed)
        layout.addWidget(self.slider_speed)

        rabbit_path = os.path.join(assets_dir, "icons", "rabbit.png")
        if os.path.exists(rabbit_path):
            lbl_rabbit = QLabel()
            lbl_rabbit.setPixmap(QPixmap(rabbit_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_rabbit)

        self.lbl_speed = QLabel(f"{self.sim.steps_per_sec}x")
        self.lbl_speed.setFixedWidth(35)
        layout.addWidget(self.lbl_speed)

        layout.addSpacing(10)

        # Open File Button
        self.btn_open = QPushButton("Open...")
        open_icon_path = os.path.join(assets_dir, "icons", "open.png")
        if os.path.exists(open_icon_path):
            self.btn_open.setIcon(QIcon(open_icon_path))
        self.btn_open.clicked.connect(self.on_open_file_dialog)
        layout.addWidget(self.btn_open)

        layout.addSpacing(6)

        # Fog of War Checkbox
        self.chk_fog = QCheckBox("Fog of War")
        self.chk_fog.setChecked(self.sim.fog_of_war)
        self.chk_fog.toggled.connect(self.on_fog_toggled)
        layout.addWidget(self.chk_fog)

        # Distances Checkbox
        self.chk_dist = QCheckBox("Distances")
        self.chk_dist.setChecked(self.sim.show_distances)
        self.chk_dist.toggled.connect(self.on_dist_toggled)
        layout.addWidget(self.chk_dist)

        layout.addStretch(1)
        return frame

    def _create_right_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Telemetry Dashboard Card
        telemetry_frame = QFrame()
        telemetry_frame.setStyleSheet("background-color: #0F172A; border-radius: 6px; padding: 6px;")
        t_layout = QGridLayout(telemetry_frame)
        t_layout.setContentsMargins(8, 8, 8, 8)
        t_layout.setSpacing(6)

        t_layout.addWidget(QLabel("<b>ROBOT TELEMETRY</b>"), 0, 0, 1, 2)

        self.lbl_status_badge = QLabel("[PAUSED]")
        self.lbl_status_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#FCD34D;")
        t_layout.addWidget(self.lbl_status_badge, 0, 2)

        t_layout.addWidget(QLabel("Coordinates:"), 1, 0)
        self.lbl_coords = QLabel("(0, 0)")
        self.lbl_coords.setStyleSheet("color:#38BDF8; font-weight:bold;")
        t_layout.addWidget(self.lbl_coords, 1, 1)

        t_layout.addWidget(QLabel("Heading:"), 1, 2)
        self.lbl_heading = QLabel("NORTH")
        self.lbl_heading.setStyleSheet("color:#60A5FA; font-weight:bold;")
        t_layout.addWidget(self.lbl_heading, 1, 3)

        t_layout.addWidget(QLabel("Steps Taken:"), 2, 0)
        self.lbl_steps = QLabel("0")
        self.lbl_steps.setStyleSheet("font-weight:bold;")
        t_layout.addWidget(self.lbl_steps, 2, 1)

        t_layout.addWidget(QLabel("Sensors (F/L/R):"), 2, 2)
        self.lbl_sensors = QLabel("OPEN | WALL | OPEN")
        self.lbl_sensors.setStyleSheet("color:#FCD34D;")
        t_layout.addWidget(self.lbl_sensors, 2, 3)

        # Progress bar
        t_layout.addWidget(QLabel("Explored:"), 3, 0)
        self.progress_explored = QProgressBar()
        self.progress_explored.setRange(0, 100)
        self.progress_explored.setValue(1)
        t_layout.addWidget(self.progress_explored, 3, 1, 1, 3)

        layout.addWidget(telemetry_frame)

        # 2. Terminal Header with Actions
        terminal_header = QHBoxLayout()
        terminal_header.addWidget(QLabel("<b>MMS SIMULATOR CONSOLE</b>"))
        terminal_header.addStretch(1)

        btn_copy = QPushButton("Copy")
        btn_copy.setFixedWidth(55)
        btn_copy.clicked.connect(self.on_copy_logs)
        terminal_header.addWidget(btn_copy)

        btn_clear = QPushButton("Clear")
        btn_clear.setFixedWidth(55)
        btn_clear.clicked.connect(self.on_clear_logs)
        terminal_header.addWidget(btn_clear)

        layout.addLayout(terminal_header)

        # 3. Terminal Log Output
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        layout.addWidget(self.console, stretch=1)

        # Bottom Shortcut Hints
        hints = QLabel("Shortcuts: Space=Play | S/→=Step | R=Reset | F=Fog | D=Dist | 1-8=Map")
        hints.setStyleSheet("color:#64748B; font-size:11px;")
        layout.addWidget(hints)

        return frame

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def on_map_changed(self, idx: int) -> None:
        val = self.combo_map.itemData(idx)
        if val == "custom":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Custom Micromouse Maze", "", "Maze Files (*.bin *.num);;All Files (*.*)"
            )
            if file_path:
                self.sim.load_map(file_path)
            else:
                # Revert selection
                self.combo_map.setCurrentIndex(4)
                return
        else:
            self.sim.load_map(val)

        self._update_all()

    def on_open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Custom Micromouse Maze", "", "Maze Files (*.bin *.num);;All Files (*.*)"
        )
        if file_path:
            self.sim.load_map(file_path)
            self._update_all()

    def on_play_pause(self) -> None:
        if self.sim.finished:
            self.sim.reset()
        self.sim.paused = not self.sim.paused
        if not self.sim.paused:
            self.timer.start(int(1000 / self.sim.steps_per_sec))
        else:
            self.timer.stop()
        self._update_all()

    def on_step_clicked(self) -> None:
        self.sim.paused = True
        self.timer.stop()
        self.sim.step()
        self._update_all()

    def on_reset_clicked(self) -> None:
        self.timer.stop()
        self.sim.reset()
        self._update_all()

    def on_speed_changed(self, val: int) -> None:
        self.sim.steps_per_sec = val
        self.lbl_speed.setText(f"{val}x")
        if not self.sim.paused:
            self.timer.setInterval(int(1000 / self.sim.steps_per_sec))

    def on_fog_toggled(self, checked: bool) -> None:
        self.sim.fog_of_war = checked
        self.maze_widget.update()

    def on_dist_toggled(self, checked: bool) -> None:
        self.sim.show_distances = checked
        self.maze_widget.update()

    def on_timer_tick(self) -> None:
        if not self.sim.paused and not self.sim.finished:
            still_running = self.sim.step()
            if not still_running:
                self.timer.stop()
            self._update_all()

    def on_clear_logs(self) -> None:
        self.console.clear()
        self.sim.logs.clear()

    def on_copy_logs(self) -> None:
        text = "\n".join(plain for _, plain in self.sim.logs)
        QApplication.clipboard().setText(text)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.on_play_pause()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_S):
            self.on_step_clicked()
        elif key == Qt.Key.Key_R:
            self.on_reset_clicked()
        elif key == Qt.Key.Key_F:
            self.chk_fog.toggle()
        elif key == Qt.Key.Key_D:
            self.chk_dist.toggle()
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal, Qt.Key.Key_Up):
            self.slider_speed.setValue(min(50, self.slider_speed.value() + 2))
        elif key in (Qt.Key.Key_Minus, Qt.Key.Key_Down):
            self.slider_speed.setValue(max(1, self.slider_speed.value() - 2))
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_8:
            idx = key - Qt.Key.Key_1
            if idx < len(self.preset_options):
                self.combo_map.setCurrentIndex(idx)
        elif key == Qt.Key.Key_0:
            # Blank preset index
            self.combo_map.setCurrentIndex(8)
        else:
            super().keyPressEvent(event)

    def _update_all(self) -> None:
        # 1. Update Buttons & Labels
        if self.sim.finished:
            self.btn_play.setText("Restart")
            self.btn_play.setStyleSheet("background-color: #059669;")
            self.lbl_status_badge.setText("[FINISHED]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#4ADE80;")
        elif self.sim.paused:
            self.btn_play.setText("Play")
            self.btn_play.setStyleSheet("")
            self.lbl_status_badge.setText("[PAUSED]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#FCD34D;")
        else:
            self.btn_play.setText("Pause")
            self.btn_play.setStyleSheet("background-color: #DC2626;")
            self.lbl_status_badge.setText("[RUNNING]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#38BDF8;")

        # 2. Update Telemetry
        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]
        self.lbl_coords.setText(f"({self.sim.mouse.x}, {self.sim.mouse.y})")
        self.lbl_heading.setText(orient_names[self.sim.mouse.orientation])
        self.lbl_steps.setText(str(self.sim.step_count))

        f_txt = "WALL" if self.sim.mouse.is_on_front_sensor else "OPEN"
        l_txt = "WALL" if self.sim.mouse.is_on_left_sensor else "OPEN"
        r_txt = "WALL" if self.sim.mouse.is_on_right_sensor else "OPEN"
        self.lbl_sensors.setText(f"{f_txt} | {l_txt} | {r_txt}")

        total_cells = self.sim.size * self.sim.size
        pct = int((len(self.sim.visited) / total_cells) * 100)
        self.progress_explored.setValue(pct)
        self.progress_explored.setFormat(f"{len(self.sim.visited)}/{total_cells} cells ({pct}%)")

        # 3. Update Console Log
        html_content = "<br>".join(html for html, _ in self.sim.logs)
        self.console.setHtml(html_content)
        # Scroll to bottom
        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

        # 4. Repaint Maze Canvas
        self.maze_widget.update()


# ============================================================================
# Entrypoint Wrappers
# ============================================================================

def run_simulation(
    maze_size: int = 16,
    maze: Optional[Maze] = None,
    step_delay: float = 0.2,
    window_size: int = 800,
    preset_name: Optional[str] = None,
) -> None:
    """Entrypoint function compatible with existing callers."""
    preset = preset_name or (str(maze_size) if maze is None else "example1")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow(preset)
    window.show()
    app.exec()


def main(argv: Optional[List[str]] = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    preset = args[0] if args else "example2"
    app = QApplication(sys.argv)
    window = MainWindow(preset)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
