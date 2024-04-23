import random

import pygame
import json
from random import randint, choice
import math
from os.path import join
from enum import Enum, auto

from pygame import Vector2

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
CENTER_WIDTH, CENTER_HEIGHT = WIDTH // 2, HEIGHT // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto Shooter")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

damage_font = pygame.font.Font('assets/font/Pixeltype.ttf', 50)


class Stats(Enum):
    HEALTH = auto()
    DAMAGE = auto()
    SPEED = auto()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.x = 0
        self.y = 0
        self.speed = 1
        self.damage = 1
        self.max_health = 100
        self.health = self.max_health
        self.exp = 0
        self.exp_to_level = 10

    def hurt(self, amount):
        global life_bar, damage_numbers
        self.health -= amount
        if (self.health <= 0):
            reset()
        else:
            life_bar = pygame.Surface(((self.health / self.max_health) * 80, 5))
            life_bar.fill(GREEN)
            damage_numbers.add(DamageNumber(str(amount), CENTER_WIDTH, CENTER_HEIGHT, GREEN))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.x -= 10
        if keys[pygame.K_d]:
            self.x += 10
        if keys[pygame.K_w]:
            self.y -= 10
        if keys[pygame.K_s]:
            self.y += 10

    def update(self):
        global exp_drops
        self.player_input()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.damage = 1
        self.y_vel = 0
        self.x_vel = 0
        self.range = 25
        self.lifetime = 0
        self.enemies_hit = []
        self.pierce = -1
        match direction:
            case "up":
                self.y_vel = 20
            case "down":
                self.y_vel = -20
            case "right":
                self.x_vel = 20
            case "left":
                self.x_vel = -20
            case "enemy":
                if enemies:
                    enemy = random.choice(enemies.sprites())
                    dx, dy = CENTER_WIDTH - enemy.rect.center[0], CENTER_HEIGHT - enemy.rect.center[1]
                    dist = math.hypot(dx, dy)
                    dx, dy = dx / dist, dy / dist
                    self.x_vel = dx * -20
                    self.y_vel = dy * -20
                else:
                    self.x_vel = 20


    def update(self):
        global y_vel, x_vel, enemies, player
        self.rect.x += self.x_vel - x_vel
        self.rect.y += self.y_vel - y_vel
        self.lifetime += 1
        if self.lifetime > self.range:
            self.kill()
        enemies_hit = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemies_hit:
            if not (enemy in self.enemies_hit):
                enemy.hurt(self.damage * player.sprite.damage)
                self.enemies_hit.append(enemy)
                if len(self.enemies_hit) >= self.pierce and self.pierce >= 0:
                    self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        global offset_y, offset_x
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLACK)
        self.hurt_frames = 0
        self.damage = 1
        self.rect = self.image.get_rect(center=(x + offset_x, y + offset_y))
        self.health = 3

    def drop_exp(self):
        global exp_drops
        exp_drops.add(ExpDrop(1, self.rect.x, self.rect.y))

    def hurt(self, amount):
        self.health -= amount
        damage_numbers.add(DamageNumber(str(amount), self.rect.x, self.rect.y, RED))
        if self.health <= 0:
            self.drop_exp()
            self.drop_exp()
            self.drop_exp()
            self.kill()

    def update(self):
        global bullets, damage_numbers, enemies, player, damage_numbers
        dx, dy = CENTER_WIDTH - self.rect.center[0], CENTER_HEIGHT - self.rect.center[1]
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist
        self.rect.x += dx - x_vel
        self.rect.y += dy - y_vel
        if pygame.sprite.spritecollide(self, player, False):
            if abs(self.rect.center[0] - CENTER_WIDTH) > abs(self.rect.center[1] - CENTER_HEIGHT):
                if self.rect.right <= CENTER_WIDTH:
                    self.rect.right = player.sprite.rect.left
                else:
                    self.rect.left = player.sprite.rect.right
            else:
                if self.rect.bottom <= CENTER_HEIGHT:
                    self.rect.bottom = player.sprite.rect.top
                else:
                    self.rect.top = player.sprite.rect.bottom
            if self.hurt_frames == 0:
                player.sprite.hurt(self.damage)
                self.hurt_frames = 50
        if self.hurt_frames > 0:
            self.hurt_frames -= 1


class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, num, x, y, color):
        super().__init__()
        self.image = damage_font.render(num, False, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 0

    def update(self):
        self.rect.y -= y_vel + 3
        if self.lifetime >= 40:
            self.kill()
        elif 10 >= self.lifetime > 5 or 20 >= self.lifetime > 15 or 30 >= self.lifetime > 25 or self.lifetime > 35:
            self.rect.x -= x_vel + 3
        else:
            self.rect.x -= x_vel - 3
        self.lifetime += 1
        self.image.set_alpha(180 - (self.lifetime * 6))


class ExpDrop(pygame.sprite.Sprite):
    def __init__(self, num, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.exp_amount = num
        self.rect = self.image.get_rect(center=(x, y))
        self.move_time = 10
        self.x_vel = randint(0, 10)
        self.y_vel = randint(0, 10)

    def update(self):
        global player
        if Vector2(player.sprite.rect.center).distance_to(self.rect.center) < 100:
            dx, dy = CENTER_WIDTH - self.rect.x, CENTER_HEIGHT - self.rect.y
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * 10 - x_vel
            self.rect.y += dy * 10 - y_vel
        elif self.move_time > 0:
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel
            self.move_time -= 1
        self.rect.x -= x_vel
        self.rect.y -= y_vel
        if pygame.sprite.spritecollide(self, player, False):
            exp_check(self.exp_amount)
            self.kill()


class UpgradeOption(pygame.sprite.Sprite):
    def __init__(self, slot, upgrade):
        super().__init__()
        global upgrade_window_rect
        self.upgrade = upgrade
        self.image = pygame.Surface((upgrade_window_rect.width//1.2, upgrade_window_rect.height//5))
        self.image.fill(RED)
        match slot:
            case 1:
                self.rect = self.image.get_rect(center=(CENTER_WIDTH, upgrade_window_rect.top + upgrade_window_rect.height//4))
            case 2:
                self.rect = self.image.get_rect(center=(CENTER_WIDTH, CENTER_HEIGHT))
            case 3:
                self.rect = self.image.get_rect(center=(CENTER_WIDTH, upgrade_window_rect.bottom - upgrade_window_rect.height//4))

    def apply(self):
        global player
        player.sprite.max_health += self.upgrade.health
        player.sprite.health += self.upgrade.health
        player.sprite.damage += self.upgrade.damage
        player.sprite.speed += self.upgrade.speed



class Upgrade:
    def __init__(self, stats):
        self.text = stats["Text"]
        self.damage = 0
        self.speed = 0
        self.health = 0
        if "Damage" in stats:
            self.damage = stats["Damage"]
        if "Health" in stats:
            self.health = stats["Health"]
        if "Speed" in stats:
            self.speed = stats["Speed"]



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 2):
        for j in range(HEIGHT // height + 65):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def exp_check(amount):
    global player, exp_bar_progress, go, upgrade_texts
    player.sprite.exp += amount
    if player.sprite.exp >= player.sprite.exp_to_level:
        player.sprite.exp -= player.sprite.exp_to_level
        player.sprite.exp_to_level *= 1.5
        exp_bar_progress = pygame.Surface((0, 20))
        damage_numbers.add(DamageNumber("Level up!", CENTER_WIDTH, CENTER_HEIGHT, GREEN))
        exp_check(0)
        upgrade1 = choice(upgrade_options)
        upgrade_texts.append(damage_font.render(upgrade1.text, True, GREEN))
        upgrades.add(UpgradeOption(1, upgrade1))
        upgrade2 = choice(upgrade_options)
        upgrade_texts.append(damage_font.render(upgrade2.text, True, GREEN))
        upgrades.add(UpgradeOption(2, upgrade2))
        upgrade3 = choice(upgrade_options)
        upgrade_texts.append(damage_font.render(upgrade3.text, True, GREEN))
        upgrades.add(UpgradeOption(3, upgrade3))
        go = False
    else:
        exp_bar_progress = pygame.Surface(((player.sprite.exp / player.sprite.exp_to_level) * (WIDTH * 0.9), 20))
        exp_bar_progress.fill(WHITE)



def reset():
    global offset_y, offset_x, life_bar, exp_bar_progress, \
        bullets, enemies, damage_numbers, player
    player.sprite.max_health = 100
    player.sprite.health = player.sprite.max_health
    enemies.empty()
    bullets.empty()
    damage_numbers.empty()
    exp_drops.empty()
    offset_x = 0
    offset_y = 0
    player.sprite.exp_to_level = 10
    player.sprite.damage = 1
    player.sprite.exp = 0
    life_bar = pygame.Surface((80, 5))
    life_bar.fill(GREEN)
    exp_bar_progress = pygame.Surface((0, 20))
    exp_bar_progress.fill(WHITE)


# Sprite Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
damage_numbers = pygame.sprite.Group()
exp_drops = pygame.sprite.Group()
upgrades = pygame.sprite.Group()

# # player stats
# exp = 0
# level_up_exp = 1
#
# max_health = 100
# health = max_health
#
# damage = 1

go = True

exp_bar = pygame.Surface((WIDTH * 0.9, 20))

exp_bar_progress = pygame.Surface((0, 20))
exp_bar_progress.fill(WHITE)

# upgrade_window = pygame.image.load('assets/menu/upgrade.png')
upgrade_window = pygame.Surface((WIDTH // 1.2, HEIGHT // 1.2))
upgrade_window.fill(WHITE)
upgrade_window_rect = upgrade_window.get_rect(center=(CENTER_WIDTH, CENTER_HEIGHT))
upgrade_options = []
upgrade_texts = []

with open("assets/upgrades.JSON", "r") as f:
    data = json.load(f)

for d in data:
    upgrade_options.append(Upgrade(d))

life_total_bar = pygame.Surface((80, 5))
life_total_bar.fill(RED)

life_bar = pygame.Surface((80, 5))
life_bar.fill(GREEN)

center_dot = pygame.Surface((1, 1))
center_dot.fill(WHITE)

# Game loop
clock = pygame.time.Clock()
running = True

# Timer
bullet_timer = pygame.USEREVENT + 1
pygame.time.set_timer(bullet_timer, 250)

enemy_timer = pygame.USEREVENT + 2
pygame.time.set_timer(enemy_timer, 500)

y_vel = 0
x_vel = 0

offset_x = 0
offset_y = 0

while running:
    background, bg_image = get_background("Blue.png")
    for tile in background:
        screen.blit(bg_image, (
            tile[0] - (offset_x % bg_image.get_width()), tile[1] - (offset_y % bg_image.get_height())))

    player.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    damage_numbers.draw(screen)
    exp_drops.draw(screen)
    screen.blit(exp_bar, (WIDTH * 0.05, HEIGHT * 0.9))
    screen.blit(exp_bar_progress, (WIDTH * 0.05, HEIGHT * 0.9))
    screen.blit(center_dot, (CENTER_WIDTH, CENTER_HEIGHT))

    screen.blit(life_total_bar, (CENTER_WIDTH - 40, CENTER_HEIGHT - 40))
    screen.blit(life_bar, (CENTER_WIDTH - 40, CENTER_HEIGHT - 40))

    if go:
        player.update()
        bullets.update()
        enemies.update()
        damage_numbers.update()
        exp_drops.update()

        y_vel = 0
        x_vel = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            x_vel -= 10
        if keys[pygame.K_d]:
            x_vel += 10
        if keys[pygame.K_w]:
            y_vel -= 10
        if keys[pygame.K_s]:
            y_vel += 10

        offset_y += y_vel
        offset_x += x_vel

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == bullet_timer:
                bullets.add(Bullet("enemy"), Bullet("enemy"), Bullet("enemy"), Bullet("enemy"))
            if event.type == enemy_timer:
                enemies.add(choice([Enemy(-30, randint(0, HEIGHT)), Enemy(WIDTH + 30, randint(0, HEIGHT)),
                                   Enemy(randint(0, WIDTH), -30), Enemy(randint(0, WIDTH), HEIGHT + 30)]))
    else:
        screen.blit(upgrade_window, upgrade_window_rect)
        upgrades.draw(screen)
        screen.blit(upgrade_texts[0], (CENTER_WIDTH, upgrade_window_rect.top + upgrade_window_rect.height//4))
        screen.blit(upgrade_texts[1], (CENTER_WIDTH, CENTER_HEIGHT))
        screen.blit(upgrade_texts[2], (CENTER_WIDTH, upgrade_window_rect.bottom - upgrade_window_rect.height//4))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for upgrade in upgrades:
                    if upgrade.rect.collidepoint(event.pos):
                        upgrade.apply()
                        go = True
                        upgrades.empty()
                        upgrade_texts.clear()


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
