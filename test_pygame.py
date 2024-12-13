import pygame

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Pygame Test")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill screen with white
    screen.fill(WHITE)
    
    # Draw a blue rectangle
    pygame.draw.rect(screen, BLUE, (150, 100, 100, 100))
    
    # Update display
    pygame.display.flip()

# Quit pygame
pygame.quit()
