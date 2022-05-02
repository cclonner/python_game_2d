import pygame
import os
import csv
import button
import math
import random

pygame.init()

clock = pygame.time.Clock

SCREEN_WIDTH = 1650
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.5625)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set FPS
clock = pygame.time.Clock()
FPS = 100

# Основные переменные
GRAVITY = 0.75
# GRAVITY = 0
SCROLL_THRESH = 500
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = [0,0]

bg_scroll = 0
level = 0
start_game = False

# Действия игрока
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shoot = False
grenade = False
grenade_thrown = False

# Загрузка изображений
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# Задний фон
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
# Собираем все "клетки" в список
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# Пуля
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# Гранаты
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# коробки HP|AMMO|GRENADES
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Цвета
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Шрифт
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        # кулдаун
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right, moving_down, moving_up):
        # сброс
        screen_scroll = [0,0]

        dx = 0
        dy = 0

        # Движение по осям
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if moving_down:
            dy = self.vel_y
            self.vel_y = +10

        if moving_up:
            dy = self.vel_y
            self.vel_y = -10

        # Обновление положения прямоугольника
        self.rect.x += dx
        self.rect.y += dy

        # скролим экрна по позиции игрока

        if self.char_type == "player":
            if self.rect.right > SCREEN_WIDTH > - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                self.rect.x -= dx
                screen_scroll[0] = -dx
                print(screen_scroll)
            if self.rect.top < SCREEN_WIDTH or self.rect.bottom < SCREEN_HEIGHT:
                self.rect.y -= dy
                screen_scroll[1] = -dy
                print(screen_scroll)

        return screen_scroll

    def shoot(self, size):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), \
                            self.rect.centery, size, self.direction)
            bullet_group.add(bullet)
            # Уменьшение патронов в магазине
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            dx, dy = self.rect.x - player.rect.x, self.rect.y - player.rect.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            else:
                dx, dy = dx / dist, (dy / dist) * -1

            self.rect.x -= (dx * self.speed) * 2
            self.rect.y += (dy * self.speed) * 2
            self.rect.x = 10
            self.rect.y = 10

    def update_animation(self):
        # Обновление анимации
        ANIMATION_COOLDOWN = 80
        # Обновление image в зависимости от текущего кадра(frame)
        self.image = self.animation_list[self.action][self.frame_index]
        # Проверка, достаточно ли времени прошло с момента последнего обновления
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # Если анимация заканчивается, то начинается заново
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Проверка если новое действие отличается от предидущего
        if new_action != self.action:
            self.action = new_action
            # Обновление настроек анимации
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            # delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, direction_s):
        self.direction_Solder = direction_s
        pygame.sprite.Sprite.__init__(self)
        mx, my = pygame.mouse.get_pos()
        self.direction = (mx - x, my - y)
        # находим гипотинузу, что пы понять направление пули
        length = math.hypot(*self.direction)
        if length == 0.0:
            self.direction = (0, 0)
        else:
            self.direction = (self.direction[0] / length, self.direction[1] / length)
        angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        self.scale = scale
        self.damage = 25
        self.speed = 20
        self.image = bullet_img
        self.image = pygame.transform.rotate(bullet_img, angle)
        self.image = pygame.transform.scale(bullet_img, \
                                            (int(bullet_img.get_width() * self.scale), \
                                             int(bullet_img.get_height() * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Движение пули
        # self.rect.x += (self.direction * self.speed)
        self.rect.center = (self.rect.center[0] + self.direction[0] * self.speed,
                            self.rect.center[1] + self.direction[1] * self.speed)
        # print(self.direction_Solder)
        # Проверка, не ушла ли пуля за границы экрана
        """if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()"""

        """if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()"""

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()
                    # print(enemy_group)


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        # check collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        # update grenade position
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        # update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll[0]
        self.rect.y -= screen_scroll[1]


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll[0]
        self.rect.y -= screen_scroll[1]


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


# Создаем кнопки меню
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# Создаем спрайты групп
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
hitbox_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
# temp - create item boxes
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 260)
item_box_group.add(item_box)

water = Water(pygame.image.load('img/tile/9.png').convert_alpha(), 100 * TILE_SIZE, 500 * TILE_SIZE)
water_group.add(water)

decoration = Decoration(pygame.image.load('img/tile/9.png').convert_alpha(), 20 * TILE_SIZE, 78 * TILE_SIZE)
decoration_group.add(decoration)

player = Soldier('player', 200, 200, 1.65, 4, 20, 5)
health_bar = HealthBar(10, 10, player.health, player.health)

a = random.randrange(0, SCREEN_WIDTH)
b = random.randrange(-150, -100)
enemy = Soldier('enemy', a, b, 1.65, 1, 20, 0)
enemy_group.add(enemy)
enemies = []
#

run = True
while run:
    clock.tick(FPS)
    if start_game == False:
        # Рисуем меню
        screen.fill(BG)
        # Добавляем кнопки
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:
        # Обновляем задний фон
        draw_bg()
        # Рисуем здоровье игрока
        health_bar.draw(player.health)
        # Рисуем запас патронов игрока
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        # Рисуем запас гранат игрока
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))
        # enemies.append(enemy)
        enemy_group.add(enemy)
        if enemy.alive == False:
            enemy_group.add(enemy)

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #
        bullet_group.update()
        bullet_group.draw(screen)

        explosion_group.update()
        explosion_group.draw(screen)

        grenade_group.update()
        grenade_group.draw(screen)

        item_box_group.update()
        item_box_group.draw(screen)

        decoration_group.update()
        decoration_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)

        # Обновление действий игрока
        if player.alive:
            # Проверка на стрельбу игрока
            if shoot:
                player.shoot(1)
                print("кол-во патронов игрока:", player.ammo, "кол-во гранат игока: ", player.grenades)
            # Проверка на бросок гранаты игрока
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                  player.rect.top, player.direction)
                grenade_group.add(grenade)
                # Уменьшение запаса гранат игрока
                player.grenades -= 1
                print("кол-во патронов игрока:", player.ammo, "кол-во гранат игока: ", player.grenades)
                grenade_thrown = True
            # print(player.grenades)
            """if player.in_air:
                player.update_action(2)"""  # 2: Прыжок
            if moving_left or moving_right or moving_down or moving_up:
                player.update_action(1)  # 1: Бег
            else:
                player.update_action(0)  # 0: Бездействие
            screen_scroll = player.move(moving_left, moving_right, moving_down, moving_up)

    for event in pygame.event.get():
        # Выход из игры
        if event.type == pygame.QUIT:
            run = False
        # Нажатие клавиш игрока

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_e and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # Отжатие клавиш игрока
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_e:
                player.jump = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
