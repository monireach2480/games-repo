import asyncio
from os.path import join
from random import randint

import pygame

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BACKGROUND_COLOR = "lightblue"
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Drone Hunter")

# --- groups ---
all_sprites = pygame.sprite.Group()
drone_sprites = pygame.sprite.Group()
missile_sprites = pygame.sprite.Group()

# --- assets ---
drone_surf = pygame.image.load(join("images", "Drone.png")).convert_alpha()
missile_surf = pygame.image.load(join("images", "missile.png")).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
big_font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 80)
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


missile_sound = load_sound(join("audio", "missile launching.mp3"))
explosion_sound = load_sound(join("audio", "explosion.wav"))


class Jet(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale(
            pygame.image.load(join("images", "Jet.png")).convert_alpha(), (140, 90)
        )
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 300

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt

        # Keep the jet inside the window
        self.rect.clamp_ip(display_surface.get_rect())

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            Missile((all_sprites, missile_sprites), missile_surf, self.rect.midtop)
            if missile_sound:
                missile_sound.play()


class Missile(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = pygame.transform.scale(
            surf, (112, 75)
        )
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.y -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Drone(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = pygame.transform.scale(
            surf, (112, 75)
        )
        self.rect = self.image.get_frect(
            center=(randint(0, WINDOW_WIDTH), randint(-200, -100))
        )
        self.speed = randint(300, 500)

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


def collisions():
    global state, final_score
    if pygame.sprite.spritecollide(player, drone_sprites, True):
        final_score = (pygame.time.get_ticks() - round_start_time) // 100
        state = "game_over"
    for missile in missile_sprites:
        if pygame.sprite.spritecollide(missile, drone_sprites, True):
            missile.kill()
            if explosion_sound:
                explosion_sound.play()


def draw_text_center(text, font_used, color, y):
    text_surf = font_used.render(text, True, color)
    text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, y))
    display_surface.blit(text_surf, text_rect)


def reset_game():
    """Clear old sprites and start a fresh round."""
    global round_start_time
    for sprite in drone_sprites:
        sprite.kill()
    for sprite in missile_sprites:
        sprite.kill()
    player.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    round_start_time = pygame.time.get_ticks()


def display_score():
    score = (pygame.time.get_ticks() - round_start_time) // 100
    text_surf = font.render(str(score), True, "black")
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)


# --- create sprites ---
player = Jet(all_sprites)

# --- meteor spawn timer ---
drone_event = pygame.event.custom_type()
pygame.time.set_timer(drone_event, 500)

# Game states: "start", "playing", "game_over"
state = "start"
round_start_time = 0
final_score = 0


async def main():
    global state

    running = True
    last_time = pygame.time.get_ticks()

    while running:
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == drone_event and state == "playing":
                Drone((all_sprites, drone_sprites), drone_surf)

            if event.type == pygame.KEYDOWN:
                if state == "start" and event.key == pygame.K_SPACE:
                    reset_game()
                    state = "playing"
                elif state == "game_over":
                    if event.key == pygame.K_SPACE:
                        reset_game()
                        state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if state == "start":
            display_surface.fill(BACKGROUND_COLOR)
            draw_text_center("DRONE HUNTER", big_font, "darkblue", WINDOW_HEIGHT / 2 - 100)
            draw_text_center("Arrow keys to move, SPACE to shoot", font, "black", WINDOW_HEIGHT / 2)
            draw_text_center("Press SPACE to start", font, "darkred", WINDOW_HEIGHT / 2 + 80)

        elif state == "playing":
            all_sprites.update(dt)
            collisions()

            display_surface.fill(BACKGROUND_COLOR)
            all_sprites.draw(display_surface)
            display_score()

        else:
            # Game over screen
            display_surface.fill(BACKGROUND_COLOR)
            draw_text_center("GAME OVER", big_font, "darkred", WINDOW_HEIGHT / 2 - 100)
            draw_text_center(f"Score: {final_score}", font, "black", WINDOW_HEIGHT / 2)
            draw_text_center("Press SPACE to play again or ESC to exit", font, "darkblue", WINDOW_HEIGHT / 2 + 80)

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
