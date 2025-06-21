import pygame
import os
import random
import math

# Power-up Configuration Constants
POWER_UP_SPAWN_FREQ_TEST = (100, 200)  # Fast spawning for testing
POWER_UP_SPAWN_FREQ_NORMAL = (300, 500)  # Normal game spawning
POWER_UP_OBSTACLE_BUFFER = 500  # Distance buffer from obstacles
POWER_UP_WIDTH = 40  # Power-up collision width

# Power-up Durations (in frames)
SHIELD_DURATION = 10 * 30  # 10 seconds at 30 FPS
MULTIPLIER_DURATION = 10 * 30  # 10 seconds at 30 FPS

SHIELD = pygame.image.load(os.path.join("Assets/Other", "Shield.png"))


class PowerUp:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image.get_rect()
        self.rect.x = 1100 + random.randint(800, 1200)
        self.rect.y = 300  # Fixed height for better accessibility
        self.animation_counter = 0

    def update(self, game_speed):
        self.rect.x -= game_speed
        self.animation_counter += 0.1
        self.rect.y += int(math.sin(self.animation_counter) * 2)
        if self.rect.x < -self.rect.width:
            return True  # Mark for removal
        return False

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)
        glow_radius = self.rect.width // 2 + 5
        glow_color = (0, 0, 255, 50) if self.type == "shield" else (255, 0, 0, 50)
        glow_surface = pygame.Surface(
            (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            glow_surface, glow_color, (glow_radius, glow_radius), glow_radius
        )
        SCREEN.blit(
            glow_surface,
            (self.rect.centerx - glow_radius, self.rect.centery - glow_radius),
        )


class ShieldPowerUp(PowerUp):
    def __init__(self):
        super().__init__(SHIELD, "shield")
        self.rect.y = 300


class ScoreMultiplier(PowerUp):
    IMAGE = None

    def __init__(self):
        if ScoreMultiplier.IMAGE is None:
            MULTIPLIER = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(MULTIPLIER, (255, 0, 0, 180), (20, 20), 20)
            font = pygame.font.Font("freesansbold.ttf", 20)
            text = font.render("2x", True, (255, 255, 255))
            text_rect = text.get_rect(center=(20, 20))
            MULTIPLIER.blit(text, text_rect)
            ScoreMultiplier.IMAGE = MULTIPLIER
        super().__init__(ScoreMultiplier.IMAGE, "multiplier")
        self.rect.y = 300


class PowerUpState:
    """Manages power-up state and visual indicators for the player"""

    def __init__(self):
        self.score_multiplier = 1
        self.multiplier_timer = 0

    def activate_multiplier(self):
        self.score_multiplier *= 2
        self.multiplier_timer = MULTIPLIER_DURATION

    def update(self):
        """Update power-up timers"""
        if self.score_multiplier > 1:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.score_multiplier = 1
                self.multiplier_timer = 0


class PowerUpManager:
    """Manages power-up spawning, updates, and collision detection"""

    def __init__(self, testing_mode=False, screen_width=1100):
        self.power_ups = []
        self.spawn_timer = 0
        self.testing_mode = testing_mode
        self.screen_width = screen_width

        # Set spawn frequency based on mode
        freq_range = (
            POWER_UP_SPAWN_FREQ_TEST if testing_mode else POWER_UP_SPAWN_FREQ_NORMAL
        )
        self.spawn_frequency = random.randint(*freq_range)

    def update(self, game_speed, obstacles):
        """Update all power-ups and handle spawning"""
        # Update existing power-ups
        for power_up in self.power_ups[:]:
            remove = power_up.update(game_speed)
            if remove:
                self.power_ups.remove(power_up)

        # Handle spawning
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_frequency:
            self._try_spawn_powerup(obstacles)

    def _try_spawn_powerup(self, obstacles):
        """Attempt to spawn a power-up if no obstacles are in the way"""
        spawn_x = self.screen_width + random.randint(200, 400)
        can_spawn = True

        # Check against all obstacles with buffer spacing
        for obstacle in obstacles:
            obstacle_end_x = obstacle.rect.x + obstacle.rect.width
            if (
                spawn_x < obstacle_end_x + POWER_UP_OBSTACLE_BUFFER
                and spawn_x + POWER_UP_WIDTH
                > obstacle.rect.x - POWER_UP_OBSTACLE_BUFFER
            ):
                can_spawn = False
                break

        if can_spawn:
            # Randomly choose power-up type (only multiplier for now, shield handled separately)
            self.power_ups.append(ScoreMultiplier())

            self.spawn_timer = 0
            # Reset spawn frequency
            freq_range = (
                POWER_UP_SPAWN_FREQ_TEST
                if self.testing_mode
                else POWER_UP_SPAWN_FREQ_NORMAL
            )
            self.spawn_frequency = random.randint(*freq_range)

    def draw_all(self, screen):
        """Draw all active power-ups"""
        for power_up in self.power_ups:
            power_up.draw(screen)

    def check_collisions(self, player_rect):
        """Check for collisions with player and return collected power-ups"""
        collected = []
        for power_up in self.power_ups[:]:
            if player_rect.colliderect(power_up.rect):
                collected.append(power_up)
                self.power_ups.remove(power_up)
        return collected
