import pygame
from os.path import join

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto Shooter")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

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
        match direction:
            case "up":
                self.y_vel = 10
            case "down":
                self.y_vel = -10
            case "right":
                self.x_vel = 10
            case "left":
                self.x_vel = -10

    def update(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 65):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


player = pygame.sprite.GroupSingle()
player.add(Player())

bullets = pygame.sprite.Group()

# Game loop
clock = pygame.time.Clock()
running = True

#Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 500)


while running:
    background, bg_image = get_background("Blue.png")
    for tile in background:
        screen.blit(bg_image, (tile[0] - ((player.sprite.x / 10) % bg_image.get_width()), tile[1] - ((player.sprite.y / 10) % bg_image.get_height())))
    player.draw(screen)
    player.update()
    bullets.draw(screen)
    bullets.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == obstacle_timer:
            bullets.add(Bullet("up"), Bullet("down"), Bullet("left"), Bullet("right"))



    pygame.display.flip()
    clock.tick(60)

pygame.quit()