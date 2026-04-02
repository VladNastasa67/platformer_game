import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Platformer")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 52)

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (70, 140, 255)
GREEN = (80, 200, 120)
RED = (220, 70, 70)
YELLOW = (255, 220, 70)
BROWN = (120, 80, 40)
SKY = (150, 210, 255)
GRAY = (110, 110, 110)

GRAVITY = 0.8
PLAYER_SPEED = 6
JUMP_POWER = -16

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(screen, BROWN, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False

    def draw(self):
        if not self.collected:
            pygame.draw.ellipse(screen, YELLOW, self.rect)
            pygame.draw.ellipse(screen, BLACK, self.rect, 2)

class Enemy:
    def __init__(self, x, y, w, h, left_limit, right_limit):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = 2
        self.left_limit = left_limit
        self.right_limit = right_limit

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= self.left_limit or self.rect.right >= self.right_limit:
            self.speed *= -1

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, 40, 50)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        self.alive = True
        self.won = False

    def reset_position(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vel_x = 0
        self.vel_y = 0

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        if self.rect.top > HEIGHT:
            self.alive = False

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

platforms = [
    Platform(0, 560, 1000, 40),
    Platform(120, 470, 140, 20),
    Platform(320, 400, 160, 20),
    Platform(560, 340, 160, 20),
    Platform(780, 270, 140, 20),
    Platform(650, 470, 120, 20),
    Platform(420, 250, 100, 20),
]

coins = [
    Coin(170, 435),
    Coin(385, 365),
    Coin(620, 305),
    Coin(830, 235),
    Coin(455, 215),
]

enemies = [
    Enemy(350, 370, 40, 30, 320, 480),
    Enemy(580, 530, 40, 30, 540, 900),
]

goal = pygame.Rect(900, 210, 30, 60)

player = Player(50, 500)

def draw_text_center(text, font_obj, color, y):
    img = font_obj.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    screen.blit(img, rect)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (not player.alive or player.won):
                player = Player(50, 500)
                for coin in coins:
                    coin.collected = False

    if player.alive and not player.won:
        player.move(platforms)

        for coin in coins:
            if not coin.collected and player.rect.colliderect(coin.rect):
                coin.collected = True
                player.score += 1

        for enemy in enemies:
            enemy.update()
            if player.rect.colliderect(enemy.rect):
                player.alive = False

        if player.rect.colliderect(goal):
            if all(coin.collected for coin in coins):
                player.won = True

    screen.fill(SKY)

    for platform in platforms:
        platform.draw()

    for coin in coins:
        coin.draw()

    for enemy in enemies:
        enemy.draw()

    pygame.draw.rect(screen, GREEN, goal)
    pygame.draw.rect(screen, BLACK, goal, 2)

    player.draw()

    score_text = font.render(f"Scor: {player.score}/{len(coins)}", True, BLACK)
    screen.blit(score_text, (20, 20))

    info_text = font.render("Miscare: A/D sau sageti | Saritura: SPACE/W/UP", True, BLACK)
    screen.blit(info_text, (20, 55))

    if not player.alive:
        draw_text_center("GAME OVER", big_font, RED, HEIGHT // 2 - 20)
        draw_text_center("Apasa R pentru restart", font, BLACK, HEIGHT // 2 + 40)

    if player.won:
        draw_text_center("AI CASTIGAT!", big_font, GREEN, HEIGHT // 2 - 20)
        draw_text_center("Apasa R pentru restart", font, BLACK, HEIGHT // 2 + 40)

    if not all(coin.collected for coin in coins) and player.rect.colliderect(goal):
        draw_text_center("Colecteaza toate monedele mai intai!", font, RED, 120)

    pygame.display.flip()

pygame.quit()
sys.exit()