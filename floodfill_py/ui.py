"""
Unified Interactive Micromouse Visualizer & GUI (PyQt6).

Strictly decoupled presentation layer:
- All navigation, flood-fill, and speed-run path planning logic is handled by
  `floodFill.py` (MicromouseEngine).
- This module handles ONLY GUI rendering, Qt widgets, user controls, and log display.
"""

import math
import os
import sys
from typing import List, Optional, Set, Tuple

# Enable local package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
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

from cell import Maze
from mazes import build_preset_maze, load_bin_maze, load_num_maze
from floodFill import MicromouseEngine


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
QPushButton#speedrun {
    background-color: #B45309;
    border: 1px solid #F59E0B;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#speedrun:hover {
    background-color: #D97706;
    border-color: #FBBF24;
}
QPushButton#speedrun:pressed {
    background-color: #78350F;
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
# GUI Presentation Controller (Delegates algorithm to MicromouseEngine)
# ============================================================================

class UIController:
    """Manages GUI-specific state (speed, paused, logs) and delegates all algorithm to MicromouseEngine."""

    def __init__(self, preset_or_path: str = "example2"):
        self.preset_or_path = preset_or_path
        self.ground_truth: Maze = None
        self.engine: MicromouseEngine = None

        self.paused = True
        self.fog_of_war = True
        self.show_distances = True
        self.steps_per_sec = 5

        self.logs: List[Tuple[str, str]] = []
        self.load_map(preset_or_path)

    def log(self, message: str, color_hex: str = "#94A3B8") -> None:
        """Add a color-coded log message for display."""
        html = f'<span style="color:{color_hex};">{message}</span>'
        self.logs.append((html, message))

    def load_map(self, preset_or_path: str) -> None:
        """Load ground truth maze and initialize decoupled navigation engine."""
        self.preset_or_path = str(preset_or_path)

        if os.path.exists(preset_or_path):
            if preset_or_path.endswith(".bin"):
                self.ground_truth = load_bin_maze(preset_or_path)
            else:
                self.ground_truth = load_num_maze(preset_or_path)
        else:
            self.ground_truth = build_preset_maze(preset_or_path)

        # Delegate navigation logic to MicromouseEngine from floodFill.py
        self.engine = MicromouseEngine(self.ground_truth)
        self.paused = True

        self.logs.clear()
        self.log("=== MMS Micromouse Simulator Initialized ===", "#38BDF8")
        self.log(f"[INFO] Map: '{self.preset_or_path}' ({self.engine.size}x{self.engine.size})", "#94A3B8")
        self.log("[INFO] Phase 1: Search & Exploration Run", "#94A3B8")
        start_dist = self.engine.empty_maze[0, 0].value
        self.log(f"[START] Position: (0, 0), facing NORTH, dist={start_dist}", "#38BDF8")

    def reset(self) -> None:
        """Reset simulator state."""
        self.load_map(self.preset_or_path)

    def step(self) -> bool:
        """Call algorithm engine step and format visual logs."""
        evt = self.engine.step()
        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]

        if evt["type"] == "SEARCH_STEP":
            px, py = evt["prev_pos"]
            cx, cy = evt["pos"]
            o = orient_names[evt["orientation"]]
            d = evt["dist"]
            self.log(f"[{evt['step_num']:03d}] Move: ({px},{py}) -> ({cx},{cy}) {o} (d={d})", "#60A5FA")
            return True

        elif evt["type"] == "SEARCH_COMPLETE":
            px, py = evt.get("prev_pos", evt["pos"])
            cx, cy = evt["pos"]
            o = orient_names[evt["orientation"]]
            if "prev_pos" in evt:
                self.log(f"[{evt['step_num']:03d}] Move: ({px},{py}) -> ({cx},{cy}) {o} (d=0)", "#60A5FA")
            self.log("=========================================", "#4ADE80")
            self.log(f"[SUCCESS] Search complete! Goal reached in {evt['search_steps']} exploration steps!", "#4ADE80")
            self.log(
                f"[MEMORY] Explored-only speed-run route: {evt['speed_path_length']} steps strictly through visited cells",
                "#38BDF8"
            )
            self.log("[READY] Click 'Speed Run 🚀' or press G to execute fast sprint!", "#FCD34D")
            self.paused = True
            return False

        elif evt["type"] == "SPEED_RUN_STEP":
            px, py = evt["prev_pos"]
            cx, cy = evt["pos"]
            o = orient_names[evt["orientation"]]
            self.log(f"[{evt['step_num']:02d} 🚀] Fast Move: ({px},{py}) -> ({cx},{cy}) {o}", "#F59E0B")
            return True

        elif evt["type"] == "SPEED_RUN_COMPLETE":
            px, py = evt["prev_pos"]
            cx, cy = evt["pos"]
            o = orient_names[evt["orientation"]]
            self.log(f"[{evt['step_num']:02d} 🚀] Fast Move: ({px},{py}) -> ({cx},{cy}) {o}", "#F59E0B")
            saved = evt["search_steps"] - evt["total_speed_steps"]
            pct = (saved / max(1, evt["search_steps"])) * 100
            self.log("=========================================", "#4ADE80")
            self.log(
                f"[VICTORY 🏆] Speed Run Complete! Goal reached in {evt['total_speed_steps']} steps! "
                f"(Search took {evt['search_steps']} steps - {saved} steps / {pct:.1f}% saved!)",
                "#4ADE80"
            )
            self.paused = True
            return False

        elif evt["type"] == "ERROR":
            self.log(f"[ERROR] {evt.get('message', 'Unknown error')}", "#EF4444")
            self.paused = True
            return False

        return False

    def start_speed_run(self) -> bool:
        """Request algorithm engine to plan speed-run path strictly through explored cells and begin."""
        success = self.engine.start_speed_run()
        if success:
            self.paused = False
            self.log("=========================================", "#F59E0B")
            self.log("=== 🚀 PHASE 2: SPEED RUN LAUNCHED (MEMORY MODE) ===", "#F59E0B")
            self.log(
                f"[SPEED RUN] Driving optimal path: {len(self.engine.speed_run_path)} steps strictly through explored cells",
                "#F59E0B"
            )
        else:
            self.log("[ERROR] Cannot start speed run: no path to goal found in explored cells!", "#EF4444")
        return success


# ============================================================================
# Maze Canvas Widget (QPainter)
# ============================================================================

class MazeWidget(QWidget):
    """Hardware-accelerated canvas rendering the Micromouse grid."""

    def __init__(self, ctrl: UIController, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ctrl = ctrl
        self.setMinimumSize(400, 400)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        width = self.width()
        height = self.height()
        engine = self.ctrl.engine
        dim = engine.size

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
        color_speed_visited = QColor("#78350F")
        color_goal = QColor("#065F46")
        color_start = QColor("#312E81")
        color_current = QColor("#2563EB")
        color_speed_current = QColor("#F59E0B")
        color_cell = QColor("#0F172A")
        color_grid = QColor("#1E293B")

        font_dist = QFont("Segoe UI", max(7, cell_size // 3))
        painter.setFont(font_dist)

        is_speed_mode = (engine.mode == MicromouseEngine.MODE_SPEED_RUN)

        # 2. Draw Cells
        for y in range(dim):
            for x in range(dim):
                cx = origin_x + x * cell_size
                cy = origin_y + (dim - 1 - y) * cell_size
                cell_rect = QRectF(cx, cy, cell_size, cell_size)

                is_goal = (engine.empty_maze[x, y].value == 0) or any(g.x == x and g.y == y for g in engine.goal_cells)
                is_start = (x == 0 and y == 0)
                is_current = (x == engine.mouse.x and y == engine.mouse.y)
                is_speed_visited = (x, y) in engine.speed_visited if is_speed_mode else False
                is_visited = (x, y) in engine.explored_cells

                if is_current:
                    cell_color = color_speed_current if is_speed_mode else color_current
                elif is_speed_visited:
                    cell_color = color_speed_visited
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
                if self.ctrl.show_distances and (not self.ctrl.fog_of_war or is_visited or is_goal or is_start):
                    dist_val = engine.empty_maze[x, y].value
                    if dist_val >= 0:
                        txt_color = QColor("#FFFFFF") if (is_current or is_goal or is_start) else QColor("#94A3B8")
                        painter.setPen(QPen(txt_color))
                        painter.drawText(cell_rect, Qt.AlignmentFlag.AlignCenter, str(dist_val))

        # 3. Draw Golden Speed-Run Memory Trajectory Ribbon (Strictly Explored Path)
        if engine.speed_run_path:
            ribbon_color = QColor(245, 158, 11, 210) if is_speed_mode else QColor(245, 158, 11, 140)
            ribbon_pen = QPen(
                ribbon_color,
                max(2.5, cell_size * 0.14),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin
            )
            painter.setPen(ribbon_pen)

            p_prev = QPointF(
                origin_x + 0 * cell_size + cell_size / 2.0,
                origin_y + (dim - 1 - 0) * cell_size + cell_size / 2.0
            )
            for px, py, _ in engine.speed_run_path:
                p_curr = QPointF(
                    origin_x + px * cell_size + cell_size / 2.0,
                    origin_y + (dim - 1 - py) * cell_size + cell_size / 2.0
                )
                painter.drawLine(p_prev, p_curr)
                p_prev = p_curr

            # Corner waypoint dots
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(254, 240, 138, 220)))
            dot_rad = max(2.0, cell_size * 0.08)
            for px, py, _ in engine.speed_run_path:
                pt = QPointF(
                    origin_x + px * cell_size + cell_size / 2.0,
                    origin_y + (dim - 1 - py) * cell_size + cell_size / 2.0
                )
                painter.drawEllipse(pt, dot_rad, dot_rad)

        # 4. Draw Walls
        wall_thick_known = max(3.0, min(6.0, cell_size / 7.0))
        wall_thick_fog = max(1.0, min(2.0, cell_size / 14.0))

        pen_known = QPen(QColor("#EF4444"), wall_thick_known, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        pen_outer = QPen(QColor("#94A3B8"), wall_thick_known, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        pen_fog = QPen(QColor("#334155"), wall_thick_fog, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

        for y in range(dim):
            for x in range(dim):
                gt_cell = engine.ground_truth[x, y]
                disc_cell = engine.empty_maze[x, y]

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
                    if has_disc or is_boundary or not self.ctrl.fog_of_war:
                        painter.setPen(pen_outer if is_boundary else pen_known)
                        painter.drawLine(p0, p1)
                    elif self.ctrl.fog_of_war:
                        painter.setPen(pen_fog)
                        painter.drawLine(p0, p1)

                draw_wall_segment(gt_cell.is_north_wall, disc_cell.is_north_wall, is_boundary_n, QPointF(x0, y0), QPointF(x1, y0))
                draw_wall_segment(gt_cell.is_south_wall, disc_cell.is_south_wall, is_boundary_s, QPointF(x0, y1), QPointF(x1, y1))
                draw_wall_segment(gt_cell.is_west_wall, disc_cell.is_west_wall, is_boundary_w, QPointF(x0, y0), QPointF(x0, y1))
                draw_wall_segment(gt_cell.is_east_wall, disc_cell.is_east_wall, is_boundary_e, QPointF(x1, y0), QPointF(x1, y1))

        # 5. Draw Mouse (Procedural MMS Vector Robot Model)
        mouse_cx = origin_x + engine.mouse.x * cell_size + cell_size / 2.0
        mouse_cy = origin_y + (dim - 1 - engine.mouse.y) * cell_size + cell_size / 2.0
        mouse_size = max(16.0, cell_size * 0.76)

        rotations = {0: 0.0, 1: 90.0, 2: 180.0, 3: 270.0}
        angle_deg = rotations.get(engine.mouse.orientation, 0.0)

        painter.save()
        painter.translate(mouse_cx, mouse_cy)
        painter.rotate(angle_deg)

        s = mouse_size

        # Afterburner Thrusters (during speed run)
        if is_speed_mode and not engine.is_finished:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#EF4444")))
            painter.drawEllipse(QPointF(0.0, s * 0.44), s * 0.16, s * 0.22)
            painter.setBrush(QBrush(QColor("#FBBF24")))
            painter.drawEllipse(QPointF(0.0, s * 0.38), s * 0.10, s * 0.14)

        # Wheels
        wheel_w = max(2.5, s * 0.14)
        wheel_h = max(6.0, s * 0.48)
        wheel_y = -wheel_h / 2.0

        painter.setPen(QPen(QColor("#0F172A"), 1.0))
        painter.setBrush(QBrush(QColor("#1E293B")))
        painter.drawRoundedRect(QRectF(-s * 0.44, wheel_y, wheel_w, wheel_h), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(s * 0.44 - wheel_w, wheel_y, wheel_w, wheel_h), 1.5, 1.5)

        # Chassis Pentagon
        body_color = QColor("#D97706") if is_speed_mode else QColor("#0284C7")
        body_border = QColor("#FDE68A") if is_speed_mode else QColor("#38BDF8")

        body_pts = [
            QPointF(-s * 0.28, s * 0.32),
            QPointF(-s * 0.28, -s * 0.12),
            QPointF(0.0, -s * 0.44),
            QPointF(s * 0.28, -s * 0.12),
            QPointF(s * 0.28, s * 0.32),
        ]
        body_poly = QPolygonF(body_pts)
        painter.setPen(QPen(body_border, 1.5))
        painter.setBrush(QBrush(body_color))
        painter.drawPolygon(body_poly)

        # Center Status LED
        led_color = QColor("#F59E0B") if is_speed_mode else (QColor("#4ADE80") if not engine.is_finished else QColor("#FCD34D"))
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
        self.resize(1220, 780)
        self.setStyleSheet(DARK_THEME_QSS)

        # Set official MMS Window Icon
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets")
        icon_path = os.path.join(assets_dir, "mms_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Presentation Controller (wraps MicromouseEngine)
        self.ctrl = UIController(initial_preset)

        # Timer for stepping
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_tick)

        self._init_ui()
        self._update_all()

    def _init_ui(self) -> None:
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

        self.maze_widget = MazeWidget(self.ctrl, self)
        splitter.addWidget(self.maze_widget)
        splitter.setStretchFactor(0, 3)

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

        idx = next((i for i, (_, val) in enumerate(self.preset_options) if val == self.ctrl.preset_or_path), 4)
        self.combo_map.setCurrentIndex(idx)
        self.combo_map.currentIndexChanged.connect(self.on_map_changed)
        layout.addWidget(self.combo_map)

        layout.addSpacing(6)

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

        # Speed Run Button
        self.btn_speedrun = QPushButton("Speed Run 🚀")
        self.btn_speedrun.setObjectName("speedrun")
        self.btn_speedrun.setToolTip("Run along the discovered shortest memory path (Shortcut: G)")
        self.btn_speedrun.clicked.connect(self.on_speed_run_clicked)
        layout.addWidget(self.btn_speedrun)

        layout.addSpacing(6)

        # Speed Slider with MMS Turtle & Rabbit Icons
        layout.addWidget(QLabel("Speed:"))
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_assets")
        turtle_path = os.path.join(assets_dir, "icons", "turtle.png")
        if os.path.exists(turtle_path):
            lbl_turtle = QLabel()
            lbl_turtle.setPixmap(QPixmap(turtle_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_turtle)

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(1, 50)
        self.slider_speed.setValue(self.ctrl.steps_per_sec)
        self.slider_speed.setFixedWidth(100)
        self.slider_speed.valueChanged.connect(self.on_speed_changed)
        layout.addWidget(self.slider_speed)

        rabbit_path = os.path.join(assets_dir, "icons", "rabbit.png")
        if os.path.exists(rabbit_path):
            lbl_rabbit = QLabel()
            lbl_rabbit.setPixmap(QPixmap(rabbit_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(lbl_rabbit)

        self.lbl_speed = QLabel(f"{self.ctrl.steps_per_sec}x")
        self.lbl_speed.setFixedWidth(35)
        layout.addWidget(self.lbl_speed)

        layout.addSpacing(6)

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
        self.chk_fog.setChecked(self.ctrl.fog_of_war)
        self.chk_fog.toggled.connect(self.on_fog_toggled)
        layout.addWidget(self.chk_fog)

        # Distances Checkbox
        self.chk_dist = QCheckBox("Distances")
        self.chk_dist.setChecked(self.ctrl.show_distances)
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

        self.lbl_status_badge = QLabel("[SEARCH RUN]")
        self.lbl_status_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#38BDF8;")
        t_layout.addWidget(self.lbl_status_badge, 0, 2, 1, 2)

        t_layout.addWidget(QLabel("Coordinates:"), 1, 0)
        self.lbl_coords = QLabel("(0, 0)")
        self.lbl_coords.setStyleSheet("color:#38BDF8; font-weight:bold;")
        t_layout.addWidget(self.lbl_coords, 1, 1)

        t_layout.addWidget(QLabel("Heading:"), 1, 2)
        self.lbl_heading = QLabel("NORTH")
        self.lbl_heading.setStyleSheet("color:#60A5FA; font-weight:bold;")
        t_layout.addWidget(self.lbl_heading, 1, 3)

        t_layout.addWidget(QLabel("Steps:"), 2, 0)
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
        hints = QLabel("Shortcuts: Space=Play | G=Speed Run | S/→=Step | R=Reset | F=Fog | D=Dist | 1-8=Map")
        hints.setStyleSheet("color:#64748B; font-size:11px;")
        layout.addWidget(hints)

        return frame

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def on_map_changed(self, idx: int) -> None:
        val = self.combo_map.itemData(idx)
        if val == "custom":
            self.on_open_file_dialog()
            return
        else:
            self.ctrl.load_map(val)
        self._update_all()

    def on_open_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Custom Micromouse Maze", "", "Maze Files (*.bin *.num);;All Files (*.*)"
        )
        if file_path:
            self.ctrl.load_map(file_path)
            self._update_all()

    def on_play_pause(self) -> None:
        if self.ctrl.engine.is_finished:
            if self.ctrl.engine.mode == MicromouseEngine.MODE_SPEED_RUN:
                self.ctrl.reset()
            else:
                self.on_speed_run_clicked()
                return

        self.ctrl.paused = not self.ctrl.paused
        if not self.ctrl.paused:
            self.timer.start(int(1000 / self.ctrl.steps_per_sec))
        else:
            self.timer.stop()
        self._update_all()

    def on_step_clicked(self) -> None:
        self.ctrl.paused = True
        self.timer.stop()
        self.ctrl.step()
        self._update_all()

    def on_reset_clicked(self) -> None:
        self.timer.stop()
        self.ctrl.reset()
        self._update_all()

    def on_speed_run_clicked(self) -> None:
        """Launch high-speed sprint strictly through explored cells."""
        # If search is not finished yet, fast-forward search to completion
        if not self.ctrl.engine.speed_run_path and not self.ctrl.engine.is_finished:
            while not self.ctrl.engine.is_finished:
                self.ctrl.step()

        success = self.ctrl.start_speed_run()
        if success:
            rate = max(12, self.ctrl.steps_per_sec)
            self.timer.start(int(1000 / rate))
        self._update_all()

    def on_speed_changed(self, val: int) -> None:
        self.ctrl.steps_per_sec = val
        self.lbl_speed.setText(f"{val}x")
        if not self.ctrl.paused:
            self.timer.setInterval(int(1000 / self.ctrl.steps_per_sec))

    def on_fog_toggled(self, checked: bool) -> None:
        self.ctrl.fog_of_war = checked
        self.maze_widget.update()

    def on_dist_toggled(self, checked: bool) -> None:
        self.ctrl.show_distances = checked
        self.maze_widget.update()

    def on_timer_tick(self) -> None:
        if not self.ctrl.paused and not self.ctrl.engine.is_finished:
            still_running = self.ctrl.step()
            if not still_running:
                self.timer.stop()
            self._update_all()

    def on_clear_logs(self) -> None:
        self.console.clear()
        self.ctrl.logs.clear()

    def on_copy_logs(self) -> None:
        text = "\n".join(plain for _, plain in self.ctrl.logs)
        QApplication.clipboard().setText(text)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key.Key_Space:
            self.on_play_pause()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_S):
            self.on_step_clicked()
        elif key == Qt.Key.Key_R:
            self.on_reset_clicked()
        elif key == Qt.Key.Key_G:
            self.on_speed_run_clicked()
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
            self.combo_map.setCurrentIndex(8)
        else:
            super().keyPressEvent(event)

    def _update_all(self) -> None:
        engine = self.ctrl.engine
        is_speed_mode = (engine.mode == MicromouseEngine.MODE_SPEED_RUN)

        # 1. Update Badges & Play Button
        if engine.is_finished:
            if is_speed_mode:
                self.btn_play.setText("Restart")
                self.btn_play.setStyleSheet("background-color: #059669;")
                self.lbl_status_badge.setText("[SPEED RUN COMPLETED 🏆]")
                self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#4ADE80;")
            else:
                self.btn_play.setText("Speed Run")
                self.btn_play.setStyleSheet("background-color: #D97706;")
                self.lbl_status_badge.setText("[READY FOR SPEED RUN 🚀]")
                self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#FBBF24;")
        elif is_speed_mode:
            self.btn_play.setText("Pause")
            self.btn_play.setStyleSheet("background-color: #DC2626;")
            self.lbl_status_badge.setText("[SPEED RUN 🚀]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#F59E0B;")
        elif self.ctrl.paused:
            self.btn_play.setText("Play")
            self.btn_play.setStyleSheet("")
            self.lbl_status_badge.setText("[PAUSED]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#FCD34D;")
        else:
            self.btn_play.setText("Pause")
            self.btn_play.setStyleSheet("background-color: #DC2626;")
            self.lbl_status_badge.setText("[SEARCHING]")
            self.lbl_status_badge.setStyleSheet("font-weight:bold; color:#38BDF8;")

        # Speed run button styling
        if is_speed_mode and not engine.is_finished:
            self.btn_speedrun.setText("Sprinting 🚀")
            self.btn_speedrun.setStyleSheet("background-color: #F59E0B; color: #000; font-weight: bold;")
        elif engine.speed_run_path:
            self.btn_speedrun.setText(f"Speed Run 🚀 ({len(engine.speed_run_path)} steps)")
            self.btn_speedrun.setStyleSheet("background-color: #D97706; color: #FFF; font-weight: bold;")
        else:
            self.btn_speedrun.setText("Speed Run 🚀")
            self.btn_speedrun.setStyleSheet("")

        # 2. Update Telemetry
        orient_names = ["NORTH", "EAST", "SOUTH", "WEST"]
        self.lbl_coords.setText(f"({engine.mouse.x}, {engine.mouse.y})")
        self.lbl_heading.setText(orient_names[engine.mouse.orientation])

        if is_speed_mode:
            saved = engine.search_steps - engine.speed_steps
            self.lbl_steps.setText(f"{engine.speed_steps} (Saved: {saved})")
        else:
            self.lbl_steps.setText(str(engine.step_count))

        f_txt = "WALL" if engine.mouse.is_on_front_sensor else "OPEN"
        l_txt = "WALL" if engine.mouse.is_on_left_sensor else "OPEN"
        r_txt = "WALL" if engine.mouse.is_on_right_sensor else "OPEN"
        self.lbl_sensors.setText(f"{f_txt} | {l_txt} | {r_txt}")

        total_cells = engine.size * engine.size
        pct = int((len(engine.explored_cells) / total_cells) * 100)
        self.progress_explored.setValue(pct)
        self.progress_explored.setFormat(f"{len(engine.explored_cells)}/{total_cells} cells ({pct}%)")

        # 3. Update Console Log
        html_content = "<br>".join(html for html, _ in self.ctrl.logs)
        self.console.setHtml(html_content)
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
