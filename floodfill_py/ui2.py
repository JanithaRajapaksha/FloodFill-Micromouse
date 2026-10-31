import time

import pygame
import os

from cell import Cell, Maze
from mouse import Mouse as M
from floodFill import create_empty_maze, wall_arrangement_x5, wall_arrangement_x6, flood_fill, navigate, navigate_ui

WIDTH, HEIGHT = 800, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

MOVE_DISTANCE = 133

visited_cells = []


class Mouse():
    def __init__(self):
        self.x = 5
        self.y = HEIGHT - 5 - 125
        self.orientation = 0

    def set_position_and_orientation(self, x, y, orientation):
        if x == 0:
            self.x = 5
        else:
            self.x = x * MOVE_DISTANCE

        if y == 0:
            self.y = HEIGHT - 5 - 125
        else:
            self.y = HEIGHT - y * MOVE_DISTANCE - 5 - 125

        self.orientation = orientation

    # def move_up(self):
    #     self.y -= MOVE_DISTANCE
    # def move_down(self):
    #     self.y += MOVE_DISTANCE
    # def move_left(self):
    #     self.x -= MOVE_DISTANCE
    # def move_right(self):
    #     self.x += MOVE_DISTANCE
    #
    # def turn_left(self):
    #     self.orientation = (self.orientation - 1) % 4
    # def turn_right(self):
    #     self.orientation = (self.orientation + 1) % 4
    # def turn_around(self):
    #     self.turn_right()
    #     self.turn_right()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator")

MOUSE_IMAGE = pygame.image.load(os.path.join("ui_assets", "mouse.png"))
MOUSE_IMAGE = pygame.transform.scale(MOUSE_IMAGE, (WIDTH // 6, HEIGHT // 6))

m = M()
mouse = Mouse()


def make_maze(dim):
    maze = create_empty_maze(dim)
    wall_arrangement_x6(maze)
    return maze

maze = make_maze(6)

def draw_grid(dim, mouse):
    WIN.fill(GREEN)

    # Draw grid lines
    for i in range(dim):
        pygame.draw.line(WIN, BLACK, (i * WIDTH // dim, 0), (i * WIDTH // dim, HEIGHT))
        pygame.draw.line(WIN, BLACK, (0, i * HEIGHT // dim), (WIDTH, i * HEIGHT // dim))

    font = pygame.font.Font(None, 24)

    for row in maze.cells:
        for cell in row:
            cell_x = cell.x
            cell_y = dim - 1 - cell.y

            # Check if the cell is visited and color it differently
            if (cell.x, cell.y) in visited_cells:
                pygame.draw.rect(WIN, (200, 200, 255),
                                 (cell_x * WIDTH // dim, cell_y * HEIGHT // dim,
                                  WIDTH // dim, HEIGHT // dim))

            if cell.is_north_wall:
                pygame.draw.line(WIN, RED, (cell_x * WIDTH // dim, cell_y * HEIGHT // dim),
                                 ((cell_x + 1) * WIDTH // dim, cell_y * HEIGHT // dim), 6)
            if cell.is_south_wall:
                pygame.draw.line(WIN, RED, (cell_x * WIDTH // dim, (cell_y + 1) * HEIGHT // dim),
                                 ((cell_x + 1) * WIDTH // dim, (cell_y + 1) * HEIGHT // dim), 6)
            if cell.is_west_wall:
                pygame.draw.line(WIN, RED, (cell_x * WIDTH // dim, cell_y * HEIGHT // dim),
                                 (cell_x * WIDTH // dim, (cell_y + 1) * HEIGHT // dim), 4)
            if cell.is_east_wall:
                pygame.draw.line(WIN, RED, ((cell_x + 1) * WIDTH // dim, cell_y * HEIGHT // dim),
                                 ((cell_x + 1) * WIDTH // dim, (cell_y + 1) * HEIGHT // dim), 6)

            text = font.render(f"{cell_x}, {cell_y}", True, RED)
            text_rect = text.get_rect(center=(
                (cell.x * WIDTH // dim) + (WIDTH // dim) // 2,
                (cell.y * HEIGHT // dim) + (HEIGHT // dim) // 2
            ))
            WIN.blit(text, text_rect)

    # Draw the mouse at its position
    if mouse.orientation == 0:
        WIN.blit(pygame.transform.rotate(MOUSE_IMAGE, 0), (mouse.x, mouse.y))
    elif mouse.orientation == 1:
        WIN.blit(pygame.transform.rotate(MOUSE_IMAGE, -90), (mouse.x, mouse.y))
    elif mouse.orientation == 2:
        WIN.blit(pygame.transform.rotate(MOUSE_IMAGE, 180), (mouse.x, mouse.y))
    elif mouse.orientation == 3:
        WIN.blit(pygame.transform.rotate(MOUSE_IMAGE, 90), (mouse.x, mouse.y))

    pygame.display.update()

def move_mouse(mouse_pos, keys_pressed):
    if keys_pressed[pygame.K_LEFT]:
        mouse_pos[0] -= 5
    if keys_pressed[pygame.K_RIGHT]:
        mouse_pos[0] += 5
    if keys_pressed[pygame.K_UP]:
        mouse_pos[1] -= 5
    if keys_pressed[pygame.K_DOWN]:
        mouse_pos[1] += 5

def main():
    global visited_cells

    clock = pygame.time.Clock()
    run = True
    pygame.init()

    path = navigate_ui(m, maze)

    mouse.set_position_and_orientation(0, 0, 0)
    visited_cells.append((0, 0))  # Add the starting position
    draw_grid(6, mouse)
    time.sleep(1)

    for i in path:
        clock.tick(60)

        mouse.set_position_and_orientation(i[0], i[1], i[2])

        # Append the visited cell to the list
        visited_cells.append((i[0], i[1]))

        draw_grid(6, mouse)
        time.sleep(1)

    pygame.quit()

if __name__ == "__main__":
    main()
