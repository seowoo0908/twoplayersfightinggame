import sys
import os

print("Python Version:", sys.version)
print("\nPython Executable:", sys.executable)
print("\nPython Path:")
for path in sys.path:
    print(path)

print("\nChecking for pygame:")
try:
    import pygame
    print("Pygame version:", pygame.version.ver)
    print("Pygame path:", pygame.__file__)
except ImportError as e:
    print("Error importing pygame:", e)

input("\nPress Enter to continue...")
