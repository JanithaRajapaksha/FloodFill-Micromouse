"""
16x16 Maze UI Demonstration.
Delegates to unified interactive simulator in ui.py.
"""

from ui import run_simulation


def main() -> None:
    run_simulation(preset_name="16")


if __name__ == "__main__":
    main()
