import pygame
import random
import os

SHIELD_IMAGE = pygame.image.load(os.path.join("Assets/Other", "Shield.png"))

class ShieldPowerUp:
    def __init__(self):
        self.image = SHIELD_IMAGE
        self.x = 1100 + random.randint(800, 1200)  # spawn off screen right
        self.y = 300  # fixed y (can adjust)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.active = True

    def update(self, game_speed):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            self.active = False  # off screen, deactivate

    def draw(self, SCREEN):
        if self.active:
            SCREEN.blit(self.image, (self.rect.x, self.rect.y))
