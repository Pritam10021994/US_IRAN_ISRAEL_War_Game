"""
╔══════════════════════════════════════════════════════╗
║         WAR OF PRIDE & HONOR                        ║
║   An Angry-Birds Style Artillery Game               ║
║   Featuring: Trump | Netanyahu | Khamenei           ║
╚══════════════════════════════════════════════════════╝
Requirements: pip install pygame
Run: python main.py
"""

import pygame
import sys
from game import WarGame

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("⚔️  War of Pride & Honor  ⚔️")
    
    clock = pygame.time.Clock()
    game = WarGame(screen, clock)
    game.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
