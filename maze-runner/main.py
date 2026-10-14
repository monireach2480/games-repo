import asyncio
import random

import pygame

# List of mazes
mazes = [
    # Maze 1
    [
        ["#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", " ", " ", "G", "#"],
        ["#", "#", "#", " ", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 2
    [
        ["#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", " ", "#", " ", "G", "#"],
        ["#", " ", "#", " ", "#", " ", "#", "#"],
        ["#", " ", "#", " ", " ", " ", " ", "#"],
        ["#", " ", "#", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 3
    [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", "#", " ", " ", " ", "G", "#"],
        ["#", " ", " ", "#", " ", "#", " ", "#", "#"],
        ["#", " ", "#", "#", " ", "#", " ", " ", "#"],
        ["#", " ", " ", " ", " ", "#", "#", " ", "#"],
        ["#", "#", "#", " ", "#", "#", "#", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 4
    [
        ["#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", "#", " ", " ", "G", "#"],
        ["#", " ", "#", "#", " ", "#", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 5
    [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", " ", "#", " ", " ", "G", "#"],
        ["#", "#", "#", " ", "#", "#", " ", "#", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 6
    [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", "#", " ", "#", " ", " ", "G", "#"],
        ["#", " ", "#", " ", " ", "#", " ", "#", "#", "#"],
        ["#", " ", "#", " ", "#", " ", " ", " ", " ", "#"],
        ["#", " ", " ", " ", "#", " ", "#", "#", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 7
    [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", " ", " ", "#", " ", "G", " ", "#"],
        ["#", " ", "#", "#", " ", "#", " ", "#", " ", "#"],
        ["#", " ", "#", " ", " ", " ", " ", "#", " ", "#"],
        ["#", " ", " ", " ", "#", "#", " ", " ", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ],
    # Maze 8
    [
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        ["#", "S", " ", "#", " ", " ", "#", " ", "G", " ", "#"],
        ["#", " ", "#", " ", "#", "#", "#", " ", "#", " ", "#"],
        ["#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
        ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ],
]

# Window and tile sizes (the biggest maze is 11 columns x 8 rows)
TILE = 60
WIDTH = 11 * TILE
HEIGHT = 8 * TILE + 60

# Colors
BACKGROUND = (20, 20, 30)
WALL_COLOR = (70, 80, 120)
FLOOR_COLOR = (45, 45, 60)
GOAL_COLOR = (240, 200, 60)
PLAYER_COLOR = (80, 200, 120)
TEXT_COLOR = (230, 230, 230)
WARNING_COLOR = (240, 100, 100)

# Key -> (row change, column change)
MOVES = {
    pygame.K_w: (-1, 0),
    pygame.K_UP: (-1, 0),
    pygame.K_s: (1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_a: (0, -1),
    pygame.K_LEFT: (0, -1),
    pygame.K_d: (0, 1),
    pygame.K_RIGHT: (0, 1),
}


def new_game():
    # "S" always at [1, 1]
    return random.choice(mazes), [1, 1]


def try_move(maze, player_pos, d_row, d_col):
    """Return (new_pos, tile). A wall keeps the player where they were."""
    new_pos = [player_pos[0] + d_row, player_pos[1] + d_col]
    tile = maze[new_pos[0]][new_pos[1]]
    if tile == "#":
        return player_pos, tile
    return new_pos, tile


def draw_maze(screen, maze, player_pos):
    # Center the maze in the window
    offset_x = (WIDTH - len(maze[0]) * TILE) // 2
    offset_y = (HEIGHT - 60 - len(maze) * TILE) // 2

    for r in range(len(maze)):
        for c in range(len(maze[r])):
            rect = pygame.Rect(offset_x + c * TILE, offset_y + r * TILE, TILE, TILE)
            if maze[r][c] == "#":
                pygame.draw.rect(screen, WALL_COLOR, rect)
            else:
                pygame.draw.rect(screen, FLOOR_COLOR, rect)
            if maze[r][c] == "G":
                pygame.draw.rect(screen, GOAL_COLOR, rect.inflate(-20, -20))
            if [r, c] == player_pos:
                pygame.draw.circle(screen, PLAYER_COLOR, rect.center, TILE // 3)


def draw_text(screen, font, text, color, center):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Runner")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 72)

    maze, player_pos = new_game()
    won = False
    wall_message_until = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif won:
                    if event.key == pygame.K_r:
                        maze, player_pos = new_game()
                        won = False
                elif event.key in MOVES:
                    d_row, d_col = MOVES[event.key]
                    player_pos, tile = try_move(maze, player_pos, d_row, d_col)
                    if tile == "#":
                        wall_message_until = pygame.time.get_ticks() + 800
                    elif tile == "G":
                        won = True

        screen.fill(BACKGROUND)
        draw_maze(screen, maze, player_pos)

        hint_center = (WIDTH // 2, HEIGHT - 30)
        if won:
            draw_text(
                screen, big_font, "You win!", GOAL_COLOR, (WIDTH // 2, HEIGHT // 2)
            )
            draw_text(
                screen, font, "R = new maze   Esc = quit", TEXT_COLOR, hint_center
            )
        elif pygame.time.get_ticks() < wall_message_until:
            draw_text(screen, font, "You hit a wall!", WARNING_COLOR, hint_center)
        else:
            draw_text(
                screen, font, "WASD / arrow keys to move", TEXT_COLOR, hint_center
            )

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
