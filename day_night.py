import math
import os

import pygame

# Day-Night Cycle Constants
DAY_COLOR = (255, 255, 255)  # White for day
NIGHT_COLOR = (20, 20, 50)  # Dark blue for night
CYCLE_LENGTH = 1400  # Points until a full day-night cycle
HOURS_PER_CYCLE = 24  # 24 hours in a day

# Load assets for day/night
MOON = pygame.image.load(os.path.join("Assets/Other", "moon.png"))
SUN = pygame.image.load(os.path.join("Assets/Other", "sun.png"))


class DayNightCycle:
    def __init__(self):
        self.cycle_position = 0  # 0 to 1 representing position in day/night cycle
        self.start_hour = 6  # Start at 6 AM

    def update(self, points):
        # Update cycle position based on points
        self.cycle_position = ((points // (CYCLE_LENGTH / 2)) % 2) * 0.5
        self.cycle_movement = (points % CYCLE_LENGTH) / CYCLE_LENGTH

    def get_current_color(self):
        # Transition smoothly between day and night
        # Use cosine function for smooth transition (noon is brightest, midnight is darkest)
        brightness = (math.cos(2 * math.pi * self.cycle_position) + 1) / 2

        # Interpolate between night and day colors
        r = int(NIGHT_COLOR[0] + (DAY_COLOR[0] - NIGHT_COLOR[0]) * brightness)
        g = int(NIGHT_COLOR[1] + (DAY_COLOR[1] - NIGHT_COLOR[1]) * brightness)
        b = int(NIGHT_COLOR[2] + (DAY_COLOR[2] - NIGHT_COLOR[2]) * brightness)

        return (r, g, b)

    def get_text_color(self):
        # calculate text color based on brightness, and then opposite of that
        brightness = (math.cos(2 * math.pi * self.cycle_position) + 1) / 2
        r = int(NIGHT_COLOR[0] + (DAY_COLOR[0] - NIGHT_COLOR[0]) * brightness)
        g = int(NIGHT_COLOR[1] + (DAY_COLOR[1] - NIGHT_COLOR[1]) * brightness)
        b = int(NIGHT_COLOR[2] + (DAY_COLOR[2] - NIGHT_COLOR[2]) * brightness)
        return (255 - r, 255 - g, 255 - b)

    def is_night(self):
        # Return true if it's night time (6 PM to 6 AM)
        current_hour = (
            self.start_hour + self.cycle_position * HOURS_PER_CYCLE
        ) % HOURS_PER_CYCLE
        return 18 <= current_hour or current_hour < 6

    def get_night_opacity(self):
        # Calculate how "night" it is from 0 (day) to 1 (full night)
        current_hour = (
            self.start_hour + self.cycle_position * HOURS_PER_CYCLE
        ) % HOURS_PER_CYCLE

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


class DayNightEnvironment:
    def __init__(self, screen_width, screen_height):
        self.cycle = DayNightCycle()
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, points):
        self.cycle.update(points)

    def get_bg_color(self):
        return self.cycle.get_current_color()

    def draw(self, screen, font):

        # Get night and day opacity
        night_opacity = self.cycle.get_night_opacity()
        day_opacity = self.cycle.get_day_opacity()

        # Draw the sun during day
        if day_opacity > 0:
            self._draw_sun(screen, day_opacity)

        # Draw stars and moon when it's night
        if night_opacity > 0:
            self._draw_night_objects(screen, night_opacity)

    def _draw_sun(self, screen, day_opacity):
        # Sun is visible based on how bright it is
        sun_alpha = int(255 * day_opacity)
        sun_surface = SUN.copy()
        sun_surface.set_alpha(sun_alpha)

        # Calculate sun position based on time (opposite to moon)
        # Sun rises from left and sets to right
        sun_angle = (self.cycle.cycle_movement * 2 * math.pi) % (2 * math.pi)
        sun_x = self.screen_width * (0.5 + 0.4 * math.cos(sun_angle))

        # Position the sun higher in the sky to avoid interference with the dinosaur
        # Keep it in the top portion of the screen
        sun_y = 80 - 30 * math.sin(sun_angle)  # Reduced y-coordinate and amplitude

        # Only show sun when it's above the horizon
        if math.sin(sun_angle) > -0.2:
            # Scale the sun image to appropriate size
            # Reduced size range
            sun_size = max(64, min(96, 70 + 26 * math.sin(sun_angle)))
            scaled_sun = pygame.transform.scale(sun_surface, (sun_size, sun_size))

            # Draw the sun in the background
            screen.blit(
                scaled_sun,
                (
                    sun_x - scaled_sun.get_width() // 2,
                    sun_y - scaled_sun.get_height() // 2,
                ),
            )

    def _draw_night_objects(self, screen, night_opacity):
        # Draw moon when it's night
        moon_alpha = int(255 * night_opacity)
        moon_surface = MOON.copy()
        moon_surface.set_alpha(moon_alpha)

        # Calculate moon position based on time
        # Moon rises from right and sets to left
        moon_angle = (self.cycle.cycle_movement * 2 * math.pi + math.pi) % (
            2 * math.pi
        )  # Offset by π so moon rises at night
        # Moon moves horizontally across screen
        moon_x = self.screen_width * (0.5 + 0.4 * math.cos(moon_angle))

        # Position the moon higher in the sky to avoid interference with the dinosaur
        # Keep it in the top portion of the screen
        moon_y = 80 - 30 * math.sin(moon_angle)  # Reduced y-coordinate and amplitude

        # Only show moon when it's above the horizon
        if (
            math.sin(moon_angle) > -0.2
        ):  # Allow moon to be slightly below horizon before disappearing
            # Scale the moon if needed to make it smaller
            moon_size = moon_surface.get_width()
            if moon_size > 80:  # If moon is too large
                scaled_moon = pygame.transform.scale(moon_surface, (80, 80))
                screen.blit(
                    scaled_moon,
                    (
                        moon_x - scaled_moon.get_width() // 2,
                        moon_y - scaled_moon.get_height() // 2,
                    ),
                )
            else:
                screen.blit(
                    moon_surface,
                    (
                        moon_x - moon_surface.get_width() // 2,
                        moon_y - moon_surface.get_height() // 2,
                    ),
                )
