try:
    import pygame
    print("Pygame successfully imported!")
    print(f"Pygame version: {pygame.version.ver}")
except ImportError as e:
    print(f"Error importing pygame: {e}")
    print("Python path:")
    import sys
    for path in sys.path:
        print(path)
