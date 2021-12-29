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
    image: pygame.Surface
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
    # New, to flip the sprite
    facing_right = True

    def __init__(self, scorekeeper):
        self.scorekeeper = scorekeeper

        super().__init__()

        # TODO new - loads and uses image, scaling it. surf is renamed to iamge because it makes sense
        # self.surf = pygame.Surface(self.dimensions)  # Creates the surface "image" of the player sprite
        # self.surf.fill((128, 255, 40))  # Fills the surface with a color
        self.image = pygame.image.load("Assets/Player.png")
        # TODO this is changed too, because our new player is a bit taller
        self.image = pygame.transform.scale(self.image, (20, 54))
        self.rect = self.image.get_rect()  # Creates the rectangular "hitbox" for the player using our graphical surface

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


        old_facing_right = self.facing_right
        # TODO new - determine where character is facing based on x-velocity
        # We use ACC because our velocity fluctuates a lot, print the velocity to show this
        if self.vel.x > ACC: # facing right
            self.facing_right = True
        elif self.vel.x < -ACC:
            self.facing_right = False
        # print(self.vel.x)

        if old_facing_right != self.facing_right: # If our facing direction changed
            self.image = pygame.transform.flip(self.image, True, False)

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
                if self.rect.bottom <= hits[
                    0].rect.top + 1 + self.vel.y:  # Sets player y-position to be on top of platform
                    self.rect.bottom = hits[0].rect.top + 1  # Sets player y-position to be on top of platform
                    self.vel.y = 0  # Zeroes out velocity (Stops the object)
                    scorekeeper.on_platform_hit(hits[0])


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
        hits = pygame.sprite.spritecollideany(player, terrain_sprites)
        if hits:  # Makes sure player is contacting a solid object (the platforms)
            self.vel.y = -12


class Platform(Entity):  # Creates the platforms
    def __init__(self):
        super().__init__()
        # TODO same as player, except here we're scaling wtih a default size and also renaming
        # self.surf = pygame.Surface((WIDTH, 20))  # Creates the surface of the platform
        # self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.image = pygame.image.load("Assets/Platform.png")
        self.image = pygame.transform.scale(self.image, (WIDTH, 20))
        self.rect = self.image.get_rect()  # Creates the hitbox of the platform
        self.rect.center = Vector2((WIDTH / 2, HEIGHT - 10))

    def randomize_size(self):
        # TODO Here we are just rescaling, no need to modify the image again, don't forget to rename it
        self.image = pygame.transform.scale(self.image, (random.randint(50, 100), 12))
        # self.image.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.image.get_rect()  # Creates the hitbox of the platform


class PlatformGenerator:
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
            y_position = HEIGHT - self.vertical_counter + height_offset
            platform.rect.bottom = y_position

            new_platforms.add(platform)
        return new_platforms

    def on_scroll_down(self, amount):
        # Now everything is offset, so we need to offset the counter down
        if amount >= 0:
            self.vertical_counter -= amount


# This class is new
class CameraController:
    def __init__(self, to_follow, to_move, listeners):
        self.to_follow = to_follow
        self.to_move = to_move
        self.listeners = listeners

    def follow(self):
        if self.to_follow.rect.centery < HEIGHT / 3:
            self.scroll_up(HEIGHT / 3 - self.to_follow.rect.centery)

    def scroll_up(self, dist):
        # Move everything that follows the camera down, to make the character appear like it's moving up
        self.to_follow.rect.y += dist
        for e in self.to_move:
            e.rect.y += dist
            if e.rect.top > HEIGHT:
                e.kill()

        for l in self.listeners:
            l.on_scroll_down(dist)


class Scorekeeper:
    font = pygame.font.Font('Assets\\8-BIT WONDER.ttf', 32)
    score = 0
    height_offset = HEIGHT

    def on_platform_hit(self, plat):
        if plat.rect.top < self.height_offset:
            self.score += 1
            self.height_offset = plat.rect.top
            print(self.height_offset)
            print(self.score)

    def on_scroll_down(self, dist):
        if dist >= 0:
            self.height_offset += dist

    def display(self):
        score_img = self.font.render(str(self.score), True, (255, 255, 255))
        displaysurface.blit(score_img, (WIDTH / 2 - 16, 10))


scorekeeper = Scorekeeper()

ground = Platform()  # Creates the first platform
player = Player(scorekeeper)  # Creates the player

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

# Instantiate camera controller
controller = CameraController(player, terrain_sprites, [generator, scorekeeper])

def start():
    # Temporary game loop for title screen
    title_image = pygame.image.load("Assets/Title.png")
    title_image = pygame.transform.scale(title_image, (WIDTH, HEIGHT))
    while True:  # Game loop
        for event in pygame.event.get():
            if event.type == QUIT:  # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                return
        displaysurface.fill((0, 0, 0))
        displaysurface.blit(title_image, (0, 0))
        pygame.display.update()
        frame_clock.tick(FPS)

def end():
    # Temporary game loop for title screen
    end_image = pygame.image.load("Assets/GameOver.png")
    end_image = pygame.transform.scale(end_image, (WIDTH, HEIGHT))
    while True:  # Game loop
        for event in pygame.event.get():
            if event.type == QUIT:  # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
        displaysurface.fill((0, 0, 0))
        displaysurface.blit(end_image, (0, 0))
        pygame.display.update()
        frame_clock.tick(FPS)


def check_if_end():
    if player.rect.top > HEIGHT:
        end()


def main():
    start()

    # TODO new initializer code loads the scene background
    bg = pygame.image.load("Assets/Background.png")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
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

        controller.follow()
        # If there is space for new platforms, make them:
        for new_platform in generator.generate():
            terrain_sprites.add(new_platform)
            sprites.add(new_platform)

        # TODO render background here, do it first because it's in the back
        displaysurface.blit(bg, (0, 0))

        for entity in sprites:  # For every entity in the group
            displaysurface.blit(entity.image, entity.rect)  # Displays the entity to the screen

        scorekeeper.display()
        check_if_end()

        pygame.display.update()  # Updates the screen
        frame_clock.tick(FPS)  # Sets the FPS


main()  # Runs the game
