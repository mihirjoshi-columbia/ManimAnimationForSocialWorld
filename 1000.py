import pygame
import random
import time

# ------------------ Configuration ------------------
# Window dimensions and regions
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
BAR_CHART_WIDTH = 200         # Left-side region for bar chart
DICE_AREA_MARGIN = 40         # Margin before dice grid starts
FPS = 60                      # Frames per second

# Grid parameters (10x10 grid)
COLUMNS = 10
ROWS = 10
NUM_DICE = COLUMNS * ROWS
DICE_SIZE = 40                # Size of each dice square
SPACING = 10                  # Space between dice

# Update intervals for dice (progressively faster)
BASE_INTERVAL = 1.0  # Slowest dice update every 1.0 sec (changed from 0.5)
MIN_INTERVAL  = 0.2  # Fastest dice update every 0.2 sec (changed from 0.05)

# Simulation stop condition
MAX_ROLLS = 1000

# Bar chart parameters
BAR_WIDTH = 50
BAR_MAX_HEIGHT = 400        # Height corresponding to 1000 rolls
BAR_BOTTOM = 550            # y-coordinate for bottom of bars
LEFT_BAR_X = 50            # x position for left bar
RIGHT_BAR_X = WINDOW_WIDTH - 200 # x position for right bar

# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (30, 30, 30)
BLUE = (50, 150, 255)
RED  = (255, 100, 100)

pygame.init()
FONT = pygame.font.SysFont("Arial", 24)

# ------------------ Dice Class ------------------
class Dice:
    def __init__(self, x, y, size, update_interval):
        self.x = x
        self.y = y
        self.size = size
        self.update_interval = update_interval
        self.last_update_time = time.time()
        self.value = random.randint(1, 20)
    
    def update(self, current_time):
        """Update dice face if the update interval has passed.
           Returns True if updated, otherwise False."""
        if current_time - self.last_update_time >= self.update_interval:
            self.value = random.randint(1, 20)
            self.last_update_time = current_time
            return True
        return False
    
    def draw(self, surface):
        # Draw dice background and border
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.size, self.size), 2)
        # Render the dice value and center it
        text = FONT.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.size/2, self.y + self.size/2))
        surface.blit(text, text_rect)

# ------------------ Setup Dice Grid ------------------
# Compute grid dimensions
grid_width = COLUMNS * DICE_SIZE + (COLUMNS - 1) * SPACING
grid_height = ROWS * DICE_SIZE + (ROWS - 1) * SPACING
# Place grid in the dice area (right side of the window)
grid_start_x = BAR_CHART_WIDTH + DICE_AREA_MARGIN
grid_start_y = (WINDOW_HEIGHT - grid_height) // 2

# Create dice objects with update intervals that interpolate from BASE_INTERVAL to MIN_INTERVAL
dice_list = []
for i in range(NUM_DICE):
    col = i % COLUMNS
    row = i // COLUMNS
    x = grid_start_x + col * (DICE_SIZE + SPACING)
    y = grid_start_y + row * (DICE_SIZE + SPACING)
    # Linear interpolation: first dice (i=0) gets BASE_INTERVAL, last gets MIN_INTERVAL.
    update_interval = BASE_INTERVAL - (i / (NUM_DICE - 1)) * (BASE_INTERVAL - MIN_INTERVAL)
    dice_list.append(Dice(x, y, DICE_SIZE, update_interval))

# ------------------ Global Roll Counters ------------------
global_roll_count = 0
count_low = 0   # outcomes 1-13
count_high = 0  # outcomes 14-20

# ------------------ Pygame Setup ------------------
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("20-Sided Dice with Bar Chart")
clock = pygame.time.Clock()

running = True
simulation_active = True  # Whether dice continue updating

# ------------------ Main Loop ------------------
while running:
    current_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Only update dice if simulation is active (less than MAX_ROLLS)
    if simulation_active:
        # Update each dice; count each update event as a roll.
        for dice in dice_list:
            if global_roll_count < MAX_ROLLS and dice.update(current_time):
                global_roll_count += 1
                # Update our counters based on the new dice value
                if 1 <= dice.value <= 13:
                    count_low += 1
                else:
                    count_high += 1
                # If we've reached MAX_ROLLS, stop further updates.
                if global_roll_count >= MAX_ROLLS:
                    simulation_active = False
                    break

    # ------------------ Drawing ------------------
    screen.fill(BG_COLOR)
    
    # --- Draw the Bar Chart ---
    # Calculate bar heights proportionally to MAX_ROLLS
    low_bar_height = (count_low / MAX_ROLLS) * BAR_MAX_HEIGHT
    high_bar_height = (count_high / MAX_ROLLS) * BAR_MAX_HEIGHT
    
    # Draw the "Low" bar (1-13) in blue on the left
    pygame.draw.rect(screen, BLUE, (LEFT_BAR_X, BAR_BOTTOM - low_bar_height, BAR_WIDTH, low_bar_height))
    # Draw the "High" bar (14-20) in red on the right
    pygame.draw.rect(screen, RED, (RIGHT_BAR_X, BAR_BOTTOM - high_bar_height, BAR_WIDTH, high_bar_height))
    
    # Draw labels for the bars
    low_label = FONT.render(f"1-13: {count_low}", True, WHITE)
    high_label = FONT.render(f"14-20: {count_high}", True, WHITE)
    screen.blit(low_label, (LEFT_BAR_X, BAR_BOTTOM + 10))
    screen.blit(high_label, (RIGHT_BAR_X, BAR_BOTTOM + 10))
    
    # Split the titles for each bar
    left_title = FONT.render("Low Rolls (1-13)", True, WHITE)
    right_title = FONT.render("High Rolls (14-20)", True, WHITE)
    screen.blit(left_title, (LEFT_BAR_X - 10, 10))
    screen.blit(right_title, (RIGHT_BAR_X - 20, 10))
    
    # --- Draw the Dice Grid on the right ---
    for dice in dice_list:
        dice.draw(screen)
    
    # If simulation has ended, display a message.
    if not simulation_active:
        end_msg = FONT.render("Simulation finished (1000 rolls reached)", True, WHITE)
        msg_rect = end_msg.get_rect(center=(WINDOW_WIDTH//2, 30))
        screen.blit(end_msg, msg_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

# Wait a few seconds before quitting, to let the user see final results.
pygame.time.delay(3000)
pygame.quit()
