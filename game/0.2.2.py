import pygame
from math import atan2, degrees

wn = pygame.display.set_mode((400, 400))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(185, 180))

    def point_at(self, x, y):
        rotated_image = pygame.transform.rotate(self.image, degrees(atan2(x - self.rect.x, y - self.rect.y)))
        new_rect = rotated_image.get_rect(center=self.rect.center)
        wn.fill((0, 0, 0))
        wn.blit(rotated_image, new_rect.topleft)


player = Player()
clock = pygame.time.Clock()  # Create the clock

while True:
    clock.tick(30)  # Use the clock
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    keys = pygame.key.get_pressed()  # Get al the pressed keys
    if keys[pygame.K_w]:
        player.rect.y -= 5
    if keys[pygame.K_s]:
        player.rect.y += 5
    if keys[pygame.K_a]:
        player.rect.x -= 5
    if keys[pygame.K_d]:
        player.rect.x += 5

    player.point_at(*pygame.mouse.get_pos())  # Put this here
    pygame.display.update()