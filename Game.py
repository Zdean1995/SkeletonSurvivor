import pygame
from random import randint, choice
import math
from os.path import join

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

damage_font = pygame.font.Font('assets/font/Pixeltype.ttf', 50)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.x = 0
        self.y = 0

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
        self.y_vel = 0
        self.x_vel = 0
        self.range = 25
        self.lifetime = 0
        match direction:
            case "up":
                self.y_vel = 20
            case "down":
                self.y_vel = -20
            case "right":
                self.x_vel = 20
            case "left":
                self.x_vel = -20

    def update(self):
        global y_vel
        global x_vel
        self.rect.x += self.x_vel - x_vel
        self.rect.y += self.y_vel - y_vel
        self.lifetime += 1
        if self.lifetime > self.range:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global offset_y, offset_x
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLACK)
        self.hurt_frames = 0
        self.rect = self.image.get_rect(center=
                                        ((randint(0, WIDTH) + offset_x)
                                         , (randint(0, HEIGHT) + offset_y)))
        self.health = 3

    def drop_exp(self):
        global exp_drops
        exp_drops.add(ExpDrop(10, self.rect.x, self.rect.y))

    def update(self):
        global bullets, damage_numbers, enemies
        dx, dy = CENTER_WIDTH - self.rect.x, CENTER_HEIGHT - self.rect.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist
        self.rect.x += dx - x_vel
        self.rect.y += dy - y_vel
        if self.hurt_frames > 0:
            self.hurt_frames -= 1
        elif pygame.sprite.spritecollide(self, bullets, False):
            self.hurt_frames = 5
            if self.health == 1:
                self.drop_exp()
                self.drop_exp()
                self.drop_exp()
                self.kill()
            else:
                self.health -= 1
            damage_numbers.add(DamageNumber("1", self.rect.x, self.rect.y))

class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, num, x, y):
        super().__init__()
        self.image = damage_font.render(num, False, RED)
        self.rect = self.image.get_rect(center = (x, y))
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
    global exp, level_up_exp, exp_bar_progress
    exp += amount
    if exp >= level_up_exp:
        exp -= level_up_exp
        level_up_exp *= 1.5
        exp_bar_progress = pygame.Surface((0, 20))
        exp_check(0)
    else:
        exp_bar_progress = pygame.Surface(((exp/level_up_exp)*(WIDTH * 0.9), 20))
        exp_bar_progress.fill(WHITE)




player = pygame.sprite.GroupSingle()
player.add(Player())

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
damage_numbers = pygame.sprite.Group()
exp_drops = pygame.sprite.Group()

#exp values
exp = 0
level_up_exp = 1000

exp_bar = pygame.Surface((WIDTH * 0.9, 20))

exp_bar_progress = pygame.Surface((0, 20))
exp_bar_progress.fill(WHITE)



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
    player.update()
    bullets.draw(screen)
    bullets.update()
    enemies.draw(screen)
    enemies.update()
    damage_numbers.draw(screen)
    damage_numbers.update()
    exp_drops.draw(screen)
    exp_drops.update()

    screen.blit(exp_bar, (WIDTH*0.05, HEIGHT*0.9))
    screen.blit(exp_bar_progress, (WIDTH*0.05, HEIGHT*0.9))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == bullet_timer:
            bullets.add(Bullet("up"), Bullet("down"), Bullet("left"), Bullet("right"))
        if event.type == enemy_timer:
            enemies.add(Enemy())

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
