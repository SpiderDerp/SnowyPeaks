import pygame
from pygame.locals import *
import sys
import random
import time
 
pygame.init()
vec = pygame.math.Vector2  # Allows game to be 2d
 
HEIGHT = 450 # Height of the screen
WIDTH = 400 # Width of the screen
ACC = 0.5 # Acceleration of the character
FRIC = -0.12 # Friction of the character
FPS = 60 # Frames per second
 
FramePerSec = pygame.time.Clock() # FPS
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT)) # Sets the size of the screen
pygame.display.set_caption("Snowy Peaks") # Sets the name of the game

class Player(pygame.sprite.Sprite): # Creates the player
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface((30, 30)) # Creates the surface of the player
        self.surf.fill((128,255,40)) # Fills the surface with a color
        self.rect = self.surf.get_rect(center = (15, 415)) # Creates the rectangle of the player

        self.pos = vec((10, 385)) # Sets the position of the player
        self.vel = vec(0,0) # Sets the velocity of the player
        self.acc = vec(0,0) # Sets the acceleration of the player

    def move(self): # Moves the player
        self.acc = vec(0,0.5) #Adds gravity to the player
    
        pressed_keys = pygame.key.get_pressed()
                
        if pressed_keys[K_a]: # Uses A and D to move
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC 
        
        self.acc.x += self.vel.x * FRIC # Adds friction to the player
        self.vel += self.acc # Adds acceleration to the player
        self.pos += self.vel + 0.5 * self.acc # Determines position of the player

        if self.pos.x > WIDTH: # If the player goes off the screen it will appear on the other side
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
     
        self.rect.midbottom = self.pos

    def update(self): # Object Collision
        hits = pygame.sprite.spritecollide(P1 , platforms, False)
        if P1.vel.y > 0:
            if hits:
                self.pos.y = hits[0].rect.top + 1
                self.vel.y = 0

    def jump(self): # Allows the player to jump
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits: # Prevents double jump
            self.vel.y = -15


class platform(pygame.sprite.Sprite): # Creates the platforms
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20)) # Creates the surface of the platform
        self.surf.fill((255,0,0)) # Fills the surface with a color
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10)) # Creates the rectangle of the platform
    
    def move(self):
        pass


 
PT1 = platform() # Creates the first platform
P1 = Player() # Creates the player

all_sprites = pygame.sprite.Group() # Creates the group of all sprites
all_sprites.add(PT1) # Adds the first platform to the group
all_sprites.add(P1) # Adds the player to the group

platforms = pygame.sprite.Group() # Creates the group of platforms
platforms.add(PT1)


 

def Game():
    while True: # Game loop
        for event in pygame.event.get(): # Gets all the events
            if event.type == QUIT: # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: # When the player presses a key  
                if event.key == pygame.K_w: # If the player presses W
                    P1.jump()

        displaysurface.fill((0,0,0)) # Fills the screen with a color

        P1.update() # Updates the player

        for entity in all_sprites: # For every entity in the group
            displaysurface.blit(entity.surf, entity.rect) # Displays the entity to the screen
            entity.move() # Moves the entity
    
        pygame.display.update() # Updates the screen (basically process each frame)
        FramePerSec.tick(FPS) # Sets the FPS

Game() # Runs the game