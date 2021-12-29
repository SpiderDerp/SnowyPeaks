import pygame
from pygame.locals import *
import sys
import random
import time
from pygame.math import Vector2

pygame.init()

HEIGHT = 450  # Height of the screen
WIDTH = 400  # Width of the screen
ACC = 0.4  # Acceleration of the character
GRAVITY = 0.3
FRIC = 0.3  # Friction of the character
FPS = 60  # Frames per second

JUMP = 8

frame_clock = pygame.time.Clock()  # FPS

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))  # Sets the size of the screen
pygame.display.set_caption("Snowy Peaks")  # Sets the name of the game


class Entity(pygame.sprite.Sprite):
    surf: pygame.Surface
    vel: Vector2
    rect: Rect

    def __init__(self):
        super().__init__()

    def update(self):
        pass

    def late_update(self):
        pass

    def on_key_down(self, event):
        pass


class Player(Entity):  # Class that represents the player
    dimensions = Vector2(30, 30)

    def __init__(self, terrain):
        self.terrain = terrain

        super().__init__()
        self.surf = pygame.Surface(self.dimensions)  # Creates the surface "image" of the player sprite
        self.surf.fill((128, 255, 40))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the rectangular "hitbox" for the player using our graphical surface

        self.vel = Vector2(0, 0)  # Zeroes out the velocity of the player

    def move_horizontal(self, pressed_keys):  # Moves the player

        if pressed_keys[K_a]:  # Uses A and D to move
            self.vel.x -= ACC
        if pressed_keys[K_d]:
            self.vel.x += ACC

        if self.vel.x < -FRIC:
            self.vel.x += FRIC
        elif self.vel.x > FRIC:
            self.vel.x -= FRIC
        else:
            self.vel.x = 0


    def update(self):
        pressed_keys = pygame.key.get_pressed()
        self.move_horizontal(pressed_keys)
        # Applies a positive vertical acceleration to the player
        # Since y-positive points down, this will cause the player to accelerate downwards, simulating gravity
        self.vel.y += GRAVITY
        self.rect.center += self.vel

    def late_update(self):  # Object Collision
        # Find out which platforms have collided with the player
        hits = pygame.sprite.spritecollide(self, self.terrain, dokill=False)

        # Makes sure player is approaching platform from the top (moving downwards, falling downwards onto it)
        if self.vel.y > 0:
            if hits:  # If the player is colliding with any platform
                self.rect.bottom = hits[0].rect.top + 1  # Sets player y-position to be on top of platform
                self.vel.y = 0  # Zeroes out velocity (Stops the object)

        # Makes it so the player does not go off screen
        # Clamp the x-values to the bounds of the screen
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.vel.x = 0
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel.x = 0

    def on_key_down(self, event):
        if event.key == K_w:
            self.jump()

    def jump(self):  # Allows the player to jump
        # Check if the player is touching terrain
        hits = pygame.sprite.spritecollideany(self, self.terrain)
        print(hits)
        if hits is not None:  # Makes sure player is contacting a solid object (the platforms)
            self.vel.y = -15


class Platform(Entity):  # Creates the platforms
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))  # Creates the surface of the platform
        self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the hitbox of the platform
        self.rect.center = Vector2((WIDTH / 2, HEIGHT - 10))




def main():


    ground = Platform()  # Creates the first platform

    terrain_sprites = pygame.sprite.Group()  # Creates the group of platforms
    terrain_sprites.add(ground)
    player = Player(terrain_sprites)  # Creates the player

    sprites = pygame.sprite.Group()  # Creates the group of all sprites
    sprites.add(ground)  # Adds the first platform to the group
    sprites.add(player)  # Adds the player to the group
    key_listeners = pygame.sprite.Group()  # Group of sprites that listen to key events
    key_listeners.add(player)

    while True:  # Game loop
        displaysurface.fill((0, 0, 0))  # Makes the background black

        entity: Entity
        for entity in sprites:
            entity.update()

        for event in pygame.event.get():  # Gets all the events
            if event.type == QUIT:  # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                for entity in key_listeners:
                    entity.on_key_down(event)

        for entity in sprites:
            entity.late_update()

        for entity in sprites:  # For every entity in the group
            displaysurface.blit(entity.surf, entity.rect)  # Displays the entity to the screen

        pygame.display.update()  # Updates the screen
        frame_clock.tick(FPS)  # Sets the FPS


main()  # Runs the game
