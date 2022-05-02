import pygame
import os
import csv
import button
import math

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
#screen_scroll = [0, 0]

screen_scroll = 0
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


# Функция рестарта
def reset_level():
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    hitbox_group.empty()

    # Создаем пустой список
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    print(data)

    return data


def draw_bg():
    screen.fill(BLACK)
    """width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - 1 * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 350))
        screen.blit(pine1_img, ((x * width) - 1 * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 180))
        screen.blit(pine2_img, ((x * width) - 1 * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))"""


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, jumpRange, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
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
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # -----------------------
        self.scale = scale
        self.jumpRange = jumpRange
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
        #screen_scroll = [0, 0]
        screen_scrolly = 0
        screen_scroll = 0
        dx = 0
        dy = 0

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
            self.vel_y = +10

        if moving_up:
            dy = self.vel_y
            self.vel_y = -10

        # Прыжок
        if self.jump == True and self.in_air == False:
            self.vel_y = -11 - self.jumpRange
            self.jump = False
            # self.in_air = True

        # Гравитация
        # self.vel_y += GRAVITY
        # dy += self.vel_y

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

        # Проверка, не упал ли игрок с карты
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Проверка, не выходит ли игрок за границы карты
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
        if self.char_type == 'enemy':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Обновление положения прямоугольника
        self.rect.x += dx
        self.rect.y += dy

        # скролинг экрана от позиции игрока
        if self.char_type == "player":
            if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                self.rect.x -= dx
                screen_scroll = -dx


        return screen_scroll

    def shoot(self, size):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), \
                            self.rect.centery, size, self.direction)
            bullet_group.add(bullet)
            # Уменьшение патронов в магазине
            self.ammo -= 1

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


# pygame.draw.rect(screen, RED, self.rect, 1)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # узнаем длину data что бы ограничить прокрутку экрана до докнца карты\ значени data
        self.level_length = len(data[0])
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
                    elif tile == 15:  # Создаем первого игрока
                        # char_type, x, y, scale, speed, jumpRange, ammo, grenades
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, (TILE_SIZE // img.get_height() * 1.4),
                                         7, (TILE_SIZE // img.get_height() * 6), 200, 10)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    elif tile == 16:  # Создаем второго игрока
                        # char_type, x, y, scale, speed, jumpRange, ammo, grenades
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE,
                                          (TILE_SIZE // img.get_height() * 1.4), 7, 5, 20, 10)
                        # health_bar1 = HealthBar((SCREEN_WIDTH - 350), 10, enemy.health, player2.health)

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

        return player, health_bar, enemy

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll


            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll



class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll



class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.healing = 25
        self.ammo = 15
        self.granade = 5
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # Проверка, поднял ли игрок коробку
        if pygame.sprite.collide_rect(self, player):
            # Проверка, какую коробку
            if self.item_type == 'Health':
                player.health += 25
                print("здоровье игрока +", self.healing, "==", player.health)
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
                print("патроны игрока +", self.ammo, "==", player.ammo)
            elif self.item_type == 'Grenade':
                player.grenades += 5
                print("гранты игрока +", self.ammo, "==", player.grenades)
            # Удаление коробки
            self.kill()
        # Проверка, поднял ли второй игрок коробку
        if pygame.sprite.collide_rect(self, enemy):
            # Проверка, какую коробку
            if self.item_type == 'Health':
                enemy.health += 25
                print("здоровье второго игрока +", self.healing, "==", enemy.health)
                if enemy.health > enemy.max_health:
                    enemy.health = enemy.max_health
            elif self.item_type == 'Ammo':
                enemy.ammo += 15
                print("патроны второго игрока +", self.ammo, "==", enemy.ammo)
            elif self.item_type == 'Grenade':
                enemy.grenades += 5
                print("гранты второго игрока +", self.ammo, "==", enemy.grenades)
            # Удаление коробки
            self.kill()
        self.rect.x += screen_scroll



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
        # -----------------------------------------

    def update(self):
        # Движение пули
        # self.rect.x += (self.direction * self.speed)
        self.rect.center = (self.rect.center[0] + self.direction[0] * self.speed + screen_scroll,
                            self.rect.center[1] + self.direction[1] * self.speed - screen_scroll)
        # print(self.direction_Solder)
        # Проверка, не ушла ли пуля за границы экрана
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Проверка на препятсвие
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Проверка на попадание по игроку """hitbox_player"""
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                print("здоровье игрока:", player.health - self.damage, "здоровье второго игрока:", enemy.health)
                # player.health -= self.damage
                # self.kill()
        # Проверка на попадание по второму игроку """enemy"""
        """if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                print("здоровье игрока:", player.health, "здоровье второго игрока:", enemy.health - self.damage)
                enemy.health -= self.damage
                self.kill()"""


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 1
        self.damage = 10
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        # self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.direction * self.speed
        # dy = self.vel_y

        # Проверка на препятсвие
        for tile in world.obstacle_list:
            # Проверка на соприкосновение со стеной
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # Проверка на соприкосновение по оси Y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.speed // self.direction > 0:
                    self.speed -= self.direction
                    if self.speed <= 0:
                        self.speed = 0
                if self.speed // self.direction < 0:
                    self.speed += self.direction
                    if self.speed <= 0:
                        self.speed = 0
                # Проверка на поверхность над гранатой(потолок), i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Проверка на поверхность под гранатой(пол), i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # Обновление позиции гранаты
        self.rect.x += dx + screen_scroll
        self.rect.y += dy - screen_scrolly

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
                print("здоровье игрока:", player.health - self.damage, "здоровье второго игрока:", enemy.health)
            if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * (enemy.scale) and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * (enemy.scale):
                player2.health -= 25 + self.damage + abs(self.rect.centerx - enemy.rect.centerx)
                print("здоровье игрока:", player.health, "здоровье второго игрока:", enemy.health - self.damage)


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
        self.rect.x += screen_scroll
        self.rect.y += screen_scrolly
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

# Создаем пустой tile список
world_data = []
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
player, health_bar, enemy = world.process_data(world_data)
# player, health_bar, enemy, health_bar1 = world.process_data(world_data)

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

        """# Рисуем здоровье второго игрока
        health_bar1.draw(enemy.health)
        # Рисуем запас патронов второго игрока
        draw_text('AMMO: ', font, WHITE, SCREEN_WIDTH - 350, 35)
        for x in range(enemy.ammo):
            screen.blit(bullet_img, ((SCREEN_WIDTH - 270) + (x * 10), 40))
        # Рисуем запас гранат второго игрока
        draw_text('GRENADES: ', font, WHITE, SCREEN_WIDTH - 350, 60)
        for x in range(enemy.grenades):
            screen.blit(grenade_img, ((SCREEN_WIDTH - 225) + (x * 15), 60))"""

        player.update()
        player.draw()

        # enemy.update()
        # enemy.draw()
        # ---------------------------------------------------

        # ---------------------------------------------------
        # Обновляем и рисуем группы(group)

        bullet_group.update()
        bullet_group.draw(screen)

        # Хитбоксы за задним фоном
        hitbox_group.update()
        hitbox_group.draw(screen)

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
            if moving_left or moving_right:
                player.update_action(1)  # 1: Бег
            else:
                player.update_action(0)  # 0: Бездействие
            screen_scroll = player.move(moving_left, moving_right, moving_down, moving_up)
            screen_scrolly = player.move(moving_left, moving_right, moving_down, moving_up)

        else:
            if restart_button.draw(screen):
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar, enemy = world.process_data(world_data)
                ##player, health_bar, enemy, health_bar1 = world.process_data(world_data)

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
        # ---------------------------------------------------
        # Отжатие клавиш второго игрока

    pygame.display.update()

pygame.quit()
