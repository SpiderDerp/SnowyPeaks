import pygame
from pygame.locals import *
import sys
import random
import time
from pygame.math import Vector2

pygame.init()

HEIGHT = 450  # Height of the screen
WIDTH = 400  # Width of the screen
ACC = 0.5  # Acceleration of the character
GRAVITY = 0.5
FRIC = 0.2  # Friction of the character
FPS = 60  # Frames per second

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

    def __init__(self):

        super().__init__()
        self.surf = pygame.Surface(self.dimensions)  # Creates the surface "image" of the player sprite
        self.surf.fill((128, 255, 40))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the rectangular "hitbox" for the player using our graphical surface

        # TODO set initial position to center bottom of screen
        self.rect.midbottom = (WIDTH / 2, HEIGHT - 20)

        self.vel = Vector2(0, 0)  # Zeroes out the velocity of the player

    def move_horizontal(self, pressed_keys):  # Moves the player

        if pressed_keys[K_a]:  # Uses A and D to move
            self.vel.x -= ACC
        if pressed_keys[K_d]:
            self.vel.x += ACC

        if self.vel.x < ACC / 2:
            self.vel.x += FRIC
        elif self.vel.x > ACC / 2:
            self.vel.x -= FRIC

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        self.move_horizontal(pressed_keys)
        # Applies a positive vertical acceleration to the player
        # Since y-positive points down, this will cause the player to accelerate downwards, simulating gravity
        self.vel.y += GRAVITY
        self.rect.center += self.vel

    def late_update(self):  # Object Collision
        # Find out which platforms have collided with the player
        hits = pygame.sprite.spritecollide(self, terrain_sprites, dokill=False)

        # Makes sure player is approaching platform from the top (moving downwards, falling downwards onto it)
        if self.vel.y > 0:
            if hits:  # If the player is colliding with any platform
                # TODO check so player doesn't clip on top of or thorugh platforms
                if self.rect.bottom <= hits[0].rect.top + 1 + self.vel.y:  # Sets player y-position to be on top of platform
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
        # TODO make the jump a bit less potent
        hits = pygame.sprite.spritecollideany(player, terrain_sprites)
        if hits:  # Makes sure player is contacting a solid object (the platforms)
            self.vel.y = -12


class Platform(Entity):  # Creates the platforms
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))  # Creates the surface of the platform
        self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the hitbox of the platform
        self.rect.center = Vector2((WIDTH / 2, HEIGHT - 10))

    # TODO Randomizes size
    def randomize_size(self):
        # TODO New Feature - Generates a thinner platform with a random, variable width
        self.surf = pygame.Surface((random.randint(50, 100), 12))
        self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the hitbox of the platform

# TODO this class is new
class PlatformGenerator():
    vertical_counter = 0
    increment = 75

    def generate(self):
        new_platforms = pygame.sprite.Group()
        height_offset = random.randint(-5, 5)

        while self.vertical_counter < 2 * HEIGHT:
            move_up = random.choice([0, 1, 1, 1])
            if move_up:
                self.vertical_counter += self.increment
                height_offset = random.randint(-5, 5)
            platform = Platform()
            platform.randomize_size()
            platform.rect.centerx = random.randint(0, WIDTH)
            y_position = HEIGHT - self.vertical_counter +height_offset
            platform.rect.bottom = y_position

            new_platforms.add(platform)
        return new_platforms




ground = Platform()  # Creates the first platform
player = Player()  # Creates the player
sprites = pygame.sprite.Group()  # Creates the group of all sprites
sprites.add(ground)  # Adds the first platform to the group
sprites.add(player)  # Adds the player to the group
key_listeners = pygame.sprite.Group()  # Group of sprites that listen to key events
key_listeners.add(player)

terrain_sprites = pygame.sprite.Group()  # Creates the group of platforms
terrain_sprites.add(ground)
generator = PlatformGenerator()
for p in generator.generate():
    terrain_sprites.add(p)
    sprites.add(p)


def main():
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
