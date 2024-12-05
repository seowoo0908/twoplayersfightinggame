import pygame
import sys
import math
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load sound effects
try:
    sword_swing_sound = pygame.mixer.Sound("sounds/sword_swing.wav")
    sword_hit_sound = pygame.mixer.Sound("sounds/sword_hit.wav")
    jump_sound = pygame.mixer.Sound("sounds/jump.wav")
    button_click_sound = pygame.mixer.Sound("sounds/button_click.wav")
    roblox_oof_sound = pygame.mixer.Sound("sounds/roblox_oof.wav")
except:
    # Create default sounds if files don't exist
    sword_swing_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    sword_hit_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    jump_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    button_click_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    roblox_oof_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))

# Set sound volumes
sword_swing_sound.set_volume(0.3)
sword_hit_sound.set_volume(0.4)
jump_sound.set_volume(0.2)
button_click_sound.set_volume(0.3)
roblox_oof_sound.set_volume(0.7)  # Make the oof loud and clear

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Stickman Sword Fighting Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Background colors
SKY_COLORS = [
    (70, 30, 70),   # Dark purple
    (120, 40, 40),  # Dark red
    (180, 60, 60),  # Red
    (220, 100, 50), # Orange
]

# Constants
GRAVITY = 0.8

# Cloud class
class Cloud:
    def __init__(self):
        self.x = random.randint(-100, WINDOW_WIDTH + 100)
        self.y = random.randint(20, 150)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)
        self.points = [(random.randint(-20, 20), random.randint(-10, 10)) for _ in range(8)]
        
    def move(self):
        self.x += self.speed
        if self.x > WINDOW_WIDTH + 100:
            self.x = -100
            self.y = random.randint(20, 150)
            
    def draw(self, screen):
        cloud_color = (255, 255, 255, 128)  # White with transparency
        points = [(self.x + x, self.y + y) for x, y in self.points]
        pygame.draw.polygon(screen, cloud_color, points)

# Mountain class
class Mountain:
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.points = [
            (x - random.randint(50, 100), WINDOW_HEIGHT),  # Left base
            (x, WINDOW_HEIGHT - height),                   # Peak
            (x + random.randint(50, 100), WINDOW_HEIGHT)   # Right base
        ]
        self.color = (60, 30, 30)  # Dark brown
        self.snow_line = height * 0.3
        
    def draw(self, screen):
        # Draw mountain body
        pygame.draw.polygon(screen, self.color, self.points)
        
        # Draw snow cap
        snow_points = [
            (self.points[0][0] + (self.points[1][0] - self.points[0][0]) * 0.3, 
             WINDOW_HEIGHT - self.height + self.snow_line),
            self.points[1],  # Peak
            (self.points[2][0] - (self.points[2][0] - self.points[1][0]) * 0.3, 
             WINDOW_HEIGHT - self.height + self.snow_line)
        ]
        pygame.draw.polygon(screen, WHITE, snow_points)

# Bench class
class Bench:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (139, 69, 19)  # Brown color for wooden bench

    def draw(self, screen):
        # Draw main bench seat
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw bench legs
        leg_width = 10
        leg_height = 20
        pygame.draw.rect(screen, self.color, (self.x + 10, self.y + self.height, leg_width, leg_height))
        pygame.draw.rect(screen, self.color, (self.x + self.width - 20, self.y + self.height, leg_width, leg_height))

    def check_collision(self, player):
        # Check if player's feet are near the platform
        player_feet = player.y + player.height
        player_center = player.x
        
        # Check if player is within horizontal bounds of bench
        if self.x <= player_center <= self.x + self.width:
            # Check if player is at the right height to land
            if self.y - 5 <= player_feet <= self.y + 5:
                if player.velocity_y >= 0:  # Only if falling or standing
                    player.y = self.y - player.height
                    player.velocity_y = 0
                    player.is_jumping = False
                    player.on_platform = True
                    player.current_platform = self
                    return True
            # Check if player hits bottom of platform when jumping
            elif player.velocity_y < 0 and player_feet < self.y + self.height:
                if abs(player_feet - (self.y + self.height)) < 10:
                    player.velocity_y = 0
        
        # If player walks off platform
        if player.current_platform == self:
            if not (self.x <= player_center <= self.x + self.width):
                player.on_platform = False
                player.current_platform = None
        
        return False

# Player class
class Player:
    def __init__(self, x, y, color, facing_right, controls, player_num):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 50
        self.color = color
        self.facing_right = facing_right
        self.velocity_y = 0
        self.is_jumping = False
        self.health = 100
        self.controls = controls
        self.attacking = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        self.player_num = player_num
        self.weapon = "sword"  # Default weapon
        self.arrow = None  # For bow attacks
        self.speed = 5  # Movement speed
        self.jump_power = -15  # Jump strength
        self.on_platform = False  # Track if player is on a platform
        self.current_platform = None  # Track which platform player is on
        self.last_hit_time = 0  # Add this for hit sound cooldown
    
    def move(self):
        keys = pygame.key.get_pressed()
        old_x = self.x
        old_y = self.y
        
        # Horizontal movement
        if keys[self.controls["left"]]:
            self.x -= self.speed
            self.facing_right = False
        if keys[self.controls["right"]]:
            self.x += self.speed
            self.facing_right = True
        
        # Keep player in bounds
        self.x = max(self.width//2, min(self.x, WINDOW_WIDTH - self.width//2))
        
        # Jumping
        if keys[self.controls["jump"]] and not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.on_platform = False
            self.current_platform = None
            jump_sound.play()  # Play jump sound
        
        # Apply gravity if not on platform
        if not self.on_platform:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
        
        # Ground collision
        if self.y + self.height > WINDOW_HEIGHT - 20:  # Ground height is 20
            self.y = WINDOW_HEIGHT - 20 - self.height
            self.velocity_y = 0
            self.is_jumping = False
            self.on_platform = True
            self.current_platform = None

    def draw(self, screen):
        # Draw stickman
        # Head
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + 10)), 10)
        
        # Body
        pygame.draw.line(screen, self.color, 
                        (self.x, self.y + 20), 
                        (self.x, self.y + 40), 3)
        
        # Arms
        if self.attacking and self.weapon == "sword":
            # Attacking pose for sword
            arm_angle = (self.attack_frame / 30) * math.pi  # Swing animation
            if not self.facing_right:
                arm_angle = math.pi - arm_angle
            
            # Draw arm with sword
            arm_end_x = self.x + math.cos(arm_angle) * 20
            arm_end_y = self.y + 25 - math.sin(arm_angle) * 20
            pygame.draw.line(screen, self.color, 
                           (self.x, self.y + 25),
                           (arm_end_x, arm_end_y), 3)
            
            # Draw sword with handle and blade
            sword_angle = arm_angle
            # Handle
            handle_length = 10
            handle_end_x = arm_end_x + math.cos(sword_angle) * handle_length
            handle_end_y = arm_end_y - math.sin(sword_angle) * handle_length
            pygame.draw.line(screen, (139, 69, 19),  # Brown handle
                           (arm_end_x, arm_end_y),
                           (handle_end_x, handle_end_y), 5)
            
            # Blade
            blade_length = 35
            blade_end_x = handle_end_x + math.cos(sword_angle) * blade_length
            blade_end_y = handle_end_y - math.sin(sword_angle) * blade_length
            # Main blade
            pygame.draw.line(screen, (192, 192, 192),  # Silver blade
                           (handle_end_x, handle_end_y),
                           (blade_end_x, blade_end_y), 4)
            
            # Cross guard
            guard_size = 12
            guard_angle = sword_angle + math.pi/2
            guard_x1 = handle_end_x + math.cos(guard_angle) * guard_size
            guard_y1 = handle_end_y - math.sin(guard_angle) * guard_size
            guard_x2 = handle_end_x - math.cos(guard_angle) * guard_size
            guard_y2 = handle_end_y + math.sin(guard_angle) * guard_size
            pygame.draw.line(screen, (139, 69, 19),  # Brown guard
                           (guard_x1, guard_y1),
                           (guard_x2, guard_y2), 4)
            
        elif self.attacking and self.weapon == "bow":
            # Bow shooting pose
            if self.facing_right:
                pygame.draw.line(screen, self.color, 
                               (self.x, self.y + 25),
                               (self.x + 20, self.y + 25), 3)
                # Draw bow
                pygame.draw.arc(screen, (139, 69, 19),
                              (self.x + 15, self.y + 15, 20, 20),
                              -math.pi/2, math.pi/2, 3)
            else:
                pygame.draw.line(screen, self.color,
                               (self.x, self.y + 25),
                               (self.x - 20, self.y + 25), 3)
                # Draw bow
                pygame.draw.arc(screen, (139, 69, 19),
                              (self.x - 35, self.y + 15, 20, 20),
                              math.pi/2, 3*math.pi/2, 3)
        else:
            # Normal arms
            pygame.draw.line(screen, self.color,
                           (self.x, self.y + 25),
                           (self.x + (15 if self.facing_right else -15), self.y + 25), 3)
        
        # Legs
        pygame.draw.line(screen, self.color,
                        (self.x, self.y + 40),
                        (self.x + 10, self.y + 50), 3)
        pygame.draw.line(screen, self.color,
                        (self.x, self.y + 40),
                        (self.x - 10, self.y + 50), 3)
        
        # Draw arrow if shooting
        if self.arrow:
            pygame.draw.line(screen, (139, 69, 19),
                           (self.arrow[0] - 10, self.arrow[1]),
                           (self.arrow[0] + 10, self.arrow[1]), 2)

    def attack(self, other_player):
        current_time = pygame.time.get_ticks()
        
        if not self.attacking and self.attack_cooldown <= 0:
            print(f"Player {self.player_num} starting attack with {self.weapon}")
            self.attacking = True
            self.attack_frame = 0
            
            # For bow, create arrow
            if self.weapon == "bow":
                self.arrow = [self.x + (20 if self.facing_right else -20), self.y]
            # For sword, do immediate damage check
            elif self.weapon == "sword":
                # Calculate distance between players
                distance = abs(self.x - other_player.x)
                if distance < 60:  # Sword range
                    # Check if player is facing the right direction
                    if (self.facing_right and self.x < other_player.x) or (not self.facing_right and self.x > other_player.x):
                        print(f"Player {self.player_num} sword hit!")
                        self.hit_player(other_player)
            
            self.attack_cooldown = 30
            sword_swing_sound.play()  # Play swing sound
        
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            
            # Handle bow attack
            if self.weapon == "bow" and self.arrow:
                # Move arrow
                arrow_speed = 10
                self.arrow[0] += arrow_speed * (1 if self.facing_right else -1)
                
                # Check arrow hit
                if (abs(self.arrow[0] - other_player.x) < 30 and 
                    abs(self.arrow[1] - other_player.y) < 30):
                    print(f"Player {self.player_num} arrow hit!")
                    self.hit_player(other_player)
                    self.arrow = None
                
                # Remove arrow if off screen
                elif self.arrow[0] < 0 or self.arrow[0] > WINDOW_WIDTH:
                    self.arrow = None
            
            # Reset attack after animation
            if self.attack_frame >= 30:
                self.attacking = False
                self.arrow = None
    
    def update_attack(self, other_player):
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            
            # Handle bow attack
            if self.weapon == "bow" and self.arrow:
                # Move arrow
                arrow_speed = 10
                self.arrow[0] += arrow_speed * (1 if self.facing_right else -1)
                
                # Check arrow hit
                if (abs(self.arrow[0] - other_player.x) < 30 and 
                    abs(self.arrow[1] - other_player.y) < 30):
                    print(f"Player {self.player_num} arrow hit!")
                    self.hit_player(other_player)
                    self.arrow = None
                
                # Remove arrow if off screen
                elif self.arrow[0] < 0 or self.arrow[0] > WINDOW_WIDTH:
                    self.arrow = None
            
            # Reset attack after animation
            if self.attack_frame >= 30:
                self.attacking = False
                self.arrow = None
    
    def hit_player(self, other_player):
        # Calculate damage
        if self.weapon == "sword":
            damage = 8  # Reduced from 15
        else:  # bow
            damage = 5  # Reduced from 10
        
        # Apply damage
        other_player.health = max(0, other_player.health - damage)
        print(f"Player {self.player_num} dealt {damage} damage with {self.weapon}! Target health: {other_player.health}")
        
        # Apply knockback
        knockback = 20 if self.weapon == "sword" else 10  # Reduced from 30/15
        direction = 1 if self.facing_right else -1
        other_player.x += knockback * direction
        
        # Keep player in bounds
        other_player.x = max(30, min(other_player.x, WINDOW_WIDTH - 30))
        
        # Play hit sounds
        current_time = pygame.time.get_ticks()
        if current_time - other_player.last_hit_time > 500:  # 500ms cooldown
            sword_hit_sound.play()  # Play hit sound
            roblox_oof_sound.play()  # Play Roblox oof sound
            other_player.last_hit_time = current_time

# Game options
class GameOptions:
    def __init__(self):
        self.p1_weapon = "sword"  # "sword" or "bow"
        self.p2_weapon = "sword"  # "sword" or "bow"

# Create global options
game_options = GameOptions()

class WeaponButton:
    def __init__(self, x, y, width, height, weapon_type, player_num):
        self.rect = pygame.Rect(x, y, width, height)
        self.weapon_type = weapon_type
        self.player_num = player_num
        self.hover = False
        
    def draw(self, screen, font, is_selected):
        # Colors
        if is_selected:
            color = (0, 150, 0) if self.weapon_type == "sword" else (0, 0, 150)
        else:
            base_color = (0, 100, 0) if self.weapon_type == "sword" else (0, 0, 100)
            color = (min(base_color[0] + 30, 255), 
                    min(base_color[1] + 30, 255), 
                    min(base_color[2] + 30, 255)) if self.hover else base_color
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw weapon icon
        if self.weapon_type == "sword":
            pygame.draw.line(screen, WHITE,
                           (self.rect.centerx - 10, self.rect.centery - 10),
                           (self.rect.centerx + 10, self.rect.centery + 10), 2)
        else:
            pygame.draw.arc(screen, WHITE, 
                          (self.rect.centerx - 10, self.rect.centery - 10, 20, 20),
                          -math.pi/2, math.pi/2, 2)
        
        # Draw label
        label = f"P{self.player_num} {self.weapon_type.title()}"
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        screen.blit(text, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                button_click_sound.play()  # Play click sound
                return True
        return False

# Create weapon buttons for both screens
def create_weapon_buttons(y_position):
    buttons = [
        WeaponButton(WINDOW_WIDTH//4 - 50, y_position, 80, 40, "sword", 1),
        WeaponButton(WINDOW_WIDTH//4 + 50, y_position, 80, 40, "bow", 1),
        WeaponButton(3*WINDOW_WIDTH//4 - 50, y_position, 80, 40, "sword", 2),
        WeaponButton(3*WINDOW_WIDTH//4 + 50, y_position, 80, 40, "bow", 2)
    ]
    return buttons

# Create menu buttons with weapon options
menu_weapon_buttons = create_weapon_buttons(WINDOW_HEIGHT//2 - 50)
game_over_weapon_buttons = create_weapon_buttons(WINDOW_HEIGHT//2 - 50)

# Create background elements
clouds = [Cloud() for _ in range(5)]
mountains = [
    Mountain(100, 200),
    Mountain(300, 250),
    Mountain(500, 180),
    Mountain(700, 220)
]
benches = [
    Bench(100, 300, 150, 15),   # Left low bench
    Bench(300, 250, 200, 15),   # Middle bench
    Bench(600, 300, 150, 15),   # Right low bench
    Bench(200, 200, 150, 15),   # Left high bench
    Bench(500, 200, 150, 15),   # Right high bench
    Bench(350, 150, 100, 15),   # Top middle bench
]

def draw_background(screen, time):
    # Draw sky gradient
    sky_color_top = (135, 206, 235)  # Light blue
    sky_color_bottom = (255, 255, 255)  # White
    for y in range(WINDOW_HEIGHT):
        progress = y / WINDOW_HEIGHT
        color = [int(sky_color_top[i] + (sky_color_bottom[i] - sky_color_top[i]) * progress) for i in range(3)]
        pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
    
    # Draw sun
    sun_x = WINDOW_WIDTH // 2 + math.cos(time / 3000) * 100
    sun_y = 100 + math.sin(time / 3000) * 50
    pygame.draw.circle(screen, (255, 255, 0), (int(sun_x), int(sun_y)), 40)
    
    # Draw mountains
    mountain_color = (128, 128, 128)
    points = [(0, WINDOW_HEIGHT), (200, 200), (400, 300), (600, 150), (WINDOW_WIDTH, WINDOW_HEIGHT)]
    pygame.draw.polygon(screen, mountain_color, points)
    
    # Draw clouds
    for cloud in clouds:
        cloud.move()
        cloud.draw(screen)
    
    # Draw all benches
    for bench in benches:
        bench.draw(screen)
    
    # Draw ground
    ground_rect = pygame.Rect(0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20)
    pygame.draw.rect(screen, (40, 20, 0), ground_rect)  # Dark brown ground

def check_winner():
    if player1.health <= 0:
        return "Player 2 Wins!"
    elif player2.health <= 0:
        return "Player 1 Wins!"
    return None

def draw_game_over(screen, font, player1, player2):
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Draw winner text
    winner_text = check_winner()
    if winner_text:
        text = font.render(winner_text, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        screen.blit(text, text_rect)
    
    # Draw weapon selection
    selection_font = pygame.font.Font(None, 36)
    
    # Draw weapon buttons
    for button in game_over_weapon_buttons:
        is_selected = (button.player_num == 1 and button.weapon_type == game_options.p1_weapon) or \
                     (button.player_num == 2 and button.weapon_type == game_options.p2_weapon)
        button.draw(screen, selection_font, is_selected)
    
    # Draw play again and quit buttons lower
    play_again_btn = Button(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT - 100, 120, 40, "Play Again")
    quit_btn = Button(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 50, 80, 30, "Quit")
    
    play_again_btn.draw(screen)
    quit_btn.draw(screen)
    
    return play_again_btn, quit_btn

def draw_health_bars(screen, player1, player2):
    # Draw Player 1 health bar
    pygame.draw.rect(screen, RED, (50, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (50, 20, player1.health * 2, 20))
    
    # Draw Player 2 health bar
    pygame.draw.rect(screen, RED, (WINDOW_WIDTH - 250, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (WINDOW_WIDTH - 250, 20, player2.health * 2, 20))

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (100, 100, 100)  # Default gray
        self.hover_color = (150, 150, 150)  # Lighter gray for hover
        self.text_color = WHITE
        self.font = pygame.font.Font(None, 32)
        self.is_hovered = False

    def draw(self, screen):
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # White border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                button_click_sound.play()  # Play click sound
                return True
        return False

# Create menu buttons
start_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 100, 200, 40, "Start Game")
quit_button = Button(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 50, 80, 30, "Quit")

# Create players
def reset_game():
    global player1, player2
    # Reset player positions
    player1 = Player(200, WINDOW_HEIGHT - 60, BLUE, True, {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'jump': pygame.K_SPACE,
        'attack': 1  # Left click
    }, 1)
    player2 = Player(600, WINDOW_HEIGHT - 60, RED, False, {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'attack': 3  # Right click
    }, 2)
    
    # Set weapons based on options
    player1.weapon = game_options.p1_weapon
    player2.weapon = game_options.p2_weapon

# Game font
font = pygame.font.Font(None, 74)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

clock = pygame.time.Clock()

# Initialize game state
game_state = MENU  # Start in menu state

# Game loop
running = True
start_time = pygame.time.get_ticks()
while running:
    current_time = pygame.time.get_ticks()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == MENU:
            # Handle weapon selection
            for button in menu_weapon_buttons:
                if button.handle_event(event):
                    if button.player_num == 1:
                        game_options.p1_weapon = button.weapon_type
                    else:
                        game_options.p2_weapon = button.weapon_type
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check start button
                if start_button.rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    game_state = PLAYING
                    reset_game()
                
                # Check quit button
                if quit_button.rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    running = False
        
        elif game_state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click for Player 1
                    print("Player 1 attack attempt")
                    player1.attack(player2)
                elif event.button == 3:  # Right click for Player 2
                    print("Player 2 attack attempt")
                    player2.attack(player1)
        
        elif game_state == GAME_OVER:
            # Handle weapon selection
            for button in game_over_weapon_buttons:
                if button.handle_event(event):
                    if button.player_num == 1:
                        game_options.p1_weapon = button.weapon_type
                    else:
                        game_options.p2_weapon = button.weapon_type
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check play again button
                play_again_rect = pygame.Rect(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT - 100, 120, 40)
                if play_again_rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    game_state = PLAYING
                    reset_game()
                
                # Check quit button
                quit_rect = pygame.Rect(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 50, 80, 30)
                if quit_rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    running = False
    
    # Update game state
    if game_state == PLAYING:
        # Reset platform status at start of frame
        player1.on_platform = False
        player2.on_platform = False
        
        # Move players
        player1.move()
        player2.move()
        
        # Check bench collisions for both players
        for bench in benches:
            bench.check_collision(player1)
            bench.check_collision(player2)
        
        # Update attacks
        player1.update_attack(player2)
        player2.update_attack(player1)
        
        # Check for game over
        if player1.health <= 0 or player2.health <= 0:
            game_state = GAME_OVER
    
    # Draw everything
    screen.fill((135, 206, 235))  # Sky blue background
    
    if game_state == MENU:
        draw_background(screen, current_time - start_time)
        start_button.draw(screen)
        quit_button.draw(screen)
        for button in menu_weapon_buttons:
            is_selected = (button.player_num == 1 and button.weapon_type == game_options.p1_weapon) or \
                         (button.player_num == 2 and button.weapon_type == game_options.p2_weapon)
            button.draw(screen, font, is_selected)
    elif game_state == PLAYING:
        draw_background(screen, current_time - start_time)
        player1.draw(screen)
        player2.draw(screen)
        draw_health_bars(screen, player1, player2)
    elif game_state == GAME_OVER:
        draw_background(screen, current_time - start_time)
        player1.draw(screen)
        player2.draw(screen)
        draw_health_bars(screen, player1, player2)
        draw_game_over(screen, font, player1, player2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
