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

   
font = pygame.font.Font('Resources\\8-BIT WONDER.ttf', 32)

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT)) # Sets the size of the screen
pygame.display.set_caption("Snowy Peaks") # Sets the name of the game

class Player(pygame.sprite.Sprite): # Creates the player
    def __init__(self):
        super().__init__() 

        #NEW!!(Update)
        self.image = pygame.image.load("Resources\Character.png") # Loads the image
        self.image = pygame.transform.scale(self.image, (30, 30)) # Resizes the image
        self.rect = self.image.get_rect(center = (15, 415)) # Creates the rectangle of the player

        self.pos = vec((10, 385)) # Sets the position of the player
        self.vel = vec(0,0) # Sets the velocity of the player
        self.acc = vec(0,0) # Sets the acceleration of the player

           
        self.jumping = False
        self.score = 0 #High Score

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
                if self.pos.y < hits[0].rect.bottom: #Prevents character from clipping through the platform   
                       
                    if hits[0].point == True: #Adds points  
                        hits[0].point = False   
                        self.score += 1  

                    self.pos.y = hits[0].rect.top +1
                    self.vel.y = 0
                    self.jumping = False

    def jump(self): # Allows the player to jump
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits: # Prevents double jump
            self.vel.y = -15


class platform(pygame.sprite.Sprite): # Creates the platforms
    def __init__(self):
        super().__init__()
        
        #NEW!!(Update)
        self.image = pygame.image.load("Resources\Platform.png") # Loads the image
        self.image = pygame.transform.scale(self.image, (random.randint(50,100), 12)) # Resizes the image
        self.rect = self.image.get_rect(center = (random.randint(0,WIDTH-10), random.randint(0, HEIGHT-30))) # Creates the rectangle of the platform
           
        self.moving = True
        self.point = True
        self.speed = random.randint(-1, 1) #Moving Platform


    def move(self):
        if self.moving == True: #Moves the platform
            self.rect.move_ip(self.speed,0)
            if self.speed > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = WIDTH

   
def check(platform, groupies): #Prevents platforms from forming too close to each other
    if pygame.sprite.spritecollideany(platform,groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 40) and (abs(platform.rect.bottom - entity.rect.top) < 40):
                return True
        C = False

def plat_gen(): # Generates platforms ahead of time

    while len(platforms) < 7 : # Generates platforms until there are 7
        width = random.randrange(50,100)
        p  = platform()         

        C = True    
        while C: #Implements check to platform gen     
             p = platform()
             p.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-50, 0))
             C = check(p, platforms)
        platforms.add(p)
        all_sprites.add(p)
 
PT1 = platform() # Creates the first platform
P1 = Player() # Creates the player

 
PT1.surf = pygame.Surface((WIDTH, 20)) # Makes the random platforms
PT1.surf.fill((255,0,0))
PT1.rect = PT1.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

all_sprites = pygame.sprite.Group() # Creates the group of all sprites
all_sprites.add(PT1) # Adds the first platform to the group
all_sprites.add(P1) # Adds the player to the group

platforms = pygame.sprite.Group() # Creates the group of platforms
platforms.add(PT1)

   
PT1.moving = False #Sets up moving platforms
PT1.point = False

for x in range(random.randint(5, 6)): #Allows for the creation of multiple platforms
    C = True
    pl = platform()
    while C:
        pl = platform()
        C = check(pl, platforms)
    platforms.add(pl)
    all_sprites.add(pl)

def Title(): #Creates the title screen
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: # When the player presses a key  
                if event.key == pygame.K_RETURN: # If the player presses Enter
                    displaysurface.fill((0,0,0))
                    pygame.display.update()
                    Game() # Starts the game

        TitleImg = pygame.image.load('Resources\\Title.png')
        displaysurface.fill((0,0,0))
        displaysurface.blit(TitleImg, (0,0))
        pygame.display.update()
        FramePerSec.tick(FPS)

def Game():
    #NEW!!
    bg = pygame.image.load("Resources\\Background.png") #adds background

    while True: # Game loop

        P1.update() # Updates the player

        for event in pygame.event.get(): # Gets all the events
            if event.type == QUIT: # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: # When the player presses a key  
                if event.key == pygame.K_w: # If the player presses W
                    P1.jump()

         
        if P1.rect.top <= HEIGHT / 3: #Destroys platforms if they leave the screen
            P1.pos.y += abs(P1.vel.y)
            for plat in platforms:
                plat.rect.y += abs(P1.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()


        plat_gen() # Generates platforms

           
        displaysurface.fill((0,0,0))
        #NEW!!
        displaysurface.blit(bg, (0,0)) #adds background
        
        g  = font.render(str(P1.score), True, (255,255,255)) #Displays the score
        displaysurface.blit(g, (WIDTH/2 - 16, 10))



        for entity in all_sprites: # For every entity in the group
            #NEW!!(Update)
            displaysurface.blit(entity.image, entity.rect) # Displays the entity to the screen

            entity.move() # Moves the entity

           
        if P1.rect.top > HEIGHT: #Moves to Game Over screen
            for entity in all_sprites:
                entity.kill()
                time.sleep(1)
                displaysurface.fill((0,0,0))
                pygame.display.update()
                time.sleep(1)
                GameOver()

        pygame.display.update() # Updates the screen (basically process each frame)
        FramePerSec.tick(FPS) # Sets the FPS

   
def GameOver():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        GameOverImg = pygame.image.load('Resources\\GameOver.png')
        displaysurface.fill((0,0,0))
        displaysurface.blit(GameOverImg, (0,0))
        pygame.display.update()
        FramePerSec.tick(FPS)

Title() # Runs the game