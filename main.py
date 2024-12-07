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
    bow_sound = pygame.mixer.Sound("sounds/bow_sound.wav")
    spear_thrust_sound = pygame.mixer.Sound("sounds/spear_thrust.wav")
    arrow_hit_sound = pygame.mixer.Sound("sounds/arrow_hit.wav")
except:
    # Create default sounds if files don't exist
    sword_swing_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    sword_hit_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    jump_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    button_click_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    roblox_oof_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    bow_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    spear_thrust_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))
    arrow_hit_sound = pygame.mixer.Sound(bytes(bytearray([0]*44100)))

# Set sound volumes
sword_swing_sound.set_volume(0.3)
sword_hit_sound.set_volume(0.4)
jump_sound.set_volume(0.2)
button_click_sound.set_volume(0.3)
roblox_oof_sound.set_volume(0.7)  # Make the oof loud and clear
bow_sound.set_volume(0.3)
spear_thrust_sound.set_volume(0.3)
arrow_hit_sound.set_volume(0.3)  # Make the oof loud and clear

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
        self.attack_frame = 0  # Add this for attack animation
        self.attack_duration = 15  # Total frames for attack animation
        self.attack_cooldown = 0  # Add cooldown counter
        self.weapon = "sword"  # Default weapon
        self.arrow = None  # For bow attacks
        self.speed = 5  # Movement speed
        self.jump_power = -15  # Jump strength
        self.on_platform = False  # Track if player is on a platform
        self.current_platform = None  # Track which platform player is on
        self.last_hit_time = 0  # Add this for hit sound cooldown
        self.player_num = player_num  # Add this back

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
            # Define colors
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel
            diamond_shine = (220, 240, 255)  # White-blue shine
            wood_color = (90, 75, 60)        # Light wood
            gold_color = (255, 215, 0)       # Gold for diamonds
            brown_dark = (139, 69, 19)       # Dark brown

            # Diamond blade
            blade_length = 60
            # Main blade shape - ultra thin version
            blade_points = [
                (self.x + (blade_length if self.facing_right else -blade_length), self.y),  # Tip
                (self.x + ((blade_length-10) if self.facing_right else -(blade_length-10)), self.y - 2),  # Top edge
                (self.x + (15 if self.facing_right else -15), self.y),  # Base
                (self.x + ((blade_length-10) if self.facing_right else -(blade_length-10)), self.y + 2),  # Bottom edge
            ]
            # Fill with steel color
            pygame.draw.polygon(screen, steel_color, blade_points)
            # Draw steel edges
            pygame.draw.lines(screen, steel_dark, True, blade_points, 2)

            # Diamond pattern on blade
            for i in range(3):
                if self.facing_right:
                    diamond_x = self.x + 25 + (i * 15)
                else:
                    diamond_x = self.x - 25 - (i * 15)
                diamond_points = [
                    (diamond_x, self.y - 2),  # Top
                    (diamond_x + (4 if self.facing_right else -4), self.y),  # Right
                    (diamond_x, self.y + 2),  # Bottom
                    (diamond_x - (4 if self.facing_right else -4), self.y),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Gold diamond at base
            diamond_size = 6
            base_x = self.x + (15 if self.facing_right else -15)
            diamond_points = [
                (base_x, self.y - diamond_size),  # Top
                (base_x + (diamond_size if self.facing_right else -diamond_size), self.y),  # Right
                (base_x, self.y + diamond_size),  # Bottom
                (base_x - (diamond_size if self.facing_right else -diamond_size), self.y),  # Left
            ]
            pygame.draw.polygon(screen, gold_color, diamond_points)
            pygame.draw.lines(screen, brown_dark, True, diamond_points, 1)

            # Curved wooden handle - ultra thin version
            handle_x = self.x + (15 if self.facing_right else -15)
            # Main curved part
            if self.facing_right:
                pygame.draw.arc(screen, wood_color,
                              [handle_x - 25, self.y - 20, 40, 40],
                              -math.pi/4, math.pi/4, 2)
            else:
                pygame.draw.arc(screen, wood_color,
                              [handle_x - 15, self.y - 20, 40, 40],
                              3*math.pi/4, 5*math.pi/4, 2)
            
            # Wood guard - thinner version
            guard_x = self.x + (15 if self.facing_right else -15)
            pygame.draw.rect(screen, wood_color,
                           (guard_x - 8, self.y - 3, 16, 6))
            
            # Diamond shine effects
            for i in range(3):
                if self.facing_right:
                    shine_x = self.x + 25 + (i*10)
                else:
                    shine_x = self.x - 25 - (i*10)
                pygame.draw.line(screen, diamond_shine,
                               (shine_x, self.y - 3 - i),
                               (shine_x + (8 if self.facing_right else -8), self.y - 5 - i), 2)

        elif self.weapon == "bow":
            # Colors
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            string_color = (220, 220, 220)   # Light gray
            diamond_shine = (220, 240, 255)  # White-blue shine

            bow_height = 60
            # Main bow curve - thicker at grip
            if self.facing_right:
                pygame.draw.arc(screen, wood_color,
                              [self.x - 10, self.y - bow_height//2, 40, bow_height],
                              -math.pi/3, math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [self.x - 12, self.y - bow_height//2 - 2, 44, bow_height + 4],
                              -math.pi/3, math.pi/3, 2)
            else:
                pygame.draw.arc(screen, wood_color,
                              [self.x - 30, self.y - bow_height//2, 40, bow_height],
                              2*math.pi/3, 4*math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [self.x - 32, self.y - bow_height//2 - 2, 44, bow_height + 4],
                              2*math.pi/3, 4*math.pi/3, 2)

            # Gold decorations at bow tips
            tip_radius = 4
            # Top tip
            top_x = self.x + (10 if self.facing_right else -10)
            pygame.draw.circle(screen, gold_color, (top_x, self.y - bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, self.y - bow_height//2), tip_radius, 1)
            # Bottom tip
            pygame.draw.circle(screen, gold_color, (top_x, self.y + bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, self.y + bow_height//2), tip_radius, 1)

            # Diamond decorations on bow
            for i in range(2):
                diamond_y = self.y - 15 + i * 30
                diamond_x = self.x + (5 if self.facing_right else -5)
                diamond_points = [
                    (diamond_x, diamond_y - 4),  # Top
                    (diamond_x + (4 if self.facing_right else -4), diamond_y),  # Right
                    (diamond_x, diamond_y + 4),  # Bottom
                    (diamond_x - (4 if self.facing_right else -4), diamond_y),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, wood_dark, True, diamond_points, 1)

            # Bowstring
            string_start = (top_x, self.y - bow_height//2)
            string_end = (top_x, self.y + bow_height//2)
            string_mid = (self.x + (0 if self.facing_right else -0), self.y)
            
            # Draw curved bowstring
            points = [string_start, string_mid, string_end]
            pygame.draw.lines(screen, string_color, False, points, 2)

            # Arrow design (always visible)
            # Colors for arrow
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel
            wood_color = (90, 75, 60)        # Light wood
            gold_color = (255, 215, 0)       # Gold
            feather_color = (220, 20, 60)    # Crimson red

            arrow_length = 40
            arrow_x = self.x + (35 if self.facing_right else -35)
            
            # Wooden arrow shaft with gold rings
            pygame.draw.line(screen, wood_color,
                           (arrow_x, self.y),
                           (arrow_x + (arrow_length if self.facing_right else -arrow_length), self.y), 3)
            
            # Gold decorative rings
            for i in range(2):
                ring_x = arrow_x + ((10 + i*15) if self.facing_right else -(10 + i*15))
                pygame.draw.circle(screen, gold_color, (ring_x, self.y), 2)
                pygame.draw.circle(screen, wood_dark, (ring_x, self.y), 2, 1)

            # Steel arrowhead
            head_length = 15
            head_width = 8
            head_x = arrow_x + (arrow_length if self.facing_right else -arrow_length)
            head_points = [
                (head_x, self.y),  # Base
                (head_x + (head_length if self.facing_right else -head_length), self.y),  # Tip
                (head_x + (head_length*0.7 if self.facing_right else -head_length*0.7), self.y - head_width//2),  # Top barb
                (head_x + (head_length*0.7 if self.facing_right else -head_length*0.7), self.y + head_width//2),  # Bottom barb
            ]
            pygame.draw.polygon(screen, steel_color, head_points)
            pygame.draw.lines(screen, steel_dark, True, head_points, 1)

            # Diamond decoration on arrowhead
            diamond_x = head_x + (head_length*0.4 if self.facing_right else -head_length*0.4)
            diamond_points = [
                (diamond_x, self.y - 2),  # Top
                (diamond_x + (2 if self.facing_right else -2), self.y),  # Right
                (diamond_x, self.y + 2),  # Bottom
                (diamond_x - (2 if self.facing_right else -2), self.y),  # Left
            ]
            pygame.draw.polygon(screen, diamond_shine, diamond_points)
            pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Feather fletching
            feather_start = arrow_x - 5
            for i in range(2):
                feather_x = feather_start - (i * 8 if self.facing_right else -i * 8)
                feather_points = [
                    (feather_x, self.y),  # Base
                    (feather_x - (8 if self.facing_right else -8), self.y - 6),  # Top tip
                    (feather_x - (12 if self.facing_right else -12), self.y),  # Back
                ]
                pygame.draw.polygon(screen, feather_color, feather_points)
                # Bottom feather
                bottom_points = [
                    (feather_x, self.y),  # Base
                    (feather_x - (8 if self.facing_right else -8), self.y + 6),  # Bottom tip
                    (feather_x - (12 if self.facing_right else -12), self.y),  # Back
                ]
                pygame.draw.polygon(screen, feather_color, bottom_points)

        elif self.weapon == "spear":
            # Colors
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            diamond_shine = (220, 240, 255)  # White-blue shine

            shaft_length = 80
            head_length = 25
            shaft_end = self.x + (shaft_length if self.facing_right else -shaft_length)
            
            # Wooden shaft with decorative rings
            pygame.draw.line(screen, wood_color,
                           (self.x, self.y),
                           (shaft_end, self.y), 3)
            
            # Gold rings along shaft
            for i in range(3):
                ring_x = self.x + ((20 + i*25) if self.facing_right else -(20 + i*25))
                pygame.draw.circle(screen, gold_color, (ring_x, self.y), 3)
                pygame.draw.circle(screen, wood_dark, (ring_x, self.y), 3, 1)

            # Spearhead - steel blade
            head_points = [
                (shaft_end, self.y),  # Base
                (shaft_end + (head_length if self.facing_right else -head_length), self.y),  # Tip
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.y - 8),  # Top barb
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.y + 8),  # Bottom barb
            ]
            pygame.draw.polygon(screen, steel_color, head_points)
            pygame.draw.lines(screen, steel_dark, True, head_points, 2)

            # Diamond decorations on blade
            for i in range(2):
                diamond_x = shaft_end + ((head_length*0.4 + i*8) if self.facing_right else -(head_length*0.4 + i*8))
                diamond_points = [
                    (diamond_x, self.y - 3),  # Top
                    (diamond_x + (3 if self.facing_right else -3), self.y),  # Right
                    (diamond_x, self.y + 3),  # Bottom
                    (diamond_x - (3 if self.facing_right else -3), self.y),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Gold decoration at spear base
            base_x = self.x + (5 if self.facing_right else -5)
            pygame.draw.circle(screen, gold_color, (base_x, self.y), 4)
            pygame.draw.circle(screen, wood_dark, (base_x, self.y), 4, 1)
        
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
            
            if self.weapon == "bow":
                # Start the swing animation without releasing arrow
                bow_sound.play()
            elif self.weapon == "sword":
                sword_swing_sound.play()
            elif self.weapon == "spear":
                spear_thrust_sound.play()

    def update_attack(self, other_player):
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.attacking:
            self.attack_frame += 1
            
            # Calculate attack progress
            progress = self.attack_frame / self.attack_duration
            
            # Release arrow at the peak of swing (halfway through animation)
            if self.weapon == "bow" and progress >= 0.5 and self.arrow is None:
                # Set arrow position
                arrow_x = self.x + (self.width if self.facing_right else 0)
                self.arrow = [arrow_x, self.y + self.height // 2]
            
            # Move existing arrow
            if self.weapon == "bow" and self.arrow:
                arrow_speed = 15
                if self.facing_right:
                    self.arrow[0] += arrow_speed
                else:
                    self.arrow[0] -= arrow_speed
                
                # Check arrow collision
                arrow_rect = pygame.Rect(self.arrow[0] - 5, self.arrow[1] - 2, 10, 4)
                player_rect = pygame.Rect(other_player.x, other_player.y, 
                                       other_player.width, other_player.height)
                
                if arrow_rect.colliderect(player_rect):
                    self.hit_player(other_player)
                    self.arrow = None
                    arrow_hit_sound.play()
                elif (self.arrow[0] < 0 or self.arrow[0] > 800 or 
                      self.arrow[1] < 0 or self.arrow[1] > 600):
                    self.arrow = None
            
            # Check hits at peak of swing
            if progress >= 0.5:
                # Calculate distance between players
                distance = abs(self.x - other_player.x)
                vertical_distance = abs(self.y - other_player.y)
                
                if self.weapon == "sword":
                    # Sword hit check
                    if distance < 100 and vertical_distance < 60:
                        if (self.facing_right and self.x < other_player.x) or (not self.facing_right and self.x > other_player.x):
                            print(f"Player {self.player_num} sword hit!")
                            self.hit_player(other_player)
                            sword_hit_sound.play()
                elif self.weapon == "spear":
                    # Spear hit check
                    if distance < 120 and vertical_distance < 20:
                        if (self.facing_right and self.x < other_player.x) or (not self.facing_right and self.x > other_player.x):
                            print(f"Player {self.player_num} spear hit!")
                            self.hit_player(other_player)
                            sword_hit_sound.play()
            
            # Reset attack after animation
            if self.attack_frame >= self.attack_duration:
                self.attacking = False
                self.attack_frame = 0
                # Set cooldown based on weapon
                if self.weapon == "bow":
                    self.attack_cooldown = 20
                elif self.weapon == "sword":
                    self.attack_cooldown = 25
                elif self.weapon == "spear":
                    self.attack_cooldown = 30

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
        self.facing_right = True  # Add this line to set default direction
        # Load weapon images with full path
        image_path = os.path.join(os.path.dirname(__file__), "images", f"{weapon_type}.png")
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (50, 50))  # Made images bigger
        except:
            print(f"Could not load image: {image_path}")
            self.image = None

    def draw(self, screen, font, is_selected):
        # Define colors once at the start
        steel_color = (176, 196, 222)    # Light steel blue
        steel_dark = (119, 136, 153)     # Dark steel
        diamond_shine = (220, 240, 255)  # White-blue shine
        wood_color = (90, 75, 60)        # Light wood
        gold_color = (255, 215, 0)       # Gold for diamonds
        brown_dark = (139, 69, 19)       # Dark brown

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
            # Diamond blade
            blade_length = 60
            # Main blade shape - ultra thin version
            blade_points = [
                (self.rect.centerx + blade_length, self.rect.centery),  # Tip
                (self.rect.centerx + (blade_length-10), self.rect.centery - 2),  # Top edge
                (self.rect.centerx + 15, self.rect.centery),  # Base
                (self.rect.centerx + (blade_length-10), self.rect.centery + 2),  # Bottom edge
            ]
            # Fill with steel color
            pygame.draw.polygon(screen, steel_color, blade_points)
            # Draw steel edges
            pygame.draw.lines(screen, steel_dark, True, blade_points, 2)

            # Diamond pattern on blade
            for i in range(3):
                diamond_x = self.rect.centerx + 25 + (i * 15)
                diamond_points = [
                    (diamond_x, self.rect.centery - 2),  # Top
                    (diamond_x + 4, self.rect.centery),  # Right
                    (diamond_x, self.rect.centery + 2),  # Bottom
                    (diamond_x - 4, self.rect.centery),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Gold diamond at base
            diamond_size = 6
            diamond_points = [
                (self.rect.centerx + 15, self.rect.centery - diamond_size),  # Top
                (self.rect.centerx + 15 + diamond_size, self.rect.centery),  # Right
                (self.rect.centerx + 15, self.rect.centery + diamond_size),  # Bottom
                (self.rect.centerx + 15 - diamond_size, self.rect.centery),  # Left
            ]
            pygame.draw.polygon(screen, gold_color, diamond_points)
            pygame.draw.lines(screen, brown_dark, True, diamond_points, 1)

            # Curved wooden handle - ultra thin version
            handle_x = self.rect.centerx + 15
            pygame.draw.arc(screen, wood_color,
                          [handle_x - 25, self.rect.centery - 20, 40, 40],
                          -math.pi/4, math.pi/4, 2)
            
            # Wood guard - thinner version
            guard_x = self.rect.centerx + 15
            pygame.draw.rect(screen, wood_color,
                           (guard_x - 8, self.rect.centery - 3, 16, 6))
            
            # Diamond shine effects on blade
            for i in range(3):
                shine_x = self.rect.centerx + 25 + (i*10)
                pygame.draw.line(screen, diamond_shine,
                               (shine_x, self.rect.centery - 3 - i),
                               (shine_x + 8, self.rect.centery - 5 - i), 2)

        elif self.weapon_type == "bow":
            # Colors
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            string_color = (220, 220, 220)   # Light gray
            diamond_shine = (220, 240, 255)  # White-blue shine

            bow_height = 60
            # Main bow curve - thicker at grip
            if self.facing_right:
                pygame.draw.arc(screen, wood_color,
                              [self.rect.centerx - 10, self.rect.centery - bow_height//2, 40, bow_height],
                              -math.pi/3, math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [self.rect.centerx - 12, self.rect.centery - bow_height//2 - 2, 44, bow_height + 4],
                              -math.pi/3, math.pi/3, 2)
            else:
                pygame.draw.arc(screen, wood_color,
                              [self.rect.centerx - 30, self.rect.centery - bow_height//2, 40, bow_height],
                              2*math.pi/3, 4*math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [self.rect.centerx - 32, self.rect.centery - bow_height//2 - 2, 44, bow_height + 4],
                              2*math.pi/3, 4*math.pi/3, 2)

            # Gold decorations at bow tips
            tip_radius = 4
            # Top tip
            top_x = self.rect.centerx + (10 if self.facing_right else -10)
            pygame.draw.circle(screen, gold_color, (top_x, self.rect.centery - bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, self.rect.centery - bow_height//2), tip_radius, 1)
            # Bottom tip
            pygame.draw.circle(screen, gold_color, (top_x, self.rect.centery + bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, self.rect.centery + bow_height//2), tip_radius, 1)

            # Diamond decorations on bow
            for i in range(2):
                diamond_y = self.rect.centery - 15 + i * 30
                diamond_x = self.rect.centerx + (5 if self.facing_right else -5)
                diamond_points = [
                    (diamond_x, diamond_y - 4),  # Top
                    (diamond_x + (4 if self.facing_right else -4), diamond_y),  # Right
                    (diamond_x, diamond_y + 4),  # Bottom
                    (diamond_x - (4 if self.facing_right else -4), diamond_y),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, wood_dark, True, diamond_points, 1)

            # Bowstring
            string_start = (top_x, self.rect.centery - bow_height//2)
            string_end = (top_x, self.rect.centery + bow_height//2)
            string_mid = (self.rect.centerx + (0 if self.facing_right else -0), self.rect.centery)
            
            # Draw curved bowstring
            points = [string_start, string_mid, string_end]
            pygame.draw.lines(screen, string_color, False, points, 2)

            # Arrow design
            arrow_length = 30
            arrow_x = self.rect.centerx - bow_height//4
            
            # Wooden arrow shaft with gold rings
            pygame.draw.line(screen, wood_color,
                           (arrow_x, self.rect.centery),
                           (arrow_x + arrow_length, self.rect.centery), 3)
            
            # Gold decorative rings
            for i in range(2):
                ring_x = arrow_x + (10 + i*10)
                pygame.draw.circle(screen, gold_color, (ring_x, self.rect.centery), 2)
                pygame.draw.circle(screen, wood_dark, (ring_x, self.rect.centery), 2, 1)

            # Steel arrowhead
            head_length = 12
            head_width = 6
            head_x = arrow_x + arrow_length
            head_points = [
                (head_x, self.rect.centery),  # Base
                (head_x + head_length, self.rect.centery),  # Tip
                (head_x + head_length*0.7, self.rect.centery - head_width//2),  # Top barb
                (head_x + head_length*0.7, self.rect.centery + head_width//2),  # Bottom barb
            ]
            pygame.draw.polygon(screen, steel_color, head_points)
            pygame.draw.lines(screen, steel_dark, True, head_points, 1)

            # Diamond decoration on arrowhead
            diamond_x = head_x + head_length*0.4
            diamond_points = [
                (diamond_x, self.rect.centery - 2),  # Top
                (diamond_x + 2, self.rect.centery),  # Right
                (diamond_x, self.rect.centery + 2),  # Bottom
                (diamond_x - 2, self.rect.centery),  # Left
            ]
            pygame.draw.polygon(screen, diamond_shine, diamond_points)
            pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Feather fletching
            feather_start = arrow_x - 5
            for i in range(2):
                feather_x = feather_start - i * 8
                feather_points = [
                    (feather_x, self.rect.centery),  # Base
                    (feather_x - 8, self.rect.centery - 6),  # Top tip
                    (feather_x - 12, self.rect.centery),  # Back
                ]
                pygame.draw.polygon(screen, (220, 20, 60), feather_points)
                # Bottom feather
                bottom_points = [
                    (feather_x, self.rect.centery),  # Base
                    (feather_x - 8, self.rect.centery + 6),  # Bottom tip
                    (feather_x - 12, self.rect.centery),  # Back
                ]
                pygame.draw.polygon(screen, (220, 20, 60), bottom_points)

        elif self.weapon_type == "spear":
            # Colors
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            diamond_shine = (220, 240, 255)  # White-blue shine

            shaft_length = 80
            head_length = 25
            shaft_end = self.rect.centerx + (shaft_length if self.facing_right else -shaft_length)
            
            # Wooden shaft with decorative rings
            pygame.draw.line(screen, wood_color,
                           (self.rect.centerx, self.rect.centery),
                           (shaft_end, self.rect.centery), 3)
            
            # Gold rings along shaft
            for i in range(3):
                ring_x = self.rect.centerx + ((20 + i*25) if self.facing_right else -(20 + i*25))
                pygame.draw.circle(screen, gold_color, (ring_x, self.rect.centery), 3)
                pygame.draw.circle(screen, wood_dark, (ring_x, self.rect.centery), 3, 1)

            # Spearhead - steel blade
            head_points = [
                (shaft_end, self.rect.centery),  # Base
                (shaft_end + (head_length if self.facing_right else -head_length), self.rect.centery),  # Tip
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.rect.centery - 8),  # Top barb
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.rect.centery + 8),  # Bottom barb
            ]
            pygame.draw.polygon(screen, steel_color, head_points)
            pygame.draw.lines(screen, steel_dark, True, head_points, 2)

            # Diamond decorations on blade
            for i in range(2):
                diamond_x = shaft_end + ((head_length*0.4 + i*8) if self.facing_right else -(head_length*0.4 + i*8))
                diamond_points = [
                    (diamond_x, self.rect.centery - 3),  # Top
                    (diamond_x + (3 if self.facing_right else -3), self.rect.centery),  # Right
                    (diamond_x, self.rect.centery + 3),  # Bottom
                    (diamond_x - (3 if self.facing_right else -3), self.rect.centery),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, steel_dark, True, diamond_points, 1)

            # Gold decoration at spear base
            base_x = self.rect.centerx + (5 if self.facing_right else -5)
            pygame.draw.circle(screen, gold_color, (base_x, self.rect.centery), 4)
            pygame.draw.circle(screen, wood_dark, (base_x, self.rect.centery), 4, 1)

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
