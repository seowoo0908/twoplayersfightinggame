import sys
import os

# Add the site-packages directory to Python's path
site_packages = r'C:\Users\user\AppData\Local\Programs\Python\Python312\Lib\site-packages'
if site_packages not in sys.path:
    sys.path.append(site_packages)

try:
    import pygame
    print("Successfully imported pygame version:", pygame.version.ver)
except ImportError as e:
    print("Failed to import pygame:", e)
    sys.exit(1)

# Run the main game
try:
    exec(open('main.py').read())
except Exception as e:
    print("Error running game:", e)
    input("Press Enter to exit...")
