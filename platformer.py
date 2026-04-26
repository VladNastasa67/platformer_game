import pygame
import sys
import json
import os

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Platformer")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 52)

BLACK = (20, 20, 20)
BLUE = (70, 140, 255)
GREEN = (80, 200, 120)
RED = (220, 70, 70)
YELLOW = (255, 220, 70)
BROWN = (120, 80, 40)
SKY = (150, 210, 255)
PURPLE = (160, 90, 220)
GRAY = (130, 130, 130)

GRAVITY = 0.8
PLAYER_SPEED = 6
JUMP_POWER = -16
SAVE_FILE = "save.json"

jump_sound = pygame.mixer.Sound("sounds/jump.wav")
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")
win_sound = pygame.mixer.Sound("sounds/win.wav")

jump_sound.set_volume(0.1)
coin_sound.set_volume(0.3)
gameover_sound.set_volume(0.2)
win_sound.set_volume(0.2)


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
        self.rect = pygame.Rect(x, y, 40, 50)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        self.alive = True
        self.won = False
        self.gameover_sound_played = False
        self.win_sound_played = False

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
            jump_sound.play()

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

            if not self.gameover_sound_played:
                gameover_sound.play()
                self.gameover_sound_played = True

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)


def load_level(level):
    if level == 1:
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
        start_pos = (50, 500)

    elif level == 2:
        platforms = [
            Platform(0, 560, 1000, 40),
            Platform(80, 500, 160, 20),
            Platform(240, 450, 160, 20),
            Platform(400, 390, 160, 20),
            Platform(580, 330, 160, 20),
            Platform(760, 270, 160, 20),
            Platform(600, 210, 140, 20),
            Platform(420, 170, 140, 20),
            Platform(220, 140, 140, 20),
        ]

        coins = [
            Coin(110, 465),
            Coin(270, 415),
            Coin(450, 355),
            Coin(620, 295),
            Coin(800, 235),
            Coin(630, 175),
            Coin(250, 105),
        ]

        enemies = [
            Enemy(250, 420, 40, 30, 240, 400),
            Enemy(590, 300, 40, 30, 580, 750),
            Enemy(100, 530, 40, 30, 50, 250),
        ]

        goal = pygame.Rect(240, 80, 30, 60)
        start_pos = (40, 500)

    elif level == 3:
        platforms = [
            Platform(0, 560, 1000, 40),
            Platform(50, 480, 170, 20),
            Platform(70, 380, 170, 20),
            Platform(50, 280, 170, 20),
            Platform(780, 480, 170, 20),
            Platform(750, 380, 170, 20),
            Platform(780, 280, 170, 20),
            Platform(360, 440, 280, 20),
            Platform(390, 320, 220, 20),
            Platform(420, 200, 180, 20),
        ]

        coins = [
            Coin(100, 445),
            Coin(120, 345),
            Coin(100, 245),
            Coin(830, 445),
            Coin(800, 345),
            Coin(830, 245),
            Coin(480, 405),
            Coin(480, 285),
            Coin(480, 165),
        ]

        enemies = [
            Enemy(400, 530, 40, 30, 300, 700),
            Enemy(430, 290, 40, 30, 390, 610),
            Enemy(90, 250, 40, 30, 50, 220),
            Enemy(830, 250, 40, 30, 780, 950),
        ]

        for enemy in enemies:
            enemy.speed = 1

        goal = pygame.Rect(490, 120, 30, 60)
        start_pos = (50, 500)

    elif level == 4:
        platforms = [
            Platform(0, 560, 1000, 40),
            Platform(100, 500, 150, 20),
            Platform(300, 460, 150, 20),
            Platform(520, 420, 150, 20),
            Platform(730, 380, 160, 20),
            Platform(600, 310, 160, 20),
            Platform(400, 250, 150, 20),
            Platform(200, 190, 150, 20),
            Platform(80, 130, 160, 20),
            Platform(360, 90, 180, 20),
            Platform(670, 80, 170, 20),
        ]

        coins = [
            Coin(150, 465),
            Coin(350, 425),
            Coin(570, 385),
            Coin(780, 345),
            Coin(650, 275),
            Coin(450, 215),
            Coin(250, 155),
            Coin(130, 95),
            Coin(420, 55),
            Coin(720, 45),
        ]

        enemies = [
            Enemy(330, 430, 40, 30, 300, 450),
            Enemy(550, 390, 40, 30, 520, 670),
            Enemy(630, 280, 40, 30, 600, 760),
            Enemy(230, 160, 40, 30, 200, 350),
        ]

        for enemy in enemies:
            enemy.speed = 1

        goal = pygame.Rect(735, 20, 30, 60)
        start_pos = (40, 500)

    elif level == 5:
        platforms = [
            Platform(0, 560, 260, 40),
            Platform(320, 560, 220, 40),
            Platform(600, 560, 220, 40),
            Platform(880, 560, 120, 40),
            Platform(130, 470, 150, 20),
            Platform(310, 400, 150, 20),
            Platform(500, 330, 150, 20),
            Platform(690, 260, 150, 20),
            Platform(500, 170, 150, 20),
            Platform(280, 130, 150, 20),
            Platform(70, 80, 170, 20),
        ]

        coins = [
            Coin(180, 435),
            Coin(360, 365),
            Coin(550, 295),
            Coin(740, 225),
            Coin(550, 135),
            Coin(330, 95),
            Coin(120, 45),
            Coin(900, 525),
        ]

        enemies = [
            Enemy(340, 530, 40, 30, 320, 540),
            Enemy(620, 530, 40, 30, 600, 820),
            Enemy(340, 370, 40, 30, 310, 460),
            Enemy(530, 300, 40, 30, 500, 650),
            Enemy(720, 230, 40, 30, 690, 840),
        ]

        for enemy in enemies:
            enemy.speed = 1

        goal = pygame.Rect(135, 20, 30, 60)
        start_pos = (40, 500)

    elif level == 6:
        platforms = [
            Platform(0, 560, 1000, 40),
            Platform(100, 500, 180, 20),
            Platform(360, 460, 180, 20),
            Platform(650, 500, 180, 20),
            Platform(760, 400, 170, 20),
            Platform(520, 340, 180, 20),
            Platform(270, 280, 180, 20),
            Platform(80, 210, 180, 20),
            Platform(350, 150, 220, 20),
            Platform(680, 100, 200, 20),
        ]

        coins = [
            Coin(140, 465),
            Coin(400, 425),
            Coin(700, 465),
            Coin(805, 365),
            Coin(570, 305),
            Coin(320, 245),
            Coin(130, 175),
            Coin(430, 115),
            Coin(720, 65),
            Coin(840, 65),
        ]

        enemies = []
        goal = None
        start_pos = (40, 500)

    return platforms, coins, enemies, goal, start_pos


def draw_text_center(text, font_obj, color, y):
    img = font_obj.render(text, True, color)
    rect = img.get_rect(center=(WIDTH // 2, y))
    screen.blit(img, rect)


def start_level(level):
    platforms, coins, enemies, goal, start_pos = load_level(level)
    player = Player(start_pos[0], start_pos[1])
    return platforms, coins, enemies, goal, start_pos, player


def default_scores():
    return {
        1: [0, 0, len(load_level(1)[1])],
        2: [0, 0, len(load_level(2)[1])],
        3: [0, 0, len(load_level(3)[1])],
        4: [0, 0, len(load_level(4)[1])],
        5: [0, 0, len(load_level(5)[1])],
    }


def load_save():
    if not os.path.exists(SAVE_FILE):
        return [1], default_scores(), None

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        unlocked = data.get("unlocked_levels", [1])
        scores_data = data.get("level_scores", {})
        scores = default_scores()

        for i in range(1, 6):
            key = str(i)

            if key in scores_data:
                saved = scores_data[key]

                if len(saved) == 2:
                    scores[i] = [saved[0], saved[0], saved[1]]
                else:
                    scores[i] = saved

        best_time = data.get("best_bonus_time", None)

        if 1 not in unlocked:
            unlocked.append(1)

        return unlocked, scores, best_time

    except:
        return [1], default_scores(), None


def save_progress():
    data = {
        "unlocked_levels": unlocked_levels,
        "level_scores": {
            "1": level_scores[1],
            "2": level_scores[2],
            "3": level_scores[3],
            "4": level_scores[4],
            "5": level_scores[5],
        },
        "best_bonus_time": best_bonus_time
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def reset_game():
    global unlocked_levels, level_scores, best_bonus_time, mesaj_meniu

    unlocked_levels = [1]
    level_scores = default_scores()
    best_bonus_time = None
    mesaj_meniu = "Progresul a fost resetat complet!"

    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


nivel_curent = 1
nivel_maxim = 5
nivel_bonus = 6
game_state = "menu"

unlocked_levels, level_scores, best_bonus_time = load_save()

bonus_start_time = 0
bonus_final_time = 0
mesaj_meniu = ""

platforms, coins, enemies, goal, start_pos, player = start_level(nivel_curent)

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                selected_level = None

                if event.key == pygame.K_1:
                    selected_level = 1
                elif event.key == pygame.K_2:
                    selected_level = 2
                elif event.key == pygame.K_3:
                    selected_level = 3
                elif event.key == pygame.K_4:
                    selected_level = 4
                elif event.key == pygame.K_5:
                    selected_level = 5
                elif event.key == pygame.K_b:
                    selected_level = nivel_bonus
                elif event.key == pygame.K_x:
                    reset_game()

                if selected_level is not None:
                    if selected_level == nivel_bonus:
                        nivel_curent = nivel_bonus
                        platforms, coins, enemies, goal, start_pos, player = start_level(nivel_curent)
                        bonus_start_time = pygame.time.get_ticks()
                        bonus_final_time = 0
                        mesaj_meniu = ""
                        game_state = "game"

                    elif selected_level in unlocked_levels:
                        nivel_curent = selected_level
                        platforms, coins, enemies, goal, start_pos, player = start_level(nivel_curent)
                        mesaj_meniu = ""
                        game_state = "game"

                    else:
                        mesaj_meniu = "Nivel blocat! Termina nivelul precedent."

            elif game_state == "game":
                if event.key == pygame.K_r and (not player.alive or player.won):
                    platforms, coins, enemies, goal, start_pos, player = start_level(nivel_curent)

                    if nivel_curent == nivel_bonus:
                        bonus_start_time = pygame.time.get_ticks()
                        bonus_final_time = 0

                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

    if game_state == "menu":
        screen.fill(SKY)

        draw_text_center("2D PLATFORMER", big_font, BLACK, 45)
        draw_text_center("Selecteaza nivelul:", font, BLACK, 105)

        y = 150

        for i in range(1, nivel_maxim + 1):
            last_score = level_scores[i][0]
            best_score = level_scores[i][1]
            total_score = level_scores[i][2]

            if i in unlocked_levels:
                text = f"Apasa {i} - Nivel {i} DEBLOCAT | Last: {last_score}/{total_score} | Best: {best_score}/{total_score}"
                color = BLACK
            else:
                text = f"Nivel {i} BLOCAT | Last: {last_score}/{total_score} | Best: {best_score}/{total_score}"
                color = GRAY

            draw_text_center(text, font, color, y)
            y += 40

        draw_text_center("Apasa B pentru Nivel BONUS - DEBLOCAT", font, PURPLE, y + 10)

        if best_bonus_time is not None:
            draw_text_center(f"Cel mai bun timp bonus: {best_bonus_time:.2f} secunde", font, PURPLE, y + 50)

        draw_text_center("Apasa X pentru RESET complet joc", font, RED, 500)
        draw_text_center("In joc apasa ESC pentru meniu", font, RED, 535)

        if mesaj_meniu != "":
            draw_text_center(mesaj_meniu, font, RED, 565)

        pygame.display.flip()
        continue

    if player.alive and not player.won:
        player.move(platforms)

        for coin in coins:
            if not coin.collected and player.rect.colliderect(coin.rect):
                coin.collected = True
                player.score += 1
                coin_sound.play()

        for enemy in enemies:
            enemy.update()

            if player.rect.colliderect(enemy.rect):
                player.alive = False

                if not player.gameover_sound_played:
                    gameover_sound.play()
                    player.gameover_sound_played = True

        if nivel_curent == nivel_bonus:
            if all(coin.collected for coin in coins):
                bonus_final_time = (pygame.time.get_ticks() - bonus_start_time) / 1000
                player.won = True

                if best_bonus_time is None or bonus_final_time < best_bonus_time:
                    best_bonus_time = bonus_final_time
                    save_progress()

                if not player.win_sound_played:
                    win_sound.play()
                    player.win_sound_played = True

        else:
            if player.rect.colliderect(goal):
                level_scores[nivel_curent][0] = player.score

                if player.score > level_scores[nivel_curent][1]:
                    level_scores[nivel_curent][1] = player.score

                if nivel_curent not in unlocked_levels:
                    unlocked_levels.append(nivel_curent)

                if nivel_curent + 1 <= nivel_maxim and nivel_curent + 1 not in unlocked_levels:
                    unlocked_levels.append(nivel_curent + 1)

                save_progress()

                if nivel_curent < nivel_maxim:
                    nivel_curent += 1
                    platforms, coins, enemies, goal, start_pos, player = start_level(nivel_curent)
                else:
                    player.won = True

                    if not player.win_sound_played:
                        win_sound.play()
                        player.win_sound_played = True

    screen.fill(SKY)

    for platform in platforms:
        platform.draw()

    for coin in coins:
        coin.draw()

    for enemy in enemies:
        enemy.draw()

    if goal is not None:
        pygame.draw.rect(screen, GREEN, goal)
        pygame.draw.rect(screen, BLACK, goal, 2)

    player.draw()

    if nivel_curent == nivel_bonus:
        level_text = font.render("Nivel BONUS", True, PURPLE)
    else:
        level_text = font.render(f"Nivel: {nivel_curent}/{nivel_maxim}", True, BLACK)

    screen.blit(level_text, (20, 20))

    score_text = font.render(f"Puncte nivel: {player.score}", True, BLACK)
    screen.blit(score_text, (20, 55))

    if nivel_curent == nivel_bonus and not player.won:
        timp_curent = (pygame.time.get_ticks() - bonus_start_time) / 1000
        timer_text = font.render(f"Timp: {timp_curent:.2f} secunde", True, BLACK)
        screen.blit(timer_text, (20, 90))
    else:
        info_text = font.render("A/D sau sageti = miscare | SPACE/W/UP = saritura | ESC = meniu", True, BLACK)
        screen.blit(info_text, (20, 90))

    if not player.alive:
        draw_text_center("GAME OVER", big_font, RED, HEIGHT // 2 - 20)
        draw_text_center("Apasa R pentru restart", font, BLACK, HEIGHT // 2 + 40)

    if player.won:
        if nivel_curent == nivel_bonus:
            draw_text_center("BONUS TERMINAT!", big_font, PURPLE, HEIGHT // 2 - 60)
            draw_text_center(f"Timp final: {bonus_final_time:.2f} secunde", font, BLACK, HEIGHT // 2)

            if best_bonus_time is not None:
                draw_text_center(f"Record bonus: {best_bonus_time:.2f} secunde", font, PURPLE, HEIGHT // 2 + 40)

            draw_text_center("Apasa R pentru restart sau ESC pentru meniu", font, BLACK, HEIGHT // 2 + 85)
        else:
            draw_text_center("AI CASTIGAT TOT JOCUL!", big_font, GREEN, HEIGHT // 2 - 20)
            draw_text_center("Apasa R pentru restart", font, BLACK, HEIGHT // 2 + 40)

    pygame.display.flip()

pygame.quit()
sys.exit()