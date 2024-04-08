import pygame
import random
import math
from os.path import join

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
        self.player_input()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.y_vel = 0
        self.x_vel = 0
        self.range = 10
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
        self.rect = self.image.get_rect(center=
                                        ((random.randint(0, WIDTH) + offset_x)
                                         , (random.randint(0, HEIGHT) + offset_y)))

    def update(self):
        global bullets
        dx, dy = CENTER_WIDTH - self.rect.x, CENTER_HEIGHT - self.rect.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist
        self.rect.x += dx - x_vel
        self.rect.y += dy - y_vel
        if pygame.sprite.spritecollide(self, bullets, False):
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


player = pygame.sprite.GroupSingle()
player.add(Player())

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Game loop
clock = pygame.time.Clock()
running = True

# Timer
bullet_timer = pygame.USEREVENT + 1
pygame.time.set_timer(bullet_timer, 250)

enemy_timer = pygame.USEREVENT + 2
pygame.time.set_timer(enemy_timer, 1000)

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
