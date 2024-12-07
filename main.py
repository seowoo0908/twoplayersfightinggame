import pygame
import sys
import math
import random
import os

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
        self.height = 60
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
        # Draw stick figure
        head_radius = 15
        body_length = 30
        limb_length = 20
        
        # Draw head (circle)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y - 25)), head_radius)
        
        if self.facing_right:
            # Right-facing face
            # Draw detailed eyes
            # Eye whites
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x - 5), int(self.y - 28)), 4)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x + 5), int(self.y - 28)), 4)
            
            # Eye outline
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x - 5), int(self.y - 28)), 4, 1)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x + 5), int(self.y - 28)), 4, 1)
            
            # Pupils (looking right)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x - 3), int(self.y - 28)), 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x + 7), int(self.y - 28)), 2)
        else:
            # Left-facing face
            # Draw detailed eyes
            # Eye whites
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x - 5), int(self.y - 28)), 4)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(self.x + 5), int(self.y - 28)), 4)
            
            # Eye outline
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x - 5), int(self.y - 28)), 4, 1)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x + 5), int(self.y - 28)), 4, 1)
            
            # Pupils (looking left)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x - 7), int(self.y - 28)), 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(self.x + 3), int(self.y - 28)), 2)
        
        # Draw mouth based on health
        if self.health > 50:
            # Happy mouth (using small lines for more definition)
            mouth_width = 12
            # Center line
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x - mouth_width//2, self.y - 22),
                           (self.x + mouth_width//2, self.y - 22), 2)
            # Left corner up
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x - mouth_width//2, self.y - 22),
                           (self.x - mouth_width//2 + 2, self.y - 24), 2)
            # Right corner up
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x + mouth_width//2, self.y - 22),
                           (self.x + mouth_width//2 - 2, self.y - 24), 2)
        else:
            # Sad mouth (using small lines for more definition)
            mouth_width = 10
            # Center line
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x - mouth_width//2, self.y - 22),
                           (self.x + mouth_width//2, self.y - 22), 2)
            # Left corner down
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x - mouth_width//2, self.y - 22),
                           (self.x - mouth_width//2 + 2, self.y - 20), 2)
            # Right corner down
            pygame.draw.line(screen, (0, 0, 0),
                           (self.x + mouth_width//2, self.y - 22),
                           (self.x + mouth_width//2 - 2, self.y - 20), 2)
        
        # Draw body (vertical line)
        pygame.draw.line(screen, self.color, 
                        (self.x, self.y - 10),  # Top of body (below head)
                        (self.x, self.y + 20), 2)  # Bottom of body
        
        # Draw arms
        arm_angle = math.pi/6 if self.attacking else math.pi/4  # Raise arms when attacking
        
        if self.facing_right:
            # Right arm (weapon arm) - adjust based on attack
            if self.attacking:
                # Arm follows weapon swing
                swing_progress = self.attack_frame / 15.0  # 0 to 1
                arm_angle = -math.pi/3 + swing_progress * math.pi  # Swing motion
            pygame.draw.line(screen, self.color,
                           (self.x, self.y - 5),  # Shoulder
                           (self.x + limb_length * math.cos(-arm_angle), 
                            self.y - 5 + limb_length * math.sin(-arm_angle)), 2)
            # Left arm
            pygame.draw.line(screen, self.color,
                           (self.x, self.y - 5),  # Shoulder
                           (self.x - limb_length * math.cos(arm_angle), 
                            self.y - 5 + limb_length * math.sin(arm_angle)), 2)
        else:
            # Left arm (weapon arm) - adjust based on attack
            if self.attacking:
                swing_progress = self.attack_frame / 15.0
                arm_angle = -math.pi/3 + swing_progress * math.pi
            pygame.draw.line(screen, self.color,
                           (self.x, self.y - 5),  # Shoulder
                           (self.x - limb_length * math.cos(-arm_angle), 
                            self.y - 5 + limb_length * math.sin(-arm_angle)), 2)
            # Right arm
            pygame.draw.line(screen, self.color,
                           (self.x, self.y - 5),  # Shoulder
                           (self.x + limb_length * math.cos(arm_angle), 
                            self.y - 5 + limb_length * math.sin(arm_angle)), 2)
        
        # Draw legs
        leg_angle = math.pi/6
        # Right leg
        pygame.draw.line(screen, self.color,
                        (self.x, self.y + 20),  # Hip
                        (self.x + limb_length * math.cos(-leg_angle), 
                         self.y + 20 + limb_length * math.sin(leg_angle)), 2)
        # Left leg
        pygame.draw.line(screen, self.color,
                        (self.x, self.y + 20),  # Hip
                        (self.x - limb_length * math.cos(-leg_angle), 
                         self.y + 20 + limb_length * math.sin(leg_angle)), 2)
        
        # Draw weapon
        diamond_color = (85, 205, 252)  # Light blue
        diamond_dark = (65, 185, 232)   # Darker blue for edges
        diamond_shine = (220, 240, 255)  # White-blue for shine

        if self.weapon == "sword":
            # Diamond blade
            blade_length = 60
            # Main blade shape
            blade_points = [
                (self.x + (blade_length if self.facing_right else -blade_length), self.y),  # Tip
                (self.x + (blade_length-10 if self.facing_right else -blade_length+10), self.y - 12),  # Top edge
                (self.x + (15 if self.facing_right else -15), self.y),  # Base
                (self.x + (blade_length-10 if self.facing_right else -blade_length+10), self.y + 12),  # Bottom edge
            ]
            # Fill with diamond color
            pygame.draw.polygon(screen, diamond_color, blade_points)
            # Draw crystal edges
            pygame.draw.lines(screen, diamond_dark, True, blade_points, 2)

            # Diamond pattern on blade
            pattern_x = self.x + ((blade_length-30) if self.facing_right else -(blade_length-30))
            diamond_points = [
                (pattern_x - (8 if self.facing_right else -8), self.y),  # Left
                (pattern_x, self.y - 8),  # Top
                (pattern_x + (8 if self.facing_right else -8), self.y),  # Right
                (pattern_x, self.y + 8),  # Bottom
            ]
            pygame.draw.polygon(screen, (255, 215, 0), diamond_points)  # Gold diamond
            pygame.draw.lines(screen, (139, 69, 19), True, diamond_points, 1)  # Dark outline
            
            # Curved golden handle
            handle_x = self.x + (15 if self.facing_right else -15)
            # Main curved part
            if self.facing_right:
                pygame.draw.arc(screen, (218, 165, 32),  # Gold color
                              [handle_x - 20, self.y - 15, 30, 30],
                              -math.pi/4, math.pi/4, 4)
            else:
                pygame.draw.arc(screen, (218, 165, 32),  # Gold color
                              [handle_x - 10, self.y - 15, 30, 30],
                              3*math.pi/4, 5*math.pi/4, 4)
            
            # Gold guard
            guard_x = self.x + (15 if self.facing_right else -15)
            pygame.draw.rect(screen, (218, 165, 32),  # Gold
                           (guard_x - 12, self.y - 6, 24, 12))
            pygame.draw.circle(screen, (255, 215, 0),  # Bright gold
                             (guard_x, self.y), 4)
            
            # Diamond shine effects
            for i in range(3):
                shine_x = self.x + ((25 + i*10) if self.facing_right else -(25 + i*10))
                pygame.draw.line(screen, diamond_shine,
                               (shine_x, self.y - 3 - i),
                               (shine_x + (8 if self.facing_right else -8), self.y - 5 - i), 2)

        elif self.weapon == "bow":
            bow_height = 60
            # Normal wooden bow
            if self.facing_right:
                pygame.draw.arc(screen, (139, 69, 19),  # Brown
                              (self.x + 5, self.y - bow_height//2, 30, bow_height),
                              -math.pi/2, math.pi/2, 5)
                # Bow decorations
                for i in range(3):
                    y_offset = -bow_height//2 + i*(bow_height//3)
                    pygame.draw.circle(screen, (101, 67, 33),
                                    (self.x + 20, self.y + y_offset), 3)
            else:
                pygame.draw.arc(screen, (139, 69, 19),
                              (self.x - 35, self.y - bow_height//2, 30, bow_height),
                              math.pi/2, 3*math.pi/2, 5)
                # Bow decorations
                for i in range(3):
                    y_offset = -bow_height//2 + i*(bow_height//3)
                    pygame.draw.circle(screen, (101, 67, 33),
                                    (self.x - 20, self.y + y_offset), 3)
            
            # Normal bowstring
            string_x = self.x + (30 if self.facing_right else -30)
            pygame.draw.line(screen, (255, 255, 240),  # White
                           (string_x, self.y - bow_height//2),
                           (string_x, self.y + bow_height//2), 2)
            
            # Diamond arrow when attacking
            if self.attacking:
                arrow_length = 40
                arrow_x = self.x + (35 if self.facing_right else -35)
                
                # Wooden arrow shaft
                pygame.draw.line(screen, (139, 69, 19),  # Brown
                               (arrow_x, self.y),
                               (arrow_x + (arrow_length if self.facing_right else -arrow_length), self.y), 3)
                
                # Diamond arrowhead
                head_size = 12
                head_points = [
                    (arrow_x + (arrow_length if self.facing_right else -arrow_length), self.y),
                    (arrow_x + ((arrow_length+head_size) if self.facing_right else -(arrow_length+head_size)), self.y - head_size//2),
                    (arrow_x + ((arrow_length+head_size+5) if self.facing_right else -(arrow_length+head_size+5)), self.y),
                    (arrow_x + ((arrow_length+head_size) if self.facing_right else -(arrow_length+head_size)), self.y + head_size//2),
                ]
                pygame.draw.polygon(screen, diamond_color, head_points)
                pygame.draw.lines(screen, diamond_dark, True, head_points, 2)
                
                # Red feathers
                feather_colors = [(255, 0, 0), (255, 100, 100)]
                for i, color in enumerate(feather_colors):
                    feather_x = arrow_x + (10 if self.facing_right else -10) + (i * 5 * (1 if self.facing_right else -1))
                    pygame.draw.polygon(screen, color, [
                        (feather_x, self.y),
                        (feather_x - (5 if self.facing_right else -5), self.y - 6),
                        (feather_x - (10 if self.facing_right else -10), self.y)
                    ])
                    pygame.draw.polygon(screen, color, [
                        (feather_x, self.y),
                        (feather_x - (5 if self.facing_right else -5), self.y + 6),
                        (feather_x - (10 if self.facing_right else -10), self.y)
                    ])

        elif self.weapon == "spear":
            # Wooden shaft
            shaft_length = 100
            shaft_start = self.x + (10 if self.facing_right else -10)
            shaft_end = self.x + (shaft_length if self.facing_right else -shaft_length)
            
            # Brown gradient shaft
            for i in range(4):
                y_offset = -2 + i
                pygame.draw.line(screen, (139 - i*10, 69 - i*5, 19 - i*2),  # Gradient brown
                               (shaft_start, self.y + y_offset),
                               (shaft_end, self.y + y_offset), 2)
            
            # Diamond spearhead
            head_length = 30
            head_width = 16
            head_points = [
                (shaft_end, self.y),  # Base
                (shaft_end + (head_length if self.facing_right else -head_length), self.y),  # Tip
                (shaft_end + (head_length*0.7 if self.facing_right else -head_length*0.7), self.y - head_width//2),  # Top wing
                (shaft_end + (head_length*0.7 if self.facing_right else -head_length*0.7), self.y + head_width//2),  # Bottom wing
            ]
            pygame.draw.polygon(screen, diamond_color, head_points)
            pygame.draw.lines(screen, diamond_dark, True, head_points, 2)
            
            # Binding wraps
            for i in range(5):
                bind_x = shaft_start + (10 * i if self.facing_right else -10 * i)
                bind_height = 6 if i % 2 == 0 else 4
                pygame.draw.line(screen, (101, 67, 33),  # Dark brown
                               (bind_x, self.y - bind_height//2),
                               (bind_x, self.y + bind_height//2), 3)
            
            # Gold rings
            ring_positions = [0.2, 0.4, 0.6]
            for pos in ring_positions:
                ring_x = shaft_start + (shaft_length * pos if self.facing_right else -shaft_length * pos)
                pygame.draw.circle(screen, (218, 165, 32),  # Gold
                                (ring_x, self.y), 4)
            
            # Diamond shine effects
            for i in range(3):
                shine_x = shaft_end + ((head_length*0.3 + i*5) if self.facing_right else -(head_length*0.3 + i*5))
                pygame.draw.line(screen, diamond_shine,
                               (shine_x, self.y - 2 - i),
                               (shine_x + (5 if self.facing_right else -5), self.y - 2 - i), 2)

        # Draw health bar
        health_width = 50 * (self.health / 100)
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 25, self.y - 40, 50, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 25, self.y - 40, health_width, 5))
        
        # Draw arrow if shooting
        if self.arrow:
            pygame.draw.line(screen, (139, 69, 19),
                           (self.arrow[0] - 10, self.arrow[1]),
                           (self.arrow[0] + 10, self.arrow[1]), 2)

    def attack(self, other_player):
        if not self.attacking and self.attack_cooldown <= 0:
            print(f"Player {self.player_num} starting attack with {self.weapon}")
            self.attacking = True
            self.attack_frame = 0
            
            # Play swing sound immediately for both weapons
            sword_swing_sound.play()
            
            # For bow, create arrow
            if self.weapon == "bow":
                self.arrow = [self.x + (20 if self.facing_right else -20), self.y]
            
            # For sword, check hit immediately
            elif self.weapon == "sword":
                # Calculate distance between players
                distance = abs(self.x - other_player.x)
                vertical_distance = abs(self.y - other_player.y)
                
                # Check both horizontal and vertical distance
                if distance < 100 and vertical_distance < 60:  # Increased range and added vertical check
                    # Check if player is facing the right direction
                    if (self.facing_right and self.x < other_player.x) or (not self.facing_right and self.x > other_player.x):
                        print(f"Player {self.player_num} sword hit!")
                        self.hit_player(other_player)
                        sword_hit_sound.play()
            
            # For spear, check hit immediately
            elif self.weapon == "spear":
                # Calculate distance between players
                distance = abs(self.x - other_player.x)
                vertical_distance = abs(self.y - other_player.y)
                
                # Check both horizontal and vertical distance
                if distance < 120 and vertical_distance < 20:  
                    # Check if player is facing the right direction
                    if (self.facing_right and self.x < other_player.x) or (not self.facing_right and self.x > other_player.x):
                        print(f"Player {self.player_num} spear hit!")
                        self.hit_player(other_player)
                        sword_hit_sound.play()
            
            self.attack_cooldown = 15  # Shorter cooldown
    
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
                arrow_speed = 15
                self.arrow[0] += arrow_speed * (1 if self.facing_right else -1)
                
                # Check arrow hit
                if (abs(self.arrow[0] - other_player.x) < 30 and 
                    abs(self.arrow[1] - other_player.y) < 30):
                    print(f"Player {self.player_num} arrow hit!")
                    self.hit_player(other_player)
                    sword_hit_sound.play()
                    self.arrow = None
                
                # Remove arrow if off screen
                elif self.arrow[0] < 0 or self.arrow[0] > WINDOW_WIDTH:
                    self.arrow = None
            
            # Reset attack after animation
            if self.attack_frame >= 15:  # Shorter attack animation
                self.attacking = False
                self.arrow = None
    
    def hit_player(self, other_player):
        # Calculate damage
        if self.weapon == "sword":
            damage = 8  # Reduced from 15
        elif self.weapon == "bow":
            damage = 5  # Reduced from 10
        elif self.weapon == "spear":
            damage = 11  # Very slightly decreased from 12 to 11
        
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
        self.p1_weapon = "sword"  # "sword" or "bow" or "spear"
        self.p2_weapon = "sword"  # "sword" or "bow" or "spear"

# Create global options
game_options = GameOptions()

class WeaponButton:
    def __init__(self, x, y, width, height, weapon_type, player_num):
        self.rect = pygame.Rect(x, y, width, height)
        self.weapon_type = weapon_type
        self.player_num = player_num
        self.hover = False
        # Load weapon images with full path
        image_path = os.path.join(os.path.dirname(__file__), "images", f"{weapon_type}.png")
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (50, 50))  # Made images bigger
        except:
            print(f"Could not load image: {image_path}")
            self.image = None

    def draw(self, screen, font, is_selected):
        # Colors
        if is_selected:
            color = (0, 150, 0) if self.weapon_type == "sword" else (0, 0, 150) if self.weapon_type == "bow" else (150, 0, 0)
        else:
            base_color = (0, 100, 0) if self.weapon_type == "sword" else (0, 0, 100) if self.weapon_type == "bow" else (100, 0, 0)
            color = (min(base_color[0] + 30, 255), 
                    min(base_color[1] + 30, 255), 
                    min(base_color[2] + 30, 255)) if self.hover else base_color
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw weapons
        if self.weapon_type == "sword":
            # Main blade shape
            pygame.draw.polygon(screen, (192, 192, 192), [  # Silver blade
                (self.rect.centerx - 8, self.rect.centery - 20),  # Tip left
                (self.rect.centerx + 2, self.rect.centery - 25),  # Tip point
                (self.rect.centerx + 12, self.rect.centery - 20),  # Tip right
                (self.rect.centerx + 8, self.rect.centery + 10),  # Base right
                (self.rect.centerx - 4, self.rect.centery + 10),  # Base left
            ])

            # Curved golden handle
            # Main curved part
            pygame.draw.arc(screen, (218, 165, 32),  # Gold color
                          [self.rect.centerx - 15, self.rect.centery - 5, 30, 30],
                          -math.pi/4, math.pi/4, 4)
            
            # Guard
            pygame.draw.rect(screen, (218, 165, 32),  # Gold
                           (self.rect.centerx - 15, self.rect.centery + 8,
                            30, 5))
        
        elif self.weapon_type == "bow":
            # Bow curve (thicker at grip)
            pygame.draw.arc(screen, (139, 69, 19),  # Brown color
                          (self.rect.centerx - 20, self.rect.centery - 25,
                           30, 50), -math.pi/2, math.pi/2, 5)
            # Grip wrap
            pygame.draw.rect(screen, (101, 67, 33),  # Dark brown
                           (self.rect.centerx - 15, self.rect.centery - 5,
                            8, 10))
            # Bowstring
            pygame.draw.line(screen, (255, 255, 240),  # Off-white
                           (self.rect.centerx + 2, self.rect.centery - 25),
                           (self.rect.centerx + 2, self.rect.centery + 25), 2)
            # Arrow shaft
            pygame.draw.line(screen, (139, 69, 19),  # Brown
                           (self.rect.centerx - 10, self.rect.centery),
                           (self.rect.centerx + 15, self.rect.centery), 3)
            # Arrow head
            pygame.draw.polygon(screen, (169, 169, 169), [  # Silver
                (self.rect.centerx + 15, self.rect.centery),
                (self.rect.centerx + 25, self.rect.centery - 4),
                (self.rect.centerx + 25, self.rect.centery + 4),
            ])
            # Fletching
            pygame.draw.polygon(screen, (255, 0, 0), [  # Red feathers
                (self.rect.centerx - 5, self.rect.centery),
                (self.rect.centerx - 10, self.rect.centery - 4),
                (self.rect.centerx - 15, self.rect.centery),
            ])
            
        elif self.weapon_type == "spear":
            # Main shaft
            pygame.draw.line(screen, (139, 69, 19),  # Brown
                           (self.rect.centerx - 25, self.rect.centery),
                           (self.rect.centerx + 20, self.rect.centery), 4)
            
            # Spearhead
            pygame.draw.polygon(screen, (192, 192, 192), [  # Silver
                (self.rect.centerx + 20, self.rect.centery),      # Base
                (self.rect.centerx + 40, self.rect.centery),      # Tip
                (self.rect.centerx + 25, self.rect.centery - 8),  # Top wing
                (self.rect.centerx + 25, self.rect.centery + 8),  # Bottom wing
            ])
            # Head details
            pygame.draw.line(screen, (169, 169, 169),  # Darker silver
                           (self.rect.centerx + 20, self.rect.centery), (self.rect.centerx + 40, self.rect.centery), 2)  # Center line
            pygame.draw.line(screen, (169, 169, 169),
                           (self.rect.centerx + 25, self.rect.centery - 8), (self.rect.centerx + 40, self.rect.centery), 2)  # Top edge
            pygame.draw.line(screen, (169, 169, 169),
                           (self.rect.centerx + 25, self.rect.centery + 8), (self.rect.centerx + 40, self.rect.centery), 2)  # Bottom edge
            
            # Multiple binding wraps
            for i in range(5):  # More bindings
                bind_x = self.rect.centerx - 15 + (i * 8)
                bind_height = 6 if i % 2 == 0 else 4  # Alternating sizes
                pygame.draw.line(screen, (101, 67, 33),  # Dark brown
                               (bind_x, self.rect.centery - bind_height//2),
                               (bind_x, self.rect.centery + bind_height//2), 3)
            
            # Multiple decorative rings
            ring_positions = [0.2, 0.4, 0.6]  # Positions along shaft
            for pos in ring_positions:
                ring_x = self.rect.centerx - 25 + (pos * 45)
                pygame.draw.circle(screen, (218, 165, 32),  # Gold
                                (ring_x, self.rect.centery), 4)
            
            # Multiple shine effects on blade
            for i in range(3):
                shine_x = self.rect.centerx + 25 + (i*5)
                pygame.draw.line(screen, (255, 255, 255),  # White shine
                               (shine_x, self.rect.centery - 2 - i),
                               (shine_x + 5, self.rect.centery - 2 - i), 2)
        
        # Draw label below button
        button_font = pygame.font.Font(None, 24)
        label = f"{self.weapon_type.title()}"
        text = button_font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 15))
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
        WeaponButton(WINDOW_WIDTH//4 + 150, y_position, 80, 40, "spear", 1),
        WeaponButton(2*WINDOW_WIDTH//3 - 50, y_position, 80, 40, "sword", 2),  # Moved left from 3*WINDOW_WIDTH//4
        WeaponButton(2*WINDOW_WIDTH//3 + 50, y_position, 80, 40, "bow", 2),    # Moved left accordingly
        WeaponButton(2*WINDOW_WIDTH//3 + 150, y_position, 80, 40, "spear", 2)  # Moved left accordingly
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
    selection_font = pygame.font.Font(None, 32)
    
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
        'jump': pygame.K_SPACE
    }, 1)
    
    player2 = Player(600, WINDOW_HEIGHT - 60, RED, False, {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP
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
            if event.type == pygame.KEYDOWN:
                # Player 1 jump with SPACE
                if event.key == pygame.K_SPACE:
                    player1.velocity_y = player1.jump_power
                    player1.is_jumping = True
                    player1.on_platform = False
                    player1.current_platform = None
                    jump_sound.play()  # Play jump sound
                # Player 2 jump with UP
                if event.key == pygame.K_UP:
                    player2.velocity_y = player2.jump_power
                    player2.is_jumping = True
                    player2.on_platform = False
                    player2.current_platform = None
                    jump_sound.play()  # Play jump sound

            # Get current keyboard state for attacks
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                player1.attack(player2)
            elif keys[pygame.K_SLASH]:
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
        title_font = pygame.font.Font(None, 48)  
        player_font = pygame.font.Font(None, 32)  
        title_text = title_font.render("Choose Your Weapons", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        p1_text = player_font.render("Player 1", True, WHITE)
        p2_text = player_font.render("Player 2", True, WHITE)
        screen.blit(p1_text, (WINDOW_WIDTH//4 - 30, 100))  
        screen.blit(p2_text, (2*WINDOW_WIDTH//3 - 30, 100))  
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
