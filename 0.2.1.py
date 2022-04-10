import pygame
import math

wn = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
LIGHT_BLUE = (64, 128, 255)
GREEN = (0, 200, 64)
YELLOW = (225, 225, 0)
PINK = (230, 50, 230)
shoot = False
bullets = []
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load('img/Player/Idle/0.png')
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 5
        self.shoot_cooldown = 0

    def point_at(self, x, y):
        direction = pygame.math.Vector2(x, y) - self.rect.center
        angle = direction.angle_to((0, -1))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, x, y):
        self.rect.move_ip(x * self.velocity, y * self.velocity)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery)
        bullets.append(bullet)


class Bullet:
    def __init__(self, x, y):
        self.pos = (x, y)
        mx, my = pygame.mouse.get_pos()
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0] / length, self.dir[1] / length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        self.bullet = pygame.Surface((7, 2)).convert_alpha()
        self.bullet.fill((255, 255, 255))
        self.bullet = pygame.transform.rotate(self.bullet, angle)
        self.speed = 10

    def update(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)

    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center=self.pos)
        surf.blit(self.bullet, bullet_rect)


pos = (250, 250)
player = Player(20, 20)
all_sprites = pygame.sprite.Group(player)
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot()
    for bullet in bullets[:]:
        bullet.update()
        if not wn.get_rect().collidepoint(bullet.pos):
            bullets.remove(bullet)

    player.point_at(*pygame.mouse.get_pos())
    # print((pygame.mouse.get_pos()))

    keys = pygame.key.get_pressed()
    player.move(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])

    wn.fill(GRAY)
    pygame.draw.circle(wn, (0, 255, 0), pos, 10)
    # for bullet in bullets:
    for bullet in bullets:
        bullet.draw(wn)
    all_sprites.draw(wn)
    pygame.display.flip()
