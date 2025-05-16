import pygame
import os
import random
import math
pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
MOON = pygame.image.load(os.path.join("Assets/Other", "moon.png"))
STARS = pygame.image.load(os.path.join("Assets/Other", "stars.png"))
SUN = pygame.image.load(os.path.join("Assets/Other", "sun.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# Day-Night Cycle Constants
DAY_COLOR = (255, 255, 255)  # White for day
NIGHT_COLOR = (20, 20, 50)   # Dark blue for night
CYCLE_LENGTH = 1000          # Points until a full day-night cycle
HOURS_PER_CYCLE = 24         # 24 hours in a day


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

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

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
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


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
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1


class DayNightCycle:
    def __init__(self):
        self.cycle_position = 0  # 0 to 1 representing position in day/night cycle
        self.start_hour = 6      # Start at 6 AM
        self.moon_x = SCREEN_WIDTH // 4
        self.moon_y = 100
        self.stars_opacity = 0
        
    def update(self, points):
        # Update cycle position based on points
        self.cycle_position = (points % CYCLE_LENGTH) / CYCLE_LENGTH
        
    def get_current_color(self):
        # Transition smoothly between day and night
        # Use cosine function for smooth transition (noon is brightest, midnight is darkest)
        brightness = (math.cos(2 * math.pi * self.cycle_position) + 1) / 2
        
        # Interpolate between night and day colors
        r = int(NIGHT_COLOR[0] + (DAY_COLOR[0] - NIGHT_COLOR[0]) * brightness)
        g = int(NIGHT_COLOR[1] + (DAY_COLOR[1] - NIGHT_COLOR[1]) * brightness)
        b = int(NIGHT_COLOR[2] + (DAY_COLOR[2] - NIGHT_COLOR[2]) * brightness)
        
        return (r, g, b)
    
    def get_current_time(self):
        # Calculate the current hour based on cycle position
        current_hour = (self.start_hour + self.cycle_position * HOURS_PER_CYCLE) % HOURS_PER_CYCLE
        hour = int(current_hour)
        minute = int((current_hour - hour) * 60)
        
        # Return formatted time string
        am_pm = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        if hour_12 == 0:
            hour_12 = 12
            
        return f"{hour_12:02d}:{minute:02d} {am_pm}"
    
    def is_night(self):
        # Return true if it's night time (6 PM to 6 AM)
        current_hour = (self.start_hour + self.cycle_position * HOURS_PER_CYCLE) % HOURS_PER_CYCLE
        return 18 <= current_hour or current_hour < 6
    
    def get_night_opacity(self):
        # Calculate how "night" it is from 0 (day) to 1 (full night)
        current_hour = (self.start_hour + self.cycle_position * HOURS_PER_CYCLE) % HOURS_PER_CYCLE
        
        # Sunrise transition: 5 AM to 7 AM
        if 5 <= current_hour < 7:
            return max(0, 1 - (current_hour - 5) / 2)
        
        # Sunset transition: 5 PM to 7 PM
        elif 17 <= current_hour < 19:
            return min(1, (current_hour - 17) / 2)
        
        # Full night: 7 PM to 5 AM
        elif current_hour >= 19 or current_hour < 5:
            return 1
        
        # Full day: 7 AM to 5 PM
        else:
            return 0
    
    def get_day_opacity(self):
        # The inverse of night opacity - how "day" it is from 0 (night) to 1 (full day)
        return 1 - self.get_night_opacity()
    
    def draw(self, SCREEN, font):
        # Create a transparent overlay surface for the day/night effect
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Get night and day opacity
        night_opacity = self.get_night_opacity()
        day_opacity = self.get_day_opacity()
        
        # Draw the sun during day
        if day_opacity > 0:
            # Sun is visible based on how bright it is
            sun_alpha = int(255 * day_opacity)
            sun_surface = SUN.copy()
            sun_surface.set_alpha(sun_alpha)
            
            # Calculate sun position based on time (opposite to moon)
            # Sun rises from left and sets to right
            sun_angle = (self.cycle_position * 2 * math.pi) % (2 * math.pi)
            sun_x = SCREEN_WIDTH * (0.5 + 0.4 * math.cos(sun_angle))
            
            # Position the sun higher in the sky to avoid interference with the dinosaur
            # Keep it in the top portion of the screen
            sun_y = 80 - 30 * math.sin(sun_angle)  # Reduced y-coordinate and amplitude
            
            # Only show sun when it's above the horizon
            if math.sin(sun_angle) > -0.2:
                # Scale the sun image to appropriate size
                sun_size = max(64, min(96, 70 + 26 * math.sin(sun_angle)))  # Reduced size range
                scaled_sun = pygame.transform.scale(sun_surface, (sun_size, sun_size))
                
                # Draw the sun in the background
                SCREEN.blit(scaled_sun, (sun_x - scaled_sun.get_width()//2, 
                                         sun_y - scaled_sun.get_height()//2))
        
        # Draw stars first when it's night
        if night_opacity > 0:
            # Make stars visible based on how dark it is
            stars_alpha = int(255 * night_opacity)
            # Create a copy of the stars image with appropriate alpha
            stars_surface = STARS.copy()
            # Apply transparency to stars
            stars_surface.set_alpha(stars_alpha)
            SCREEN.blit(stars_surface, (0, 0))
            
            # Draw moon when it's night
            moon_alpha = int(255 * night_opacity)
            moon_surface = MOON.copy()
            moon_surface.set_alpha(moon_alpha)
            
            # Calculate moon position based on time
            # Moon rises from right and sets to left
            moon_angle = (self.cycle_position * 2 * math.pi + math.pi) % (2 * math.pi)  # Offset by π so moon rises at night
            moon_x = SCREEN_WIDTH * (0.5 + 0.4 * math.cos(moon_angle))  # Moon moves horizontally across screen
            
            # Position the moon higher in the sky to avoid interference with the dinosaur
            # Keep it in the top portion of the screen
            moon_y = 80 - 30 * math.sin(moon_angle)  # Reduced y-coordinate and amplitude
            
            # Only show moon when it's above the horizon
            if math.sin(moon_angle) > -0.2:  # Allow moon to be slightly below horizon before disappearing
                # Scale the moon if needed to make it smaller
                moon_size = moon_surface.get_width()
                if moon_size > 80:  # If moon is too large
                    scaled_moon = pygame.transform.scale(moon_surface, (80, 80))
                    SCREEN.blit(scaled_moon, (moon_x - scaled_moon.get_width()//2, 
                                            moon_y - scaled_moon.get_height()//2))
                else:
                    SCREEN.blit(moon_surface, (moon_x - moon_surface.get_width()//2, 
                                            moon_y - moon_surface.get_height()//2))
        
        # Fill the overlay with night color based on opacity
        day_night_alpha = int(125 * night_opacity)
        overlay.fill((NIGHT_COLOR[0], NIGHT_COLOR[1], NIGHT_COLOR[2], day_night_alpha))
        
        # Draw the overlay
        SCREEN.blit(overlay, (0, 0))
        
        # Draw clock at the top center
        time_text = font.render(self.get_current_time(), True, (0, 0, 0))
        time_rect = time_text.get_rect()
        time_rect.center = (SCREEN_WIDTH // 2, 40)
        
        # Add a white background behind the clock to make it more readable
        bg_rect = pygame.Rect(time_rect)
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(SCREEN, (255, 255, 255), bg_rect, border_radius=10)
        pygame.draw.rect(SCREEN, (0, 0, 0), bg_rect, 2, border_radius=10)
        
        SCREEN.blit(time_text, time_rect)


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    day_night_cycle = DayNightCycle()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Fill screen with day/night color instead of just white
        bg_color = day_night_cycle.get_current_color()
        SCREEN.fill(bg_color)
        
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        # Update day/night cycle based on points
        day_night_cycle.update(points)
        day_night_cycle.draw(SCREEN, font)

        score()

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

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
            if event.type == pygame.KEYDOWN:
                main()


menu(death_count=0)
