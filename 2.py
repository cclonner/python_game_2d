import time
import pygame
import os
import csv
import button
import math
import random

pygame.init()

clock = pygame.time.Clock

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set FPS
clock = pygame.time.Clock()
FPS = 100

# Основные переменные
GRAVITY = 0.75
SCROLL_THRESH = 500
ROWS = 50
COLS = 50
TILE_SIZE = ROWS
TILE_TYPES = 21
screen_scroll = [0, 0]

bg_scroll = [0, 0]
level = 2
start_game = False
start_intro = False
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
PINK = (235, 65, 54)
DARK_GREEN = (85, 107, 47)
BLUE = (0, 0, 255)

# Шрифт
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Функция рестарта
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # Создаем пустой список мира
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    print(data)

    return data

def waves():
    num_wave = 1
    enemies_x = [random.randint(0, 111) for _ in range(10 * num_wave)]
    enemies_y = [random.randint(0, 111) for _ in range(10 * num_wave)]
    #enemies.append(x )
    print(enemies_x)
    for x in enemies_x:
        for y in enemies_y:
            enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 1, 1, 4)
            enemy_group.add(enemy)
            print(enemies_x)
            print(enemy_group)
            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()
    return enemy_group

def draw_bg():
    screen.fill(DARK_GREEN)


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.alive = True
        self.char_type = char_type
        self.scale = scale
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # -----------------------
        self.scale = scale
        # Загрузка анимаций для игроков
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Временный список изображений
            temp_list = []
            # Считаем кол-во изображений в папке
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # Обновление кулдауна
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right, moving_down, moving_up):
        # Сбрасываем переменные движения
        screen_scroll = [0, 0]
        dx = 0
        dy = 0

        """mx, my = pygame.mouse.get_pos()
        if mx > dx:
            self.flip = True
            self.direction = -1
        if my > dy:
            self.flip = False
            self.direction = 1"""
        # Движение влево или вправо
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
            self.vel_y = +5

        if moving_up:
            dy = self.vel_y
            self.vel_y = -5

        # Проверка на препятсвия
        for tile in world.obstacle_list:
            # Проверка на препятсвие по X
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # Проверка на препятсвие по Y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Проверка на поверхность над игроком(потолок), в прыжке
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Проверка на поверхность под игроком(пол), в падении
                # dy = tile[1].top - self.rect.bottom
                dy = 0
        # Проверка на соприкосновение с водой
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        """# Проверка, не упал ли игрок с карты
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0"""

        # Проверка, не выходит ли игрок за границы карты
        """if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0"""
        """if self.char_type == 'enemy':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0"""

        # Обновление положения прямоугольника
        self.rect.x += dx
        self.rect.y += dy
        # скролинг экрана от позиции игрока КАМЕРА
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll[0] < (
                    world.level_length[0] * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll[0] > abs(dx)):
                self.rect.x -= dx
                screen_scroll[0] = -dx

            if (self.rect.top < SCROLL_THRESH and bg_scroll[1] < (
                    world.level_length[1] * TILE_SIZE) - SCREEN_HEIGHT) \
                    or (self.rect.bottom < SCREEN_HEIGHT - SCROLL_THRESH and bg_scroll[1] > abs(dx)):
                self.rect.y -= dy
                screen_scroll[1] = -dy
        return screen_scroll

    def shoot(self, size, char_type):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), \
                            self.rect.centery, size, char_type)
            bullet_group.add(bullet)
            # Уменьшение патронов в магазине
            self.ammo -= 1

    # функция ьотов
    def ai(self):
        if self.alive and player.alive:
            dx, dy = self.rect.x - player.rect.x, self.rect.y - player.rect.y
            dist = math.hypot(dx, dy)
            if dist < 170:
                self.update_action(0)  # 0: idle
                self.shoot(2, "enemy")
            if dist == 0:
                dist = 1
            else:
                dx, dy = dx / dist, (dy / dist) * -1
            self.update_action(1)
            self.rect.x -= (dx * self.speed) * 2
            self.rect.y += (dy * self.speed) * 2
            if pygame.sprite.collide_rect(self, player):
                player.health -= 0.1
            if pygame.sprite.spritecollide(self, water_group, False):
                self.health = 0

        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

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
                start_ticks = pygame.time.get_ticks()
                self.frame_index = len(self.animation_list[self.action]) - 1
                if start_ticks >= 5000:
                    self.kill()
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Проверка если новое действие отличается от предыдущего
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
            print(self.health)



    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # узнаем длину data что бы ограничить прокрутку экрана до докнца карты\ значени data
        self.level_length = [0, 0]
        self.level_length[0] = len(data[0])
        self.level_length[1] = len(data[1])

        # проходимся по каждому значению в level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # Создаем игрока
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 200, 10)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # Создаем enemy
                        # char_type, x, y, scale, speed, ammo, grenades
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 1, 1, 4)
                        enemy_group.add(enemy)
                    elif tile == 17:  # Создаем ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # Создаем grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # Создаем health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # Создаем exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][1] += screen_scroll[1]
            tile[1][0] += screen_scroll[0]
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
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
        self.rect.y += screen_scroll[1]


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.healing = 25
        self.ammo = 15
        self.grenade = 5
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Проверка, поднял ли игрок коробку
        if pygame.sprite.collide_rect(self, player):
            # Проверка, какую коробку
            if self.item_type == 'Health':
                player.health += 25
                # print("здоровье игрока +", self.healing, "==", player.health)
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
                # print("патроны игрока +", self.ammo, "==", player.ammo)
            elif self.item_type == 'Grenade':
                player.grenades += 5
                # print("гранты игрока +", self.ammo, "==", player.grenades)
            # Удаление коробки
            self.kill()
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Обновление, здоровье на макс
        self.health = health
        # Рассчитать соотношение здоровья
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, char):
        pygame.sprite.Sprite.__init__(self)
        if char == "player":
            mx, my = pygame.mouse.get_pos()
        else:
            mx, my = enemy.rect.center
        self.direction = (mx - x, my - y)
        # находим гипотинузу, что пы понять направление пули
        length = math.hypot(*self.direction)
        if length == 0.0:
            self.direction = (0, 0)
        else:
            self.direction = (self.direction[0] / length, self.direction[1] / length)
        angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        self.scale = scale
        self.damage = 5
        self.speed = 20
        self.image = bullet_img
        self.image = pygame.transform.rotate(bullet_img, angle)
        self.image = pygame.transform.scale(bullet_img, \
                                            (int(bullet_img.get_width() * self.scale), \
                                             int(bullet_img.get_height() * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # -----------------------------------------

    def update(self):
        # Движение пули
        self.rect.center = ((self.rect.center[0] + self.direction[0] * self.speed) + screen_scroll[0],
                            (self.rect.center[1] + self.direction[1] * self.speed) + screen_scroll[1])
        # Проверка, не ушла ли пуля за границы экрана
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Проверка на препятсвие
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Проверка на попадание по игроку
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                # print("здоровье игрока:", player.health - self.damage)
                player.health -= 0
                # self.kill()
        # Проверка на попадание по enemy
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    # print("здоровье игрока:", player.health, "здоровье второго игрока:", enemy.health - self.damage)
                    enemy.health -= self.damage
                    # enemy.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, direction_s):
        self.direction_Solder = direction_s
        pygame.sprite.Sprite.__init__(self)
        mx, my = pygame.mouse.get_pos()
        self.direction = (mx - x, my - y)
        # находим гипотинузу, что пы понять направление гранатф
        length = math.hypot(*self.direction)
        if length == 0.0:
            self.direction = (0, 0)
        else:
            self.direction = (self.direction[0] / length, self.direction[1] / length)
        angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        self.timer = 100
        self.scale = scale
        self.speed = 1
        self.damage = 10
        self.image = pygame.transform.rotate(grenade_img, angle)
        self.image = pygame.transform.scale(grenade_img, \
                                            (int(grenade_img.get_width() * self.scale), \
                                             int(grenade_img.get_height() * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.center = ((self.rect.center[0] + self.direction[0] * self.speed) + screen_scroll[0],
                            (self.rect.center[1] + self.direction[1] * self.speed) + screen_scroll[1])
        # Проверка, не ушла ли пуля за границы экрана
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Проверка на препятсвие
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 2)
                explosion_group.add(explosion)

        # Таймер гранаты
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)
            # Урон по определенной области
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * (player.scale + 2) and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * (player.scale + 2):
                player.health -= 25 + self.damage + abs(self.rect.centerx - player.rect.centerx)
            for enemy in enemy_group:
                if pygame.sprite.spritecollide(enemy, explosion_group, False):
                    if enemy.alive:
                        if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * (enemy.scale) and \
                                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * (enemy.scale):
                            enemy.health -= 25 + self.damage + abs(self.rect.centerx - enemy.rect.centerx)


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
        self.rect.center = (x, y - (0.36 * self.rect.size[0]))
        self.counter = 0

    def update(self):
        # скроллинг
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
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


# заствка
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # экран исчезает
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # тож самое но по оси у
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# Создаем кнопки меню
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)
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
# Создаем пустой tile список
world_data = []
# всю карту деламем из -1
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# Загружаем уровень и создаем мир
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
print(world_data)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)
    if start_game == False:
        # Рисуем меню
        screen.fill(BG)
        # Добавляем кнопки
        if start_button.draw(screen):
            start_game = True
            #start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # Обновляем задний фон
        draw_bg()
        # Рисуем мир
        world.draw()
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

        decoration_group.update()
        decoration_group.draw(screen)

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
            if len(enemy_group) == 0:
                print("1 волна")
                waves()
                print(enemy_group)




        #print(enemy_group)
        player.update()
        player.draw()
        # Обновляем и рисуем группы(group)

        explosion_group.update()
        explosion_group.draw(screen)

        grenade_group.update()
        grenade_group.draw(screen)

        item_box_group.update()
        item_box_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        bullet_group.update()
        bullet_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)

        # заставка
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Обновление действий игрока
        if player.alive:
            # Проверка на стрельбу игрока
            if shoot:
                player.shoot(1, "player")
                print("кол-во патронов игрока:", player.ammo, "кол-во гранат игока: ", player.grenades)
            # Проверка на бросок гранаты игрока
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                  player.rect.top, 2, player.direction)
                grenade_group.add(grenade)
                # Уменьшение запаса гранат игрока
                player.grenades -= 1
                print("кол-во патронов игрока:", player.ammo, "кол-во гранат игока: ", player.grenades)
                grenade_thrown = True

            if moving_left or moving_right or moving_down or moving_up:
                player.update_action(1)  # 1: Бег
            else:
                player.update_action(0)  # 0: Бездействие
            screen_scroll = player.move(moving_left, moving_right, moving_down, moving_up)
            bg_scroll[0] -= screen_scroll[0]
            bg_scroll[1] -= screen_scroll[1]

        else:
            screen_scroll = [0, 0]
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = [0, 0]
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

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
