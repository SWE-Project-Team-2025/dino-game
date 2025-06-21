import os
import random

import pygame
from power_ups import PowerUpManager, PowerUpState

from day_night import DayNightEnvironment

pygame.init()
pygame.mixer.init()  # Ses sistemini başlatır
pygame.mixer.set_num_channels(3)  # 3 farklı kanal: jump, collision, score

# Load Sound Effects
JUMP_SOUND = pygame.mixer.Sound("Assets/Sound/jump.wav")
JUMP_SOUND.set_volume(0.5)  # Zıplama sesi: orta ses düzeyi
COLLISION_SOUND = pygame.mixer.Sound("Assets/Sound/collision.wav")
COLLISION_SOUND.set_volume(0.7)  # Çarpma sesi: biraz daha yüksek
SCORE_SOUND = pygame.mixer.Sound("Assets/Sound/score.wav")
SCORE_SOUND.set_volume(0.3)  # Puan sesi: hafif ve melodik
JUMP_CHANNEL = pygame.mixer.Channel(0)
COLLISION_CHANNEL = pygame.mixer.Channel(1)
SCORE_CHANNEL = pygame.mixer.Channel(2)


# Game Configuration
TESTING_MODE = False  # Set to False for production

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [
    pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png")),
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png")),
]

BIRD = [
    pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("Assets/Bird", "Bird2.png")),
]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.collision_rect = self.dino_rect.inflate(-50, -50)
        self.power_up_state = PowerUpState()

        self.has_shield = False
        self.shield_timer = 0  # counts down in frames or seconds

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        self.collision_rect = self.dino_rect.inflate(-50, -50)

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            JUMP_CHANNEL.play(JUMP_SOUND)  # Sadece zıplama başladığında ses çalsın
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
            # Call the shield update function here
        self.update_shield()
        self.power_up_state.update()

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:

            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def activate_shield(
        self, duration=500
    ):  # duration could be in frames (~seconds at 30 FPS)
        self.has_shield = True
        self.shield_timer = duration

    def update_shield(self):
        if self.has_shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.has_shield = False
                self.shield_timer = 0

    def draw_shield_indicator(self, SCREEN):
        if self.has_shield:
            # Example: draw a simple shield icon or circle around dino
            pygame.draw.circle(
                SCREEN,
                (0, 0, 255),
                (self.dino_rect.centerx, self.dino_rect.centery),
                40,
                3,
            )
            # Or add a timer bar (optional)


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type, y_pos):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = y_pos

        self.collision_rect = self.rect.inflate(-45, -45)

    def update(self):
        self.rect.x -= game_speed
        self.collision_rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, 325)


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, 300)


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type, random.choice([230, 280]))
        self.collision_rect = self.rect.inflate(-30, -20)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, death_count
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    environment = DayNightEnvironment(SCREEN_WIDTH, SCREEN_HEIGHT)
    power_up_manager = PowerUpManager(
        testing_mode=TESTING_MODE, screen_width=SCREEN_WIDTH
    )
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    environment.update(points)
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    enable_powerups = True  # Set to False to disable powerups for testing

    # Shield variables
    shield_active = False
    shield_duration = 300  # Duration in frames (e.g., 10 seconds if 30 FPS)
    shield_timer = 0

    # Load shield power-up image (add your shield image in Assets/Other folder)
    SHIELD_IMG = pygame.image.load(os.path.join("Assets/Other", "Shield.png"))
    shield_power_up = None  # No shield power-up on screen initially
    shield_spawn_timer = 0  # Timer to spawn shield power-up occasionally

    def score():
        global points, game_speed
        points += player.power_up_state.score_multiplier
        if int(points) % 100 == 0 and int(points) != 0:
            SCORE_CHANNEL.play(SCORE_SOUND)
            game_speed += 1

        text = font.render(
            f"Points: {int(points)}", True, environment.cycle.get_text_color()
        )
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

        if player.power_up_state.score_multiplier > 1:
            multiplier_text = font.render(
                f"{player.power_up_state.score_multiplier}x Score: {
                    player.power_up_state.multiplier_timer // 30}s",
                True,
                (255, 0, 0),
            )
            multiplier_text_rect = multiplier_text.get_rect()
            multiplier_text_rect.topleft = (textRect.left, textRect.bottom + 10)
            SCREEN.blit(multiplier_text, multiplier_text_rect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def draw_shield_indicator():
        # Draw a simple shield icon at top-left or near player
        SCREEN.blit(SHIELD_IMG, (player.dino_rect.x, player.dino_rect.y - 40))
        # Optional: Draw a timer bar or countdown text
        timer_text = font.render(
            f"Shield: {shield_timer // 30}", True, environment.cycle.get_text_color()
        )
        SCREEN.blit(timer_text, (player.dino_rect.x, player.dino_rect.y - 60))

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Update day/night cycle based on points
        environment.update(points)

        # Fill screen with day/night color
        bg_color = environment.get_bg_color()
        SCREEN.fill(bg_color)

        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.draw_shield_indicator(SCREEN)
        player.update(userInput)

        # Spawn obstacles if none present
        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif choice == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif choice == 2:
                obstacles.append(Bird(BIRD))

        # Handle obstacles update and collision
        for obstacle in obstacles[:]:  # Copy list to avoid issues while removing
            obstacle.draw(SCREEN)
            obstacle.update()

            if player.collision_rect.colliderect(obstacle.collision_rect):
                COLLISION_CHANNEL.play(COLLISION_SOUND)  # Hit sound
                if shield_active:
                    # Shield protects player once, remove obstacle and shield
                    obstacles.remove(obstacle)
                    shield_active = False
                    shield_timer = 0
                else:
                    points = int(points)
                    pygame.time.delay(800)
                    death_count += 1
                    return

        # Shield power-up spawn logic (every ~10-20 seconds)
        shield_spawn_timer += 1
        if shield_power_up is None and shield_spawn_timer > 300:
            # Spawn shield somewhere on the right side randomly
            shield_power_up = pygame.Rect(
                SCREEN_WIDTH + random.randint(500, 1000),
                random.randint(250, 350),
                SHIELD_IMG.get_width(),
                SHIELD_IMG.get_height(),
            )
            shield_spawn_timer = 0

        # Move shield power-up left with game speed
        if shield_power_up:
            shield_power_up.x -= game_speed
            SCREEN.blit(SHIELD_IMG, (shield_power_up.x, shield_power_up.y))

            # Check collision with player to collect shield
            if player.dino_rect.colliderect(shield_power_up) and not shield_active:
                shield_active = True
                shield_timer = shield_duration
                shield_power_up = None  # Remove shield power-up from screen

            # Remove shield power-up if it goes off screen
            if shield_power_up and shield_power_up.x < -SHIELD_IMG.get_width():
                shield_power_up = None

        # Update shield timer and disable shield if expired
        if shield_active:
            shield_timer -= 1
            draw_shield_indicator()
            if shield_timer <= 0:
                shield_active = False
                shield_timer = 0

        if enable_powerups:
            power_up_manager.update(game_speed, obstacles)
            power_up_manager.draw_all(SCREEN)

            # Check for power-up collisions
            collected_power_ups = power_up_manager.check_collisions(player.dino_rect)
            for power_up in collected_power_ups:
                if power_up.type == "multiplier":
                    player.power_up_state.activate_multiplier()

        background()

        cloud.draw(SCREEN)
        cloud.update()

        # Draw day/night environment
        environment.draw(SCREEN, font)

        score()

        clock.tick(30)
        pygame.display.update()


death_count = 0


def menu():
    global points, death_count
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font("freesansbold.ttf", 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()
            if event.type == pygame.KEYDOWN:
                main()
                break


menu()
