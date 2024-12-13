import pygame
import sys
import math
import random
import os

# Initialize Pygame and create window
try:
    pygame.init()
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Seowoo's Epic Battle Game!")
except pygame.error:
    print("Error: Could not initialize pygame. Make sure it's installed correctly.")
    sys.exit(1)

# Create a simple surface for weapons if images are not available
def create_weapon_surface(color):
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0, 0, 32, 32))
    return surface

# Try to load images, use colored rectangles if images don't exist
try:
    sword_img = pygame.image.load("images/sword.png")
except:
    sword_img = create_weapon_surface((192, 192, 192))  # Silver color for sword
    
try:
    bow_img = pygame.image.load("images/bow.png")
except:
    bow_img = create_weapon_surface((139, 69, 19))  # Brown color for bow
    
try:
    spear_img = pygame.image.load("images/spear.png")
except:
    spear_img = create_weapon_surface((218, 165, 32))  # Golden color for spear
    
try:
    shield_img = pygame.image.load("images/shield.png")
except:
    shield_img = create_weapon_surface((128, 128, 128))  # Gray color for shield

# Load sound effects
try:
    sword_swing_sound = pygame.mixer.Sound("sounds/sword_swing.wav")
    sword_hit_sound = pygame.mixer.Sound("sounds/sword_hit.wav")
    bow_hit_sound = pygame.mixer.Sound("sounds/bow_hit.wav")
    spear_hit_sound = pygame.mixer.Sound("sounds/spear_hit.wav")
    jump_sound = pygame.mixer.Sound("sounds/jump.wav")
    button_click_sound = pygame.mixer.Sound("sounds/button_click.wav")
    hurt_sound = pygame.mixer.Sound("sounds/oof.wav")  # Using oof.wav for hurt sound
    
    # Set sound volumes
    sword_swing_sound.set_volume(0.3)
    sword_hit_sound.set_volume(0.3)
    bow_hit_sound.set_volume(0.3)
    spear_hit_sound.set_volume(0.3)
    jump_sound.set_volume(0.3)
    button_click_sound.set_volume(0.3)
    hurt_sound.set_volume(0.5)  # Made hurt sound a bit louder
except Exception as e:
    print(f"Could not load some sound files: {e}")
    # Create default sounds if files don't exist
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    sword_swing_sound = DummySound()
    sword_hit_sound = DummySound()
    bow_hit_sound = DummySound()
    spear_hit_sound = DummySound()
    jump_sound = DummySound()
    button_click_sound = DummySound()
    hurt_sound = DummySound()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Sky colors for gradient
SKY_TOP = (135, 206, 235)      # Light blue
SKY_BOTTOM = (200, 230, 255)   # Very light blue

# Constants
GRAVITY = 0.8

# Cloud class
class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.uniform(0.8, 1.2)
        
    def draw(self, window):
        # Draw a fluffy cloud using multiple circles
        cloud_color = (255, 255, 255)  # White
        center_x = self.x
        center_y = self.y
        
        # Main cloud body
        pygame.draw.circle(window, cloud_color, (int(center_x), int(center_y)), int(30 * self.size))
        pygame.draw.circle(window, cloud_color, (int(center_x - 20 * self.size), int(center_y)), int(25 * self.size))
        pygame.draw.circle(window, cloud_color, (int(center_x + 20 * self.size), int(center_y)), int(25 * self.size))
        
        # Top puffs
        pygame.draw.circle(window, cloud_color, (int(center_x - 10 * self.size), int(center_y - 15 * self.size)), int(20 * self.size))
        pygame.draw.circle(window, cloud_color, (int(center_x + 10 * self.size), int(center_y - 15 * self.size)), int(20 * self.size))
    
    def move(self):
        self.x += self.speed
        if self.x > WINDOW_WIDTH + 100:
            self.x = -100

# Create some clouds
clouds = [
    Cloud(random.randint(0, WINDOW_WIDTH), random.randint(50, 200)) 
    for _ in range(5)
]

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(2, 4)
        self.wing_angle = 0
        self.flap_speed = random.uniform(0.2, 0.3)
        self.size = random.uniform(0.8, 1.2)
        # Random bird colors
        self.colors = random.choice([
            ((255, 0, 0), (200, 0, 0)),      # Red bird
            ((0, 100, 255), (0, 50, 200)),   # Blue bird
            ((255, 200, 0), (200, 150, 0)),  # Yellow bird
            ((0, 200, 0), (0, 150, 0)),      # Green bird
            ((255, 165, 0), (200, 130, 0))   # Orange bird
        ])
        
    def move(self):
        self.x += self.speed
        self.wing_angle = math.sin(pygame.time.get_ticks() * self.flap_speed) * 30
        if self.x > WINDOW_WIDTH + 50:
            self.x = -50
            self.y = random.randint(50, 200)
    
    def draw(self, window):
        main_color, dark_color = self.colors
        
        # Bird body (oval shape)
        pygame.draw.ellipse(window, main_color, 
                          (self.x - 10 * self.size, self.y - 5 * self.size,
                           20 * self.size, 10 * self.size))
        
        # Bird head
        pygame.draw.circle(window, main_color, 
                         (int(self.x + 8 * self.size), int(self.y - 2 * self.size)), 
                         int(6 * self.size))
        
        # Beak
        beak_points = [
            (self.x + 12 * self.size, self.y - 2 * self.size),
            (self.x + 18 * self.size, self.y - 1 * self.size),
            (self.x + 12 * self.size, self.y)
        ]
        pygame.draw.polygon(window, (255, 200, 0), beak_points)
        
        # Eye
        pygame.draw.circle(window, (0, 0, 0), 
                         (int(self.x + 10 * self.size), int(self.y - 3 * self.size)), 
                         int(2 * self.size))
        
        # Tail feathers
        tail_points = [
            (self.x - 10 * self.size, self.y),
            (self.x - 20 * self.size, self.y - 5 * self.size),
            (self.x - 15 * self.size, self.y),
            (self.x - 20 * self.size, self.y + 5 * self.size)
        ]
        pygame.draw.polygon(window, dark_color, tail_points)
        
        # Wings
        wing_height = 15 * self.size * math.sin(math.radians(self.wing_angle))
        left_wing = [
            (self.x - 5 * self.size, self.y),
            (self.x - 15 * self.size, self.y - wing_height),
            (self.x + 5 * self.size, self.y)
        ]
        pygame.draw.polygon(window, dark_color, left_wing)

class Airplane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.size = random.uniform(3.5, 4.0)
        self.trail_points = []
        self.window_color = (220, 220, 220)
        # Add lights
        self.light_color = (255, 0, 0)  # Red navigation light
        self.light_blink = 0
        
    def move(self):
        self.x += self.speed
        # Blink lights
        self.light_blink = (self.light_blink + 1) % 60  # Blink every 60 frames
        
        # Add trail point
        self.trail_points.append((self.x - 80 * self.size, self.y))
        if len(self.trail_points) > 30:
            self.trail_points.pop(0)
        if self.x > WINDOW_WIDTH + 200:
            self.x = -200
            self.y = random.randint(30, 170)
            self.trail_points = []
            self.size = random.uniform(3.2, 4.0)
    
    def draw(self, window):
        # Draw trail
        for i, point in enumerate(self.trail_points):
            alpha = i / len(self.trail_points)
            color = (255, 255, 255, int(alpha * 255))
            pygame.draw.circle(window, color, (int(point[0]), int(point[1])), 2)
        
        # Main body (fuselage) - metallic silver color
        pygame.draw.rect(window, (192, 192, 192), 
                        (self.x - 40 * self.size, self.y - 10 * self.size, 
                         80 * self.size, 20 * self.size))
        
        # Nose cone - darker silver
        nose_points = [
            (self.x + 40 * self.size, self.y),
            (self.x + 50 * self.size, self.y - 5 * self.size),
            (self.x + 50 * self.size, self.y + 5 * self.size),
        ]
        pygame.draw.polygon(window, (128, 128, 128), nose_points)
        
        # Main wings - blue tint
        pygame.draw.polygon(window, (100, 149, 237), [
            (self.x - 20 * self.size, self.y),
            (self.x - 10 * self.size, self.y - 30 * self.size),
            (self.x + 20 * self.size, self.y - 30 * self.size),
            (self.x + 30 * self.size, self.y)
        ])
        
        # Tail wing - blue tint
        pygame.draw.polygon(window, (100, 149, 237), [
            (self.x - 35 * self.size, self.y - 5 * self.size),
            (self.x - 40 * self.size, self.y - 25 * self.size),
            (self.x - 30 * self.size, self.y - 25 * self.size),
            (self.x - 25 * self.size, self.y - 5 * self.size)
        ])
        
        # Windows - blue tint
        window_spacing = 10 * self.size
        window_size = 4 * self.size
        for i in range(5):
            window_x = self.x - 20 * self.size + i * window_spacing
            pygame.draw.circle(window, (173, 216, 230), 
                             (int(window_x), int(self.y - 5 * self.size)), 
                             int(window_size))
        
        # Cockpit windows - blue tint
        pygame.draw.polygon(window, (173, 216, 230), [
            (self.x + 30 * self.size, self.y - 5 * self.size),
            (self.x + 40 * self.size, self.y - 5 * self.size),
            (self.x + 35 * self.size, self.y + 2 * self.size)
        ])
        
        # Navigation lights (blinking)
        if self.light_blink < 30:  # Blink every half second
            # Wing tip lights
            pygame.draw.circle(window, (255, 0, 0),  # Red light
                             (int(self.x - 10 * self.size), int(self.y - 25 * self.size)), 3)
            pygame.draw.circle(window, (0, 255, 0),  # Green light
                             (int(self.x + 20 * self.size), int(self.y - 25 * self.size)), 3)
            # Tail light
            pygame.draw.circle(window, (255, 255, 255),  # White light
                             (int(self.x - 40 * self.size), int(self.y - 25 * self.size)), 3)

# Create birds and airplanes
birds = [Bird(random.randint(0, WINDOW_WIDTH), random.randint(50, 200)) 
         for _ in range(5)]
airplanes = [
    Airplane(-200 - i * 400, random.randint(50, 150))  # Reduced spacing between planes
    for i in range(4)  # Increased to 4 planes
]

def draw_sky(window):
    # Draw sky gradient
    for y in range(WINDOW_HEIGHT):
        factor = y / WINDOW_HEIGHT
        color = (
            int(SKY_TOP[0] * (1 - factor) + SKY_BOTTOM[0] * factor),
            int(SKY_TOP[1] * (1 - factor) + SKY_BOTTOM[1] * factor),
            int(SKY_TOP[2] * (1 - factor) + SKY_BOTTOM[2] * factor)
        )
        pygame.draw.line(window, color, (0, y), (WINDOW_WIDTH, y))
    
    # Draw clouds
    for cloud in clouds:
        cloud.draw(window)
        cloud.move()
    
    # Draw birds
    for bird in birds:
        bird.draw(window)
        bird.move()
    
    # Draw airplanes with much higher chance of appearing
    for airplane in airplanes:
        if airplane.x <= -200 and random.random() < 0.15:  # Increased chance to 15%
            airplane.x = -200
            airplane.y = random.randint(30, 170)  # Wider height range
            # Randomize size slightly each time
            airplane.size = random.uniform(3.2, 4.0)
        if airplane.x > -200:  # Only draw and move if airplane is active
            airplane.draw(window)
            airplane.move()

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
        
    def draw(self, window):
        # Draw mountain body
        pygame.draw.polygon(window, self.color, self.points)
        
        # Draw snow cap
        snow_points = [
            (self.points[0][0] + (self.points[1][0] - self.points[0][0]) * 0.3, 
             WINDOW_HEIGHT - self.height + self.snow_line),
            self.points[1],  # Peak
            (self.points[2][0] - (self.points[2][0] - self.points[1][0]) * 0.3, 
             WINDOW_HEIGHT - self.height + self.snow_line)
        ]
        pygame.draw.polygon(window, WHITE, snow_points)

# Bench class
class Bench:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (139, 69, 19)  # Brown color for wooden bench

    def draw(self, window):
        # Draw main bench seat
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))
        # Draw bench legs
        leg_width = 10
        leg_height = 20
        pygame.draw.rect(window, self.color, (self.x + 10, self.y + self.height, leg_width, leg_height))
        pygame.draw.rect(window, self.color, (self.x + self.width - 20, self.y + self.height, leg_width, leg_height))

    def check_collision(self, player):
        # Check if player's feet are near the platform
        player_feet = player.y + player.height
        player_center = player.x
        
        # Check if player is within horizontal bounds of bench
        if self.x <= player_center <= self.x + self.width:
            # Check if player is at the right height to land
            if self.y - 5 <= player_feet <= self.y + 5:
                if player.dy >= 0:  # Only if falling or standing
                    player.y = self.y - player.height
                    player.dy = 0
                    player.is_jumping = False
                    player.on_platform = True
                    player.current_platform = self
                    return True
            # Check if player hits bottom of platform when jumping
            elif player.dy < 0 and player_feet < self.y + self.height:
                if abs(player_feet - (self.y + self.height)) < 10:
                    player.dy = 0
        
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
        self.dx = 0  # Horizontal velocity
        self.dy = 0  # Vertical velocity
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
        self.jump_power = -12  # Reduced jump power
        self.on_platform = False  # Track if player is on a platform
        self.current_platform = None  # Track which platform player is on
        self.last_hit_time = 0  # Add this for hit sound cooldown
        self.player_num = player_num  # Add this back
        self.rect = pygame.Rect(x, y, self.width, self.height)  # Add rect for collision detection
        self.on_ground = False
        self.can_jump = True  # New variable to control jumping
        self.jump_cooldown = 0  # New variable for jump cooldown
        self.max_jump_height = -12  # Maximum upward velocity
        self.knockback_dx = 0  # Knockback horizontal speed
        self.knockback_dy = 0  # Knockback vertical speed
        self.hurt_flash = 0  # Flash white when hurt
        self.combo_count = 0
        self.crit_chance = 0.2  # 20% base crit chance
        self.charge_time = 0
        self.max_charge = 60  # 1 second max charge
        self.spear_momentum = 0
        self.max_momentum = 5
        self.consecutive_spear_hits = 0
        self.name = f"P{player_num}"  # Default name
        self.defending = False  # New defense state
        self.defense_cooldown = 0  # Cooldown for defense
    
    def move(self):
        keys = pygame.key.get_pressed()
        
        # Handle defense
        if keys[self.controls['defend']]:
            self.defending = True
            self.dx = 0  # Can't move while defending
        else:
            self.defending = False
            
        if not self.defending:  # Only allow movement if not defending
            # Reset horizontal velocity
            self.dx = 0
            
            # Player 1 controls
            if self.player_num == 1:
                if keys[pygame.K_a]:
                    self.dx = -self.speed
                    self.facing_right = False
                if keys[pygame.K_d]:
                    self.dx = self.speed
                    self.facing_right = True
                if keys[pygame.K_w] and self.on_ground:
                    self.dy = -15  # Jump power
                    self.on_ground = False
            # Player 2 controls
            else:
                if keys[pygame.K_LEFT]:
                    self.dx = -self.speed
                    self.facing_right = False
                if keys[pygame.K_RIGHT]:
                    self.dx = self.speed
                    self.facing_right = True
                if keys[pygame.K_UP] and self.on_ground:
                    self.dy = -15  # Jump power
                    self.on_ground = False
        
        # Apply gravity
        if not self.on_ground:
            self.dy += 0.8  # Gravity
        
        # Apply movement
        self.x += self.dx + self.knockback_dx
        self.y += self.dy + self.knockback_dy
        
        # Reduce knockback
        self.knockback_dx *= 0.8
        self.knockback_dy *= 0.8
        
        # Keep in bounds
        if self.x < 0:
            self.x = 0
        elif self.x > WINDOW_WIDTH - self.width:
            self.x = WINDOW_WIDTH - self.width
            
        # Ground collision
        if self.y > WINDOW_HEIGHT - 20 - self.height:  # Ground is 20 pixels high
            self.y = WINDOW_HEIGHT - 20 - self.height
            self.dy = 0
            self.on_ground = True
    
    def update(self):
        # Apply stronger gravity
        if not self.on_ground:
            self.dy += 0.8  # Increased gravity
        self.y += self.dy
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Keep player in bounds
        if self.y > WINDOW_HEIGHT - 20 - self.height:
            self.y = WINDOW_HEIGHT - 20 - self.height
            self.dy = 0
            self.on_ground = True
        
        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.dy > 0:  # Falling
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    self.dy = 0
                    self.on_ground = True
                    break
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update hurt flash
        if self.hurt_flash > 0:
            self.hurt_flash -= 1
    
    def draw(self, screen):
        # Draw name above health bar
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.name, True, (0, 0, 0))
        name_rect = name_text.get_rect(centerx=self.x, bottom=self.y - 45)  # Position above health bar
        screen.blit(name_text, name_rect)
        
        # Draw body
        body_color = self.color
        if self.hurt_flash > 0:
            body_color = (255, 255, 255)  # Flash white when hurt
            self.hurt_flash -= 1

        # Draw stick figure
        head_radius = 15
        body_length = 30
        limb_length = 20

        # Calculate body lean during attack
        body_lean = 0
        if self.attacking:
            attack_progress = min(1.0, self.attack_frame / max(1, self.attack_duration))
            
            if self.facing_right:
                # Right arm follows weapon
                arm_angle = -math.pi/4 + (attack_progress * math.pi/2)  # Reduced swing
                pygame.draw.line(screen, body_color,
                               (self.x, self.y - 25),  # Shoulder
                               (self.x + limb_length * math.cos(arm_angle), 
                                self.y - 25 + limb_length * math.sin(arm_angle)), 2)
                # Left arm stays back
                pygame.draw.line(screen, body_color,
                               (self.x, self.y - 25),
                               (self.x - limb_length * 0.7, self.y - 25), 2)
            else:
                # Left arm follows weapon
                arm_angle = -math.pi/4 + (attack_progress * math.pi/2)
                pygame.draw.line(screen, body_color,
                               (self.x, self.y - 25),
                               (self.x - limb_length * math.cos(arm_angle), 
                                self.y - 25 + limb_length * math.sin(arm_angle)), 2)
                # Right arm stays back
                pygame.draw.line(screen, body_color,
                               (self.x, self.y - 25),
                               (self.x + limb_length * 0.7, self.y - 25), 2)
        else:
            # Normal arm positions
            arm_angle = math.pi/6
            pygame.draw.line(screen, body_color,
                           (self.x, self.y - 25),
                           (self.x + limb_length * math.cos(arm_angle), 
                            self.y - 25 + limb_length * math.sin(arm_angle)), 2)
            pygame.draw.line(screen, body_color,
                           (self.x, self.y - 25),
                           (self.x - limb_length * math.cos(arm_angle), 
                            self.y - 25 + limb_length * math.sin(arm_angle)), 2)

        # Draw head with lean
        head_x = int(self.x + body_lean/2)
        head_y = int(self.y - 25)
        pygame.draw.circle(screen, body_color, (head_x, head_y), head_radius)

        # Draw body (vertical line) with lean
        pygame.draw.line(screen, body_color, 
                        (head_x, head_y + 15),  # Top of body (below head)
                        (int(self.x - body_lean/2), self.y + 20), 2)  # Bottom of body

        # Draw face
        eye_color = (0, 0, 0)
        mouth_color = (0, 0, 0)
        eye_spacing = 6
        eye_y = head_y - 3

        # Eye positions based on facing direction
        if self.facing_right:
            left_eye_x = head_x - eye_spacing
            right_eye_x = head_x + eye_spacing
        else:
            left_eye_x = head_x + eye_spacing
            right_eye_x = head_x - eye_spacing

        # Draw expressions
        if self.hurt_flash > 0:
            # X eyes
            pygame.draw.line(screen, eye_color, (left_eye_x - 2, eye_y - 2), (left_eye_x + 2, eye_y + 2), 2)
            pygame.draw.line(screen, eye_color, (left_eye_x - 2, eye_y + 2), (left_eye_x + 2, eye_y - 2), 2)
            pygame.draw.line(screen, eye_color, (right_eye_x - 2, eye_y - 2), (right_eye_x + 2, eye_y + 2), 2)
            pygame.draw.line(screen, eye_color, (right_eye_x - 2, eye_y + 2), (right_eye_x + 2, eye_y - 2), 2)
            # Open mouth
            pygame.draw.ellipse(screen, mouth_color, (head_x - 4, head_y + 3, 8, 6))
        else:
            # Normal eyes
            pygame.draw.circle(screen, eye_color, (int(left_eye_x), int(eye_y)), 2)
            pygame.draw.circle(screen, eye_color, (int(right_eye_x), int(eye_y)), 2)
            # Smile or worried expression
            if self.health > 50:
                pygame.draw.arc(screen, mouth_color, 
                              (int(head_x - 5), int(head_y), 10, 8),
                              0, math.pi, 2)
            else:
                pygame.draw.arc(screen, mouth_color,
                              (int(head_x - 5), int(head_y + 3), 10, 8),
                              math.pi, 2*math.pi, 2)

        # Draw legs
        leg_angle = math.pi/6
        hip_x = int(self.x - body_lean/2)
        hip_y = self.y + 20
        
        # Right leg
        pygame.draw.line(screen, body_color,
                        (hip_x, hip_y),
                        (hip_x + limb_length * math.cos(leg_angle),
                         hip_y + limb_length * math.sin(leg_angle)), 2)
        # Left leg
        pygame.draw.line(screen, body_color,
                        (hip_x, hip_y),
                        (hip_x - limb_length * math.cos(leg_angle),
                         hip_y + limb_length * math.sin(leg_angle)), 2)

        # Calculate weapon hand position
        weapon_hand_x = head_x + (20 if self.facing_right else -20)
        weapon_hand_y = head_y + 25  # Moved hand lower (was 15)
        
        # Draw health bar
        health_width = 50 * (self.health / 100)
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 25, self.y - 40, 50, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 25, self.y - 40, health_width, 5))
        
        # Draw arrow if shooting
        if self.arrow:
            pygame.draw.line(screen, (139, 69, 19),
                           (self.arrow[0] - 10, self.arrow[1]),
                           (self.arrow[0] + 10, self.arrow[1]), 2)

        # Draw weapons
        if self.weapon == "sword":
            # Colors
            blade_color = (200, 200, 220)  # Light steel
            blade_edge = (150, 150, 170)   # Darker steel for edges
            gold_color = (218, 165, 32)    # Golden for decorations
            handle_color = (139, 69, 19)   # Dark brown for handle
            diamond_color = (85, 205, 252) # Light blue for diamonds
            diamond_edge = (65, 185, 232)  # Darker blue for diamond edges
            diamond_shine = (220, 240, 255) # White-blue for shine
            
            # Calculate angles
            if self.attacking:
                attack_progress = min(1.0, self.attack_frame / max(1, self.attack_duration))
                if attack_progress < 0.5:
                    base_angle = -45 + (attack_progress * 180)
                    wobble = math.sin(attack_progress * math.pi * 4) * 5  # Reduced wobble
                    swing_angle = base_angle + wobble
                else:
                    base_angle = -45 + (0.5 * 180)  # Fixed end position
                    swing_angle = base_angle
            else:
                swing_angle = 45

            # Convert angle to radians and adjust for facing direction
            angle_rad = math.radians(swing_angle if self.facing_right else -swing_angle)
            perp_angle = angle_rad + math.pi/2

            # Sword dimensions
            blade_length = 50
            blade_width = 6
            guard_width = 24
            guard_height = 8
            handle_length = 15

            # Draw trail effect during swing
            if self.attacking and attack_progress < 0.5:
                for i in range(5):
                    trail_progress = attack_progress - i * 0.05
                    if trail_progress > 0:
                        trail_angle = math.radians(-45 + trail_progress * 180 if self.facing_right else -(-45 + trail_progress * 180))
                        trail_x = weapon_hand_x + math.cos(trail_angle) * blade_length
                        trail_y = weapon_hand_y + math.sin(trail_angle) * blade_length
                        alpha = 100 - i * 20
                        trail_color = (192, 192, 192, alpha)
                        pygame.draw.line(screen, trail_color, (weapon_hand_x, weapon_hand_y), (trail_x, trail_y), 3)

            # Draw sword blade (sharper version)
            blade_points = [
                (weapon_hand_x + blade_length * math.cos(angle_rad), weapon_hand_y + blade_length * math.sin(angle_rad)),  # Tip
                (weapon_hand_x + (blade_length-10) * math.cos(angle_rad), weapon_hand_y + (blade_length-10) * math.sin(angle_rad)),  # Top edge
                (weapon_hand_x + 15 * math.cos(angle_rad), weapon_hand_y + 15 * math.sin(angle_rad)),  # Base
                (weapon_hand_x + (blade_length-10) * math.cos(angle_rad) + blade_width * math.cos(perp_angle), 
                 weapon_hand_y + (blade_length-10) * math.sin(angle_rad) + blade_width * math.sin(perp_angle))  # Bottom edge
            ]
            pygame.draw.polygon(screen, blade_color, blade_points)  # Light steel color
            
            # Add sharp edge highlight
            edge_points = [
                (weapon_hand_x + blade_length * math.cos(angle_rad), weapon_hand_y + blade_length * math.sin(angle_rad)),  # Tip
                (weapon_hand_x + (blade_length-5) * math.cos(angle_rad), weapon_hand_y + (blade_length-5) * math.sin(angle_rad)),  # Near tip
                (weapon_hand_x + 15 * math.cos(angle_rad), weapon_hand_y + 15 * math.sin(angle_rad))  # Base
            ]
            pygame.draw.lines(screen, (220, 220, 220), False, edge_points, 1)

            # Draw handle
            handle_end_x = weapon_hand_x - math.cos(angle_rad) * handle_length
            handle_end_y = weapon_hand_y - math.sin(angle_rad) * handle_length
            pygame.draw.line(screen, handle_color, 
                           (weapon_hand_x, weapon_hand_y), 
                           (handle_end_x, handle_end_y), 4)

            # Draw ornate cross guard
            for offset in [-guard_width/2, guard_width/2]:
                px = weapon_hand_x + math.cos(perp_angle) * offset
                py = weapon_hand_y + math.sin(perp_angle) * offset
                
                # Draw guard ends
                pygame.draw.circle(screen, gold_color, (int(px), int(py)), int(guard_height/2))
                pygame.draw.circle(screen, handle_color, (int(px), int(py)), int(guard_height/2), 1)
            
            # Draw pommel (decorated end of handle)
            pygame.draw.circle(screen, gold_color, (int(handle_end_x), int(handle_end_y)), 4)
            # Add diamond decoration to pommel
            pommel_diamond_size = 2
            pommel_diamond_points = []
            for i in range(4):
                point_angle = math.pi/2 + (i * math.pi/2)
                dx = handle_end_x + math.cos(point_angle) * pommel_diamond_size
                dy = handle_end_y + math.sin(point_angle) * pommel_diamond_size
                pommel_diamond_points.append((dx, dy))
            pygame.draw.polygon(screen, diamond_color, pommel_diamond_points)
            pygame.draw.polygon(screen, blade_edge, pommel_diamond_points, 1)

        elif self.weapon == "bow":
            # Colors
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            string_color = (220, 220, 220)   # Light gray
            diamond_shine = (220, 240, 255)  # White-blue shine
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel

            bow_height = 60
            # Calculate bow position based on attack frame
            if self.attacking:
                attack_progress = min(1.0, self.attack_frame / max(1, self.attack_duration))
                string_pull = math.sin(attack_progress * math.pi) * 20  # Maximum pull of 20 pixels
            else:
                string_pull = 0

            # Main bow curve
            if self.facing_right:
                pygame.draw.arc(screen, wood_color,
                              [weapon_hand_x - 10, weapon_hand_y - bow_height//2, 40, bow_height],
                              -math.pi/3, math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [weapon_hand_x - 12, weapon_hand_y - bow_height//2 - 2, 44, bow_height + 4],
                              -math.pi/3, math.pi/3, 2)
            else:
                pygame.draw.arc(screen, wood_color,
                              [weapon_hand_x - 30, weapon_hand_y - bow_height//2, 40, bow_height],
                              2*math.pi/3, 4*math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(screen, wood_dark,
                              [weapon_hand_x - 32, weapon_hand_y - bow_height//2 - 2, 44, bow_height + 4],
                              2*math.pi/3, 4*math.pi/3, 2)

            # Gold decorations at bow tips
            tip_radius = 4
            # Top tip
            top_x = weapon_hand_x + (10 if self.facing_right else -10)
            pygame.draw.circle(screen, gold_color, (top_x, weapon_hand_y - bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, weapon_hand_y - bow_height//2), tip_radius, 1)
            # Bottom tip
            pygame.draw.circle(screen, gold_color, (top_x, weapon_hand_y + bow_height//2), tip_radius)
            pygame.draw.circle(screen, wood_dark, (top_x, weapon_hand_y + bow_height//2), tip_radius, 1)

            # Diamond decorations on bow
            for i in range(2):
                diamond_y = weapon_hand_y - 15 + i * 30
                diamond_x = weapon_hand_x + (5 if self.facing_right else -5)
                diamond_points = [
                    (diamond_x, diamond_y - 4),  # Top
                    (diamond_x + (4 if self.facing_right else -4), diamond_y),  # Right
                    (diamond_x, diamond_y + 4),  # Bottom
                    (diamond_x - (4 if self.facing_right else -4), diamond_y),  # Left
                ]
                pygame.draw.polygon(screen, diamond_shine, diamond_points)
                pygame.draw.lines(screen, wood_dark, True, diamond_points, 1)

            # Bowstring
            string_start = (top_x, weapon_hand_y - bow_height//2)
            string_end = (top_x, weapon_hand_y + bow_height//2)
            string_mid = (weapon_hand_x + (-15 - string_pull if self.facing_right else 15 + string_pull), weapon_hand_y)
            
            # Draw curved bowstring
            points = [string_start, string_mid, string_end]
            pygame.draw.lines(screen, string_color, False, points, 2)

            # Only draw arrow when attacking
            if self.attacking:
                arrow_length = 30
                arrow_x = weapon_hand_x + (-20 - string_pull if self.facing_right else 20 + string_pull)
                arrow_dir = 1 if self.facing_right else -1
                
                # Wooden arrow shaft with gold rings
                pygame.draw.line(screen, wood_color,
                               (arrow_x, weapon_hand_y),
                               (arrow_x + arrow_length * arrow_dir, weapon_hand_y), 3)
                
                # Gold decorative rings
                for i in range(2):
                    ring_x = arrow_x + (10 + i*10) * arrow_dir
                    pygame.draw.circle(screen, gold_color, (ring_x, weapon_hand_y), 2)
                    pygame.draw.circle(screen, wood_dark, (ring_x, weapon_hand_y), 2, 1)

                # Steel arrowhead
                head_length = 12
                head_width = 6
                head_x = arrow_x + arrow_length * arrow_dir
                head_points = [
                    (head_x, weapon_hand_y),  # Base
                    (head_x + head_length * arrow_dir, weapon_hand_y),  # Tip
                    (head_x + head_length * 0.7 * arrow_dir, weapon_hand_y - head_width//2),  # Top barb
                    (head_x + head_length * 0.7 * arrow_dir, weapon_hand_y + head_width//2),  # Bottom barb
                ]
                pygame.draw.polygon(screen, steel_color, head_points)
                pygame.draw.lines(screen, steel_dark, True, head_points, 1)

                # Feathers at arrow base
                feather_length = 8
                feather_width = 3
                for offset in [-1, 1]:  # Top and bottom feathers
                    feather_points = [
                        (arrow_x, weapon_hand_y + offset * feather_width),
                        (arrow_x - feather_length * arrow_dir, weapon_hand_y),
                        (arrow_x, weapon_hand_y)
                    ]
                    pygame.draw.polygon(screen, WHITE, feather_points)
                    pygame.draw.lines(screen, (200, 200, 200), True, feather_points, 1)
        
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
            # Add diamond decoration to pommel
            pommel_diamond_size = 2
            pommel_diamond_points = []
            for i in range(4):
                point_angle = math.pi/2 + (i * math.pi/2)
                dx = base_x + math.cos(point_angle) * pommel_diamond_size
                dy = self.y + math.sin(point_angle) * pommel_diamond_size
                pommel_diamond_points.append((dx, dy))
            pygame.draw.polygon(screen, diamond_shine, pommel_diamond_points)
            pygame.draw.polygon(screen, steel_dark, pommel_diamond_points, 1)
        
        # Draw label below button
        button_font = pygame.font.Font(None, 24)
        label = f"{self.weapon.title()}"
        text = button_font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x, self.y + 40))
        screen.blit(text, text_rect)
        
        # Draw defense effect
        if self.defending:
            # Shield effect (protective aura)
            shield_color = (200, 200, 255, 100)  # Light blue, semi-transparent
            shield_radius = max(self.width, self.height) // 2
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            
            # Shield base (metallic circle)
            shield_size = 40
            shield_surface = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
            
            # Shield gradient (metallic effect)
            for i in range(shield_size // 2):
                alpha = 255 - i * 4
                color = (192, 192, 192, alpha)  # Silver color with fading alpha
                pygame.draw.circle(shield_surface, color, (shield_size // 2, shield_size // 2), shield_size // 2 - i)
            
            # Shield border
            pygame.draw.circle(shield_surface, (128, 128, 128), (shield_size // 2, shield_size // 2), shield_size // 2, 2)
            
            # Shield emblem (simple cross)
            emblem_color = (218, 165, 32)  # Golden color
            pygame.draw.line(shield_surface, emblem_color, 
                           (shield_size // 2, 5), 
                           (shield_size // 2, shield_size - 5), 3)
            pygame.draw.line(shield_surface, emblem_color, 
                           (5, shield_size // 2), 
                           (shield_size - 5, shield_size // 2), 3)
            
            # Draw the shield
            shield_x = self.x + (self.width if self.facing_right else -40)
            shield_y = self.y + 10
            screen.blit(shield_surface, (shield_x, shield_y))
            
    def attack(self, other_player):
        if not self.attacking and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = 0
            # Set weapon-specific properties
            if self.weapon == "sword":
                self.damage = 15
                self.attack_duration = 20
                self.attack_range = 50
                self.attack_cooldown = 30
                sword_swing_sound.play()
            elif self.weapon == "bow":
                self.damage = 5  # Halved base damage
                self.attack_duration = 25  # Slightly slower
                self.attack_range = 450  # Slightly reduced range
                self.attack_cooldown = 35  # Longer cooldown
                bow_hit_sound.play()
            elif self.weapon == "spear":
                self.damage = 12  # Reduced from 20 to 12
                self.attack_duration = 25
                self.attack_range = 120  # Good reach
                self.attack_cooldown = 35  # Slightly reduced from 40
                spear_hit_sound.play()

    def update_attack(self, other_player):
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.attacking:
            self.attack_frame += 1
            
            # Calculate distance and angle to target
            dx = other_player.x - self.x
            dy = other_player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if target is in front of the attacker
            is_target_in_front = (dx > 0 and self.facing_right) or (dx < 0 and not self.facing_right)
            
            # Weapon-specific attack logic
            if self.weapon == "bow":
                if self.attack_frame < self.attack_duration:
                    self.charge_time += 0.5  # Reduced charge rate by half
                else:
                    # Only hit if charged and facing the right way
                    if self.charge_time > 0 and is_target_in_front:
                        if abs(dy) < 50:  # Vertical aim check
                            self.hit_player(other_player)
                            # Calculate angle to target
                            angle = math.atan2(dy, dx)
                            # Create arrow
                            game.arrows.append(Arrow(self.x, self.y - 25, other_player.x, other_player.y - 25))
                            # Create arrow trail
                            for _ in range(5):
                                angle_var = random.uniform(-0.2, 0.2)
                                speed = random.uniform(5, 8)
                                dx = math.cos(angle + angle_var) * speed
                                dy = math.sin(angle + angle_var) * speed
                                particles.append(Particle(self.x, self.y - 25, dx, dy, (139, 69, 19)))
                    self.charge_time = 0
                    self.attacking = False
                    self.attack_frame = 0
                    self.attack_cooldown = 35  # Match the longer cooldown
                    self.attack_duration = 25  # Match the slower duration
                    self.attack_range = 450  # Set attack range
                    self.damage = 5  # Match the reduced base damage
            elif self.weapon == "spear":
                # Spear only hits at its max reach and in front
                if self.attack_frame == self.attack_duration // 2:
                    spear_range = (90, 140)  # Spear's effective range
                    if is_target_in_front and distance >= spear_range[0] and distance <= spear_range[1]:
                        other_player.health -= self.damage
                        spear_hit_sound.play()
                        # Create hit effect
                        for _ in range(10):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(2, 5)
                            dx = math.cos(angle) * speed
                            dy = math.sin(angle) * speed
                            particles.append(Particle(other_player.x, other_player.y, dx, dy, (200, 200, 200)))
                if self.attack_frame >= self.attack_duration:
                    self.attacking = False
                    self.attack_frame = 0
            else:  # Sword
                # Sword only hits in close range and in front
                if self.attack_frame == self.attack_duration // 2:
                    if is_target_in_front and distance < 80:  # Shorter sword range
                        if abs(dy) < 40:  # Height check for sword
                            self.hit_player(other_player)
                
                if self.attack_frame >= self.attack_duration:
                    self.attacking = False
                    self.attack_frame = 0
                    self.attack_cooldown = 30

    def hit_player(self, other_player):
        if not other_player.defending:  # Only deal damage if the other player is not defending
            # Calculate damage based on weapon
            if self.weapon == "sword":
                damage = 10
            elif self.weapon == "bow":
                damage = 15
            elif self.weapon == "spear":
                damage = 12 + min(self.spear_momentum * 2, 8)  # Extra damage from momentum
            
            # Apply damage
            other_player.health -= damage
            other_player.hurt_flash = 10  # Flash white when hit
            
            # Play hurt sound with cooldown
            current_time = pygame.time.get_ticks()
            if current_time - other_player.last_hit_time > 500:  # 500ms cooldown
                hurt_sound.play()
                other_player.last_hit_time = current_time
        else:
            # If player is defending, they take reduced damage
            if self.weapon == "sword":
                damage = 3
            elif self.weapon == "bow":
                damage = 5
            elif self.weapon == "spear":
                damage = 4 + min(self.spear_momentum * 0.5, 3)
            
            other_player.health -= damage
            other_player.hurt_flash = 5  # Shorter flash when blocked

class Particle:
    def __init__(self, x, y, dx, dy, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.lifetime = 30  # Particle exists for 30 frames
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, window):
        alpha = int((self.lifetime / 30) * 255)  # Fade out as lifetime decreases
        particle_color = (*self.color, alpha)
        pygame.draw.circle(window, particle_color, (int(self.x), int(self.y)), 3)

particles = []

class Game:
    def __init__(self):
        self.particles = particles  # List to store active particles
        self.arrows = []  # List to store active arrows
    
    def update(self):
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        # Update arrows
        self.arrows = [arrow for arrow in self.arrows if arrow.update()]
        
    def draw(self, window):
        # Draw fun particles
        for particle in self.particles:
            particle.draw(window)
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(window)

class Arrow:
    def __init__(self, x, y, target_x, target_y, speed=15):
        self.x = x
        self.y = y
        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        # Normalize direction
        self.dx = (dx / distance) * speed if distance > 0 else 0
        self.dy = (dy / distance) * speed if distance > 0 else 0
        self.lifetime = 30  # Arrow exists for 30 frames
        self.length = 20  # Arrow length in pixels
        self.angle = math.atan2(dy, dx)  # Store angle for drawing

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, window):
        # Draw arrow body (line)
        end_x = self.x - math.cos(self.angle) * self.length
        end_y = self.y - math.sin(self.angle) * self.length
        pygame.draw.line(window, (139, 69, 19), (self.x, self.y), (end_x, end_y), 3)
        
        # Draw arrow head (triangle)
        head_size = 8
        head_angle1 = self.angle + math.pi/4
        head_angle2 = self.angle - math.pi/4
        head_points = [
            (self.x, self.y),
            (self.x - head_size * math.cos(head_angle1), self.y - head_size * math.sin(head_angle1)),
            (self.x - head_size * math.cos(head_angle2), self.y - head_size * math.sin(head_angle2))
        ]
        pygame.draw.polygon(window, (139, 69, 19), head_points)

# Create game object
game = Game()

# Game options
class GameOptions:
    def __init__(self):
        self.p1_weapon = "sword"  # "sword" or "bow" or "spear"
        self.p2_weapon = "sword"  # "sword" or "bow" or "spear"

# Create global options
game_options = GameOptions()

# Colors for wood grain
WOOD_COLORS = [
    (120, 81, 45),   # Dark wood
    (139, 90, 43),   # Medium wood
    (160, 120, 95),  # Light wood
    (101, 67, 33),   # Deep wood
]
WOOD_GRAIN_COLOR = (90, 60, 30)  # Dark line for wood grain

def draw_wood_handle(window, x, y, width, height, angle=0):
    # Base wood color
    handle_rect = pygame.Rect(x - width//2, y - height//2, width, height)
    pygame.draw.rect(window, WOOD_COLORS[0], handle_rect)
    
    # Draw wood grain lines
    grain_spacing = 3
    for i in range(height//grain_spacing):
        y_pos = y - height//2 + i * grain_spacing
        # Wavy line effect
        wave = math.sin(i * 0.5) * 2
        start_x = x - width//2 + wave
        end_x = x + width//2 + wave
        # Draw darker grain line
        pygame.draw.line(window, WOOD_GRAIN_COLOR, 
                        (start_x, y_pos), 
                        (end_x, y_pos), 1)
        
    # Add some random knots in the wood
    for _ in range(2):
        knot_x = x + random.randint(-width//3, width//3)
        knot_y = y + random.randint(-height//3, height//3)
        pygame.draw.circle(window, WOOD_COLORS[3], (knot_x, knot_y), 2)
        # Draw grain around knot
        pygame.draw.circle(window, WOOD_COLORS[2], (knot_x, knot_y), 3, 1)

class WeaponButton:
    def __init__(self, x, y, width, height, weapon_type, player_num):
        self.rect = pygame.Rect(x, y, width, height)
        self.weapon_type = weapon_type
        self.player_num = player_num
        self.attacking = False
        self.attack_frame = 0
        self.attack_duration = 30
        self.facing_right = True
        self.hover = False
        # Load weapon images with full path
        image_path = os.path.join(os.path.dirname(__file__), "images", f"{weapon_type}.png")
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (50, 50))  # Made images bigger
        except:
            print(f"Could not load image: {image_path}")
            self.image = None

    def draw(self, window, font, is_selected):
        # Define colors once at the start
        steel_color = (176, 196, 222)    # Light steel blue
        steel_dark = (119, 136, 153)     # Dark steel
        diamond_shine = (220, 240, 255)  # White-blue shine
        wood_color = (90, 75, 60)        # Light wood
        gold_color = (255, 215, 0)       # Gold for diamonds
        brown_dark = (139, 69, 19)       # Dark brown
        string_color = (220, 220, 220)   # Light gray for bowstring

        # Colors
        if is_selected:
            color = (0, 150, 0) if self.weapon_type == "sword" else (0, 0, 150) if self.weapon_type == "bow" else (150, 0, 0)
        else:
            base_color = (0, 100, 0) if self.weapon_type == "sword" else (0, 0, 100) if self.weapon_type == "bow" else (100, 0, 0)
            color = (min(base_color[0] + 30, 255), 
                    min(base_color[1] + 30, 255), 
                    min(base_color[2] + 30, 255)) if self.hover else base_color
        
        # Draw button
        pygame.draw.rect(window, color, self.rect)
        pygame.draw.rect(window, (0, 0, 0), self.rect, 2)
        
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
            pygame.draw.polygon(window, steel_color, blade_points)  # Light steel color
            
            # Add sharp edge highlight
            edge_points = [
                (self.rect.centerx + blade_length, self.rect.centery),  # Tip
                (self.rect.centerx + (blade_length-10), self.rect.centery - 2),  # Top edge
                (self.rect.centerx + (blade_length-10), self.rect.centery + 2),  # Bottom edge
            ]
            pygame.draw.lines(window, steel_dark, True, edge_points, 1)

            # Diamond pattern on blade
            for i in range(3):
                diamond_x = self.rect.centerx + 25 + (i * 15)
                diamond_points = [
                    (diamond_x, self.rect.centery - 2),  # Top
                    (diamond_x + 4, self.rect.centery),  # Right
                    (diamond_x, self.rect.centery + 2),  # Bottom
                    (diamond_x - 4, self.rect.centery),  # Left
                ]
                pygame.draw.polygon(window, diamond_shine, diamond_points)
                pygame.draw.lines(window, steel_dark, True, diamond_points, 1)

            # Gold diamond at base
            diamond_size = 6
            diamond_points = [
                (self.rect.centerx + 15, self.rect.centery - diamond_size),  # Top
                (self.rect.centerx + 15 + diamond_size, self.rect.centery),  # Right
                (self.rect.centerx + 15, self.rect.centery + diamond_size),  # Bottom
                (self.rect.centerx + 15 - diamond_size, self.rect.centery),  # Left
            ]
            pygame.draw.polygon(window, gold_color, diamond_points)
            pygame.draw.lines(window, brown_dark, True, diamond_points, 1)

            # Draw sword handle with wood grain
            handle_x = self.rect.centerx + 15
            draw_wood_handle(window, handle_x, self.rect.centery, 8, 20)
            
            # Wood guard - thinner version
            guard_x = self.rect.centerx + 15
            pygame.draw.rect(window, wood_color,
                           (guard_x - 8, self.rect.centery - 3, 16, 6))
            
            # Diamond shine effects on blade
            for i in range(3):
                shine_x = self.rect.centerx + 25 + (i*10)
                pygame.draw.line(window, diamond_shine,
                               (shine_x, self.rect.centery - 3 - i),
                               (shine_x + 8, self.rect.centery - 5 - i), 2)

        elif self.weapon_type == "bow":
            # Colors
            wood_color = (90, 75, 60)        # Light wood
            wood_dark = (139, 69, 19)        # Dark wood
            gold_color = (255, 215, 0)       # Gold
            string_color = (220, 220, 220)   # Light gray
            diamond_shine = (220, 240, 255)  # White-blue shine
            steel_color = (176, 196, 222)    # Light steel blue
            steel_dark = (119, 136, 153)     # Dark steel

            bow_height = 60
            # Calculate bow position based on attack frame
            if self.attacking:
                attack_progress = min(1.0, self.attack_frame / max(1, self.attack_duration))
                string_pull = math.sin(attack_progress * math.pi) * 20  # Maximum pull of 20 pixels
            else:
                string_pull = 0

            # Main bow curve
            if self.facing_right:
                pygame.draw.arc(window, wood_color,
                              [self.rect.centerx - 10, self.rect.centery - bow_height//2, 40, bow_height],
                              -math.pi/3, math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(window, wood_dark,
                              [self.rect.centerx - 12, self.rect.centery - bow_height//2 - 2, 44, bow_height + 4],
                              -math.pi/3, math.pi/3, 2)
            else:
                pygame.draw.arc(window, wood_color,
                              [self.rect.centerx - 30, self.rect.centery - bow_height//2, 40, bow_height],
                              2*math.pi/3, 4*math.pi/3, 3)
                # Decorative outer curve
                pygame.draw.arc(window, wood_dark,
                              [self.rect.centerx - 32, self.rect.centery - bow_height//2 - 2, 44, bow_height + 4],
                              2*math.pi/3, 4*math.pi/3, 2)

            # Gold decorations at bow tips
            tip_radius = 4
            # Top tip
            top_x = self.rect.centerx + (10 if self.facing_right else -10)
            pygame.draw.circle(window, gold_color, (top_x, self.rect.centery - bow_height//2), tip_radius)
            pygame.draw.circle(window, wood_dark, (top_x, self.rect.centery - bow_height//2), tip_radius, 1)
            # Bottom tip
            pygame.draw.circle(window, gold_color, (top_x, self.rect.centery + bow_height//2), tip_radius)
            pygame.draw.circle(window, wood_dark, (top_x, self.rect.centery + bow_height//2), tip_radius, 1)

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
                pygame.draw.polygon(window, diamond_shine, diamond_points)
                pygame.draw.lines(window, wood_dark, True, diamond_points, 1)

            # Bowstring
            string_start = (top_x, self.rect.centery - bow_height//2)
            string_end = (top_x, self.rect.centery + bow_height//2)
            string_mid = (self.rect.centerx + (-15 - string_pull if self.facing_right else 15 + string_pull), self.rect.centery)
            
            # Draw curved bowstring
            points = [string_start, string_mid, string_end]
            pygame.draw.lines(window, string_color, False, points, 2)

            # Only draw arrow when attacking
            if self.attacking:
                arrow_length = 30
                arrow_x = self.rect.centerx + (-20 - string_pull if self.facing_right else 20 + string_pull)
                arrow_dir = 1 if self.facing_right else -1
                
                # Wooden arrow shaft with gold rings
                pygame.draw.line(window, wood_color,
                               (arrow_x, self.rect.centery),
                               (arrow_x + arrow_length * arrow_dir, self.rect.centery), 3)
                
                # Gold decorative rings
                for i in range(2):
                    ring_x = arrow_x + (10 + i*10) * arrow_dir
                    pygame.draw.circle(window, gold_color, (ring_x, self.rect.centery), 2)
                    pygame.draw.circle(window, wood_dark, (ring_x, self.rect.centery), 2, 1)

                # Steel arrowhead
                head_length = 12
                head_width = 6
                head_x = arrow_x + arrow_length * arrow_dir
                head_points = [
                    (head_x, self.rect.centery),  # Base
                    (head_x + head_length * arrow_dir, self.rect.centery),  # Tip
                    (head_x + head_length * 0.7 * arrow_dir, self.rect.centery - head_width//2),  # Top barb
                    (head_x + head_length * 0.7 * arrow_dir, self.rect.centery + head_width//2),  # Bottom barb
                ]
                pygame.draw.polygon(window, steel_color, head_points)
                pygame.draw.lines(window, steel_dark, True, head_points, 1)

                # Feathers at arrow base
                feather_length = 8
                feather_width = 3
                for offset in [-1, 1]:  # Top and bottom feathers
                    feather_points = [
                        (arrow_x, self.rect.centery + offset * feather_width),
                        (arrow_x - feather_length * arrow_dir, self.rect.centery),
                        (arrow_x, self.rect.centery)
                    ]
                    pygame.draw.polygon(window, WHITE, feather_points)
                    pygame.draw.lines(window, (200, 200, 200), True, feather_points, 1)
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
            pygame.draw.line(window, wood_color,
                           (self.rect.centerx, self.rect.centery),
                           (shaft_end, self.rect.centery), 3)
            
            # Gold rings along shaft
            for i in range(3):
                ring_x = self.rect.centerx + ((20 + i*25) if self.facing_right else -(20 + i*25))
                pygame.draw.circle(window, gold_color, (ring_x, self.rect.centery), 3)
                pygame.draw.circle(window, wood_dark, (ring_x, self.rect.centery), 3, 1)

            # Spearhead - steel blade
            head_points = [
                (shaft_end, self.rect.centery),  # Base
                (shaft_end + (head_length if self.facing_right else -head_length), self.rect.centery),  # Tip
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.rect.centery - 8),  # Top barb
                (shaft_end + (head_length*0.8 if self.facing_right else -head_length*0.8), self.rect.centery + 8),  # Bottom barb
            ]
            pygame.draw.polygon(window, steel_color, head_points)
            pygame.draw.lines(window, steel_dark, True, head_points, 2)

            # Diamond decorations on blade
            for i in range(2):
                diamond_x = shaft_end + ((head_length*0.4 + i*8) if self.facing_right else -(head_length*0.4 + i*8))
                diamond_points = [
                    (diamond_x, self.rect.centery - 3),  # Top
                    (diamond_x + (3 if self.facing_right else -3), self.rect.centery),  # Right
                    (diamond_x, self.rect.centery + 3),  # Bottom
                    (diamond_x - (3 if self.facing_right else -3), self.rect.centery),  # Left
                ]
                pygame.draw.polygon(window, diamond_shine, diamond_points)
                pygame.draw.lines(window, steel_dark, True, diamond_points, 1)

            # Gold decoration at spear base
            base_x = self.rect.centerx + (5 if self.facing_right else -5)
            pygame.draw.circle(window, gold_color, (base_x, self.rect.centery), 4)
            # Add diamond decoration to pommel
            pommel_diamond_size = 2
            pommel_diamond_points = []
            for i in range(4):
                point_angle = math.pi/2 + (i * math.pi/2)
                dx = base_x + math.cos(point_angle) * pommel_diamond_size
                dy = self.rect.centery + math.sin(point_angle) * pommel_diamond_size
                pommel_diamond_points.append((dx, dy))
            pygame.draw.polygon(window, diamond_shine, pommel_diamond_points)
            pygame.draw.polygon(window, steel_dark, pommel_diamond_points, 1)
        
        # Draw label below button
        button_font = pygame.font.Font(None, 24)
        label = f"{self.weapon_type.title()}"
        text = button_font.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.centery + 40))
        window.blit(text, text_rect)
        
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
mountains = [
    Mountain(100, 200),
    Mountain(300, 250),
    Mountain(500, 180),
    Mountain(700, 220)
]
benches = [
    Bench(200, 450, 200, 15),   # Middle high bench
    Bench(500, 500, 200, 15),   # Right ground bench
    Bench(100, 500, 200, 15),   # Left ground bench
    Bench(50, 350, 150, 15),    # Left high bench
    Bench(600, 350, 150, 15),   # Right high bench
    Bench(350, 250, 150, 15),   # Top middle bench
    Bench(350, 500, 100, 15),   # Small middle ground bench
    Bench(350, 150, 100, 15),   # Very top bench
]

# Create platforms (benches)
platforms = [
    pygame.Rect(200, 450, 200, 20),   # Middle high bench
    pygame.Rect(500, 500, 200, 20),   # Right ground bench
    pygame.Rect(100, 500, 200, 20),   # Left ground bench
    pygame.Rect(50, 350, 150, 20),    # Left high bench
    pygame.Rect(600, 350, 150, 20),   # Right high bench
    pygame.Rect(350, 250, 150, 20),   # Top middle bench
    pygame.Rect(350, 500, 100, 20),   # Small middle ground bench
    pygame.Rect(350, 150, 100, 20),   # Very top bench
]

# Colors for benches
bench_color = (139, 69, 19)  # Dark wood color
bench_border = (90, 50, 10)  # Darker wood for border

def draw_window(window, player1, player2, mountains, benches, options):
    # Draw sky first
    draw_sky(window)
    
    # Draw rest of the scene
    for mountain in mountains:
        mountain.draw(window)
    
    # Draw all benches
    for bench in benches:
        bench.draw(window)
    
    # Draw ground
    ground_rect = pygame.Rect(0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20)
    pygame.draw.rect(window, (40, 20, 0), ground_rect)  # Dark brown ground

def check_winner():
    if player1.health <= 0:
        return "Player 2 Wins!"
    elif player2.health <= 0:
        return "Player 1 Wins!"
    return None

def draw_game_over(window, font, player1, player2):
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    window.blit(overlay, (0, 0))
    
    # Draw winner text
    winner_text = check_winner()
    if winner_text:
        text = font.render(winner_text, True, (0, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        window.blit(text, text_rect)
    
    # Draw weapon selection
    selection_font = pygame.font.Font(None, 32)
    
    # Draw weapon buttons
    for button in game_over_weapon_buttons:
        is_selected = (button.player_num == 1 and button.weapon_type == game_options.p1_weapon) or \
                     (button.player_num == 2 and button.weapon_type == game_options.p2_weapon)
        button.draw(window, selection_font, is_selected)
    
    # Draw play again and quit buttons lower
    play_again_btn = Button(WINDOW_WIDTH//2 - 60, WINDOW_HEIGHT - 100, 120, 40, "Play Again")
    quit_btn = Button(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 50, 80, 30, "Quit")
    
    play_again_btn.draw(window)
    quit_btn.draw(window)
    
    return play_again_btn, quit_btn

def draw_health_bars(window, player1, player2):
    # Draw Player 1 health bar
    pygame.draw.rect(window, RED, (50, 20, 200, 20))
    pygame.draw.rect(window, GREEN, (50, 20, player1.health * 2, 20))
    
    # Draw Player 2 health bar
    pygame.draw.rect(window, RED, (WINDOW_WIDTH - 250, 20, 200, 20))
    pygame.draw.rect(window, GREEN, (WINDOW_WIDTH - 250, 20, player2.health * 2, 20))

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (100, 100, 100)  # Default gray
        self.hover_color = (150, 150, 150)  # Lighter gray for hover
        self.text_color = (0, 0, 0)
        self.font = pygame.font.Font(None, 32)
        self.is_hovered = False

    def draw(self, window):
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(window, color, self.rect)
        pygame.draw.rect(window, (0, 0, 0), self.rect, 2)  # Black border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        window.blit(text_surface, text_rect)

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

# Create players with their controls
player1 = None
player2 = None
p1_name_input = ""
p2_name_input = ""
active_input = 0

# Game font
font = pygame.font.Font(None, 74)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

clock = pygame.time.Clock()

# Initialize game state
game_state = MENU  # Start in menu state

def reset_game():
    global player1, player2, game_state, p1_name_input, p2_name_input
    # Set player names from input
    p1_name = p1_name_input if p1_name_input else "P1"
    p2_name = p2_name_input if p2_name_input else "P2"
    
    # Create players with their selected weapons
    player1 = Player(100, WINDOW_HEIGHT - 100, (255, 0, 0), True, 
                    {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "attack": pygame.K_SPACE, "defend": pygame.K_e}, 1)
    player2 = Player(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100, (0, 0, 255), False,
                    {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "attack": pygame.K_RETURN, "defend": pygame.K_RSHIFT}, 2)
    
    # Set names and weapons
    player1.name = p1_name
    player2.name = p2_name
    # Set weapons from game options
    player1.weapon = game_options.p1_weapon
    player2.weapon = game_options.p2_weapon
    
    game_state = PLAYING

# Add name input functions
def draw_name_inputs(window, font):
    global p1_name_input, p2_name_input, active_input
    
    # Draw input boxes
    p1_box = pygame.Rect(WINDOW_WIDTH//4 - 50, 150, 100, 32)
    p2_box = pygame.Rect(2*WINDOW_WIDTH//3 - 50, 150, 100, 32)
    
    # Draw boxes
    box_color = (100, 100, 100)
    pygame.draw.rect(window, box_color, p1_box, 2)
    pygame.draw.rect(window, box_color, p2_box, 2)
    
    # Render text
    p1_text = font.render(p1_name_input + ('|' if active_input == 1 else ''), True, (0, 0, 0))
    p2_text = font.render(p2_name_input + ('|' if active_input == 2 else ''), True, (0, 0, 0))
    
    # Draw text
    window.blit(p1_text, (p1_box.x + 5, p1_box.y + 5))
    window.blit(p2_text, (p2_box.x + 5, p2_box.y + 5))
    
    # Draw labels
    label_font = pygame.font.Font(None, 24)
    p1_label = label_font.render("Enter P1 Name (max 7)", True, (0, 0, 0))
    p2_label = label_font.render("Enter P2 Name (max 7)", True, (0, 0, 0))
    window.blit(p1_label, (p1_box.x - 20, p1_box.y - 20))
    window.blit(p2_label, (p2_box.x - 20, p2_box.y - 20))

def handle_name_input(event):
    global p1_name_input, p2_name_input, active_input
    
    # Handle mouse clicks for input boxes
    if event.type == pygame.MOUSEBUTTONDOWN:
        # P1 input box
        p1_box = pygame.Rect(WINDOW_WIDTH//4 - 50, 150, 100, 32)
        if p1_box.collidepoint(event.pos):
            active_input = 1
        # P2 input box
        p2_box = pygame.Rect(2*WINDOW_WIDTH//3 - 50, 150, 100, 32)
        if p2_box.collidepoint(event.pos):
            active_input = 2
            
    # Handle keyboard input
    if event.type == pygame.KEYDOWN and active_input:
        if event.key == pygame.K_RETURN:
            active_input = None
        elif event.key == pygame.K_BACKSPACE:
            if active_input == 1:
                p1_name_input = p1_name_input[:-1]
            else:
                p2_name_input = p2_name_input[:-1]
        else:
            # Add character if within limit and is a valid character
            if active_input == 1 and len(p1_name_input) < 7:
                if event.unicode.isalnum() or event.unicode in ['-', '_']:
                    p1_name_input += event.unicode
            elif active_input == 2 and len(p2_name_input) < 7:
                if event.unicode.isalnum() or event.unicode in ['-', '_']:
                    p2_name_input += event.unicode

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
                    reset_game()  # Call reset_game to create players with selected weapons
                    game_state = PLAYING
                # Check quit button
                if quit_button.rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    running = False
        
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                # Player 1 jump with SPACE
                if event.key == pygame.K_SPACE:
                    player1.dy = player1.jump_power
                    player1.is_jumping = True
                    player1.on_platform = False
                    player1.current_platform = None
                    jump_sound.play()  # Play jump sound
                # Player 2 jump with UP
                if event.key == pygame.K_UP:
                    player2.dy = player2.jump_power
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
                    reset_game()  # Reset the game state
                    game_state = PLAYING
                # Check quit button
                quit_rect = pygame.Rect(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 50, 80, 30)
                if quit_rect.collidepoint(mouse_pos):
                    button_click_sound.play()  # Play click sound
                    running = False
        
        handle_name_input(event)
    
    # Update game state
    if game_state == PLAYING:
        # Reset platform status at start of frame
        if player1:
            player1.on_platform = False
        if player2:
            player2.on_platform = False
        
        # Move players
        if player1:
            player1.move()
            player1.update()
        if player2:
            player2.move()
            player2.update()
        
        # Check bench collisions for both players
        for bench in benches:
            if player1:
                bench.check_collision(player1)
            if player2:
                bench.check_collision(player2)
        
        # Update attacks
        if player1 and player2:
            player1.update_attack(player2)
            player2.update_attack(player1)
        
        # Update game particles
        game.update()
        
        # Check for game over
        if player1 and player2:
            if player1.health <= 0 or player2.health <= 0:
                game_state = GAME_OVER
    
    # Draw everything
    screen.fill((135, 206, 235))  # Sky blue background
    
    if game_state == MENU:
        draw_window(screen, player1, player2, mountains, benches, game_options)
        draw_name_inputs(screen, pygame.font.Font(None, 32))
        start_button.draw(screen)
        quit_button.draw(screen)
        title_font = pygame.font.Font(None, 48)  
        player_font = pygame.font.Font(None, 32)  
        title_text = title_font.render("Seowoo's Epic Battle Game", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        p1_text = player_font.render("Player 1", True, (0, 0, 0))
        p2_text = player_font.render("Player 2", True, (0, 0, 0))
        screen.blit(p1_text, (WINDOW_WIDTH//4 - 30, 100))  
        screen.blit(p2_text, (2*WINDOW_WIDTH//3 - 30, 100))  
        for button in menu_weapon_buttons:
            is_selected = (button.player_num == 1 and button.weapon_type == game_options.p1_weapon) or \
                         (button.player_num == 2 and button.weapon_type == game_options.p2_weapon)
            button.draw(screen, font, is_selected)
    elif game_state == PLAYING:
        draw_window(screen, player1, player2, mountains, benches, game_options)
        if player1:
            player1.draw(screen)
        if player2:
            player2.draw(screen)
        draw_health_bars(screen, player1, player2)
        
        # Draw platforms (benches)
        for platform in platforms:
            pygame.draw.rect(screen, bench_color, platform)
            pygame.draw.rect(screen, bench_border, platform, 2)  # Add border
            
            # Draw bench legs
            leg_width = 10
            pygame.draw.rect(screen, bench_color, (platform.left + 20, platform.bottom, leg_width, 30))
            pygame.draw.rect(screen, bench_color, (platform.right - 30, platform.bottom, leg_width, 30))
        
        # Draw game particles
        game.draw(screen)
    elif game_state == GAME_OVER:
        draw_window(screen, player1, player2, mountains, benches, game_options)
        if player1:
            player1.draw(screen)
        if player2:
            player2.draw(screen)
        draw_health_bars(screen, player1, player2)
        draw_game_over(screen, font, player1, player2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()