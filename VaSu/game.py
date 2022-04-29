import sys
from Player import Player
from Player import PlayerProjectile
import pygame

pygame.init()

display = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()




player = Player(400, 300, 32, 32)

display_scroll = [0, 0]

player_projectiles = []

while True:
    display.fill((24, 164, 86))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    print(mouse_x, mouse_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            pygame.QUIT

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player_projectiles.append(PlayerProjectile(player.x, player.y, mouse_x, mouse_y))

    keys = pygame.key.get_pressed()

    pygame.draw.rect(display, (255, 255, 255), (100-display_scroll[0], 100-display_scroll[1], 16, 16))

    if keys[pygame.K_a]:
        display_scroll[0] -= 5

        player.moving_left = True
        player.watching_right = False
        player.watching_left = True

        for bullet in player_projectiles:
            bullet.x += 5
    if keys[pygame.K_d]:
        display_scroll[0] += 5

        player.moving_right = True
        player.watching_left = False
        player.watching_right = True

        for bullet in player_projectiles:
            bullet.x -= 5
    if keys[pygame.K_w]:
        display_scroll[1] -= 5

        player.moving_up_or_down = True

        for bullet in player_projectiles:
            bullet.y += 5
    if keys[pygame.K_s]:
        display_scroll[1] += 5

        player.moving_up_or_down = True

        for bullet in player_projectiles:
            bullet.y -= 5

    player.main(display)

    for bullet in player_projectiles:
        bullet.main(display)

    clock.tick(60)
    pygame.display.update()
