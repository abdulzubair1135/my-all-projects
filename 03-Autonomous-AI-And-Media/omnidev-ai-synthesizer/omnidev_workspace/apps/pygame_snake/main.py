"""
Pixel Snake Blaster - Built by OmniDev AI Game Factory
Engine: Python 3 + Pygame
"""
import pygame
import random
import math
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Snake Blaster")
clock = pygame.time.Clock()

# Colors
BLACK = (3, 7, 18)
WHITE = (248, 250, 252)
CYAN = (56, 189, 248)
RED = (239, 68, 68)
PURPLE = (192, 132, 252)
ORANGE = (249, 115, 22)

# Player
player_x = WIDTH // 2
player_y = HEIGHT - 80
player_speed = 6
player_shield = 100
score = 0
wave = 1

bullets = []
enemies = []
particles = []
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(70)]

running = True
game_state = "PLAYING"

def spawn_enemy():
    enemies.append({"x": random.randint(30, WIDTH - 30), "y": -30, "speed": random.uniform(2, 4 + wave * 0.3), "hp": 2, "r": random.randint(14, 20)})

spawn_timer = 0

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == "PLAYING":
                bullets.append({"x": player_x, "y": player_y - 15, "vy": -10})
            elif event.key == pygame.K_r and game_state == "GAMEOVER":
                game_state = "PLAYING"
                score = 0; wave = 1; player_shield = 100
                bullets.clear(); enemies.clear(); particles.clear()

    keys = pygame.key.get_pressed()
    if game_state == "PLAYING":
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_y += player_speed
        player_x = max(20, min(WIDTH - 20, player_x))
        player_y = max(30, min(HEIGHT - 30, player_y))

        # Enemy Spawning
        spawn_timer += 1
        if spawn_timer >= max(20, 60 - wave * 5):
            spawn_enemy()
            spawn_timer = 0

        # Update bullets
        for b in bullets[:]:
            b["y"] += b["vy"]
            if b["y"] < -20: bullets.remove(b)

        # Update enemies
        for e in enemies[:]:
            e["y"] += e["speed"]
            # Bullet collision
            for b in bullets[:]:
                if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["r"] + 4:
                    if b in bullets: bullets.remove(b)
                    e["hp"] -= 1
                    if e["hp"] <= 0:
                        if e in enemies: enemies.remove(e)
                        score += 50
                        if score >= wave * 500: wave += 1
                        for _ in range(12):
                            particles.append({"x": e["x"], "y": e["y"], "vx": random.uniform(-3, 3), "vy": random.uniform(-3, 3), "life": 1.0, "c": ORANGE})
                        break
            # Player collision
            if math.hypot(player_x - e["x"], player_y - e["y"]) < e["r"] + 15:
                if e in enemies: enemies.remove(e)
                player_shield -= 30
                if player_shield <= 0:
                    game_state = "GAMEOVER"

    # Draw
    screen.fill(BLACK)
    # Stars
    for i, (sx, sy, sz) in enumerate(stars):
        pygame.draw.circle(screen, WHITE, (sx, int(sy)), sz)
        stars[i] = (sx, (sy + sz * 0.8) % HEIGHT, sz)

    # Particles
    for p in particles[:]:
        p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 0.04
        if p["life"] <= 0: particles.remove(p)
        else: pygame.draw.circle(screen, p["c"], (int(p["x"]), int(p["y"])), int(p["life"] * 4))

    # Bullets
    for b in bullets:
        pygame.draw.rect(screen, CYAN, (b["x"] - 2, b["y"] - 6, 4, 12))

    # Enemies
    for e in enemies:
        pygame.draw.circle(screen, RED, (int(e["x"]), int(e["y"])), e["r"])

    # Player Ship
    if game_state == "PLAYING":
        pygame.draw.polygon(screen, WHITE, [(player_x, player_y - 20), (player_x - 15, player_y + 15), (player_x + 15, player_y + 15)])
        pygame.draw.circle(screen, CYAN, (player_x, player_y), 4)

    # HUD
    font = pygame.font.SysFont("sans-serif", 20)
    hud_surf = font.render(f"SCORE: {score}  |  WAVE: {wave}  |  SHIELD: {max(0, player_shield)}%", True, CYAN)
    screen.blit(hud_surf, (20, 20))

    if game_state == "GAMEOVER":
        go_font = pygame.font.SysFont("sans-serif", 48)
        t1 = go_font.render("MISSION FAILED", True, RED)
        t2 = font.render("Press 'R' to Redeploy", True, WHITE)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
