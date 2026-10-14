import asyncio
import sys

import pygame
from os.path import dirname, join
from random import randint

# Screen
WIDTH, HEIGHT = 800, 400
GROUND_Y = 350
FPS = 60

# Colors
SKY = (135, 206, 235)
GRASS = (86, 140, 60)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)

# Player
PLAYER_SPEED = 5
JUMP_SPEED = -13
GRAVITY = 0.6
START_LIVES = 3
INVULNERABLE_MS = 1500

# Load images from the same folder as this file, so it runs from anywhere
BASE_DIR = "." if sys.platform == "emscripten" else dirname(__file__)


def load_sprite(filename, height, width=None, remove_white=False):
    """Load an image, crop the empty edges, and scale it to the given height."""
    surf = pygame.image.load(join(BASE_DIR, filename)).convert_alpha()

    if remove_white:
        # JPGs can't be transparent, so make the near-white background see-through
        background = pygame.mask.from_threshold(surf, WHITE, (40, 40, 40, 255))
        background.invert()
        surf = background.to_surface(setsurface=surf, unsetcolor=(0, 0, 0, 0))

    # The files have a lot of empty space around the picture, so crop it away
    surf = surf.subsurface(surf.get_bounding_rect()).copy()

    if width is None:
        width = round(surf.get_width() * height / surf.get_height())
    return pygame.transform.smoothscale(surf, (width, height))


def hitbox(rect):
    """A slightly smaller rect, so a near miss doesn't count as a hit."""
    return rect.inflate(-rect.width * 0.3, -rect.height * 0.2)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pony Express Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 80)

    player_surf = load_sprite("cowboy.png", 90)
    mail_surf = load_sprite("mail.jpg", 36, remove_white=True)
    pole_surf = load_sprite("pole.jpg", 70, width=22, remove_white=True)

    def spawn_mail():
        # Some mail is too high to catch without jumping
        return mail_surf.get_rect(midbottom=(WIDTH + randint(0, 200), randint(190, 330)))

    def spawn_pole():
        return pole_surf.get_rect(midbottom=(WIDTH + randint(250, 600), GROUND_Y))

    def new_round():
        player = player_surf.get_rect(midbottom=(100, GROUND_Y))
        return {
            "player": player,
            "player_vy": 0.0,
            "mail": spawn_mail(),
            "poles": [spawn_pole()],
            "score": 0,
            "lives": START_LIVES,
            "hurt_until": 0,
        }

    game = new_round()
    game_over = False

    running = True
    while running:
        await asyncio.sleep(0)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_over and event.key == pygame.K_r:
                    game = new_round()
                    game_over = False

        player = game["player"]
        mail = game["mail"]
        poles = game["poles"]

        if not game_over:
            # The game gets faster as you deliver more mail
            speed = min(4 + game["score"] // 3, 9)

            # Controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                player.x += PLAYER_SPEED
            player.x = max(0, min(player.x, WIDTH - player.width))

            # Jump and gravity
            on_ground = player.bottom >= GROUND_Y
            if on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP]):
                game["player_vy"] = JUMP_SPEED
            game["player_vy"] += GRAVITY
            player.y += round(game["player_vy"])
            if player.bottom >= GROUND_Y:
                player.bottom = GROUND_Y
                game["player_vy"] = 0.0

            # Move mail
            mail.x -= speed
            if mail.right < 0:
                game["mail"] = mail = spawn_mail()

            # Collect mail
            if hitbox(player).colliderect(mail):
                game["score"] += 1
                game["mail"] = mail = spawn_mail()

            # Move poles, and hit them
            for pole in poles[:]:
                pole.x -= speed
                if pole.right < 0:
                    poles.remove(pole)
                elif now > game["hurt_until"] and hitbox(player).colliderect(hitbox(pole)):
                    poles.remove(pole)
                    game["lives"] -= 1
                    game["hurt_until"] = now + INVULNERABLE_MS
                    if game["lives"] <= 0:
                        game_over = True

            # More poles appear as your score goes up
            while len(poles) < 1 + min(game["score"] // 5, 2):
                poles.append(spawn_pole())

        # Draw
        screen.fill(SKY)
        pygame.draw.rect(screen, GRASS, (0, GROUND_Y - 8, WIDTH, 8))
        pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        for pole in poles:
            screen.blit(pole_surf, pole)
        screen.blit(mail_surf, mail)

        # Blink while the player is protected after a hit
        blinking = now < game["hurt_until"] and (now // 100) % 2 == 0
        if not blinking:
            screen.blit(player_surf, player)

        screen.blit(font.render(f"Mail Delivered: {game['score']}", True, BLACK), (10, 10))
        screen.blit(font.render(f"Lives: {game['lives']}", True, RED), (10, 40))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            lines = [
                (big_font, "Game Over", WHITE, HEIGHT // 2 - 40),
                (font, f"Mail Delivered: {game['score']}", WHITE, HEIGHT // 2 + 20),
                (font, "R = play again   Esc = quit", WHITE, HEIGHT // 2 + 60),
            ]
            for line_font, text, color, y in lines:
                image = line_font.render(text, True, color)
                screen.blit(image, image.get_rect(center=(WIDTH // 2, y)))
        elif game["score"] == 0 and now < 5000:
            hint = font.render("Left/Right = move   Space = jump", True, BLACK)
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 80)))

        pygame.display.update()

    pygame.quit()


asyncio.run(main())
