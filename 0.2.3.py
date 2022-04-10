import pygame
import math

pygame.init()
window = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

class Bullet:
    def __init__(self, x, y):
        self.pos = (x, y)
        mx, my = pygame.mouse.get_pos()
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0]/length, self.dir[1]/length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        self.bullet = pygame.Surface((7, 2)).convert_alpha()
        self.bullet.fill((255, 255, 255))
        self.bullet = pygame.transform.rotate(self.bullet, angle)
        self.speed = 2

    def update(self):
        self.pos = (self.pos[0]+self.dir[0]*self.speed,
                    self.pos[1]+self.dir[1]*self.speed)

    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center = self.pos)
        surf.blit(self.bullet, bullet_rect)



bullets = []
pos = (250, 250)
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            bullets.append(Bullet(*pos))

    for bullet in bullets[:]:
        bullet.update()
        if not window.get_rect().collidepoint(bullet.pos):
            bullets.remove(bullet)

    window.fill(0)
    pygame.draw.circle(window, (0, 255, 0), pos, 10)
    for bullet in bullets:
        bullet.draw(window)
    pygame.display.flip()

"""
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, scale):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        self.damage = 25
        self.speed = 20
        self.pos = pygame.mouse.get_pos()
        self.image = pygame.transform.scale(bullet_img, (
        int(bullet_img.get_width() * self.scale), int(bullet_img.get_height() * self.scale)))
        self.rect = self.image.get_rect()
        #self.rect.center = self.pos

    def update(self):
        # Движение пули
        self.rect.x = self.pos[0] - self.rect.x
        self.rect.y = self.pos[1] - self.rect.x
        angle = math.atan2(self.rect.x, self.rect.y)
        print(angle)
        self.rect.x += self.speed * math.cos(angle)
        self.rect.y += self.speed * math.cos(angle)

        # Проверка, не ушла ли пуля за границы экрана
        if self.rect.right < 0 or self.rect.left > 400:
            self.kill()


player = Player(20, 20)
all_sprites = pygame.sprite.Group(player)


while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                shoot = False
    if shoot:
        player.shoot(1)
    player.point_at(*pygame.mouse.get_pos())
    print((pygame.mouse.get_pos()))
    keys = pygame.key.get_pressed()
    player.move(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])

    wn.fill((255, 255, 255))
    all_sprites.draw(wn)
    pygame.display.update()
"""