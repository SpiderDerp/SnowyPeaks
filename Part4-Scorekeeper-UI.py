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

    # TODO new - add scorekeeper parameter to player
    def __init__(self, scorekeeper, terrain):
        self.scorekeeper = scorekeeper
        self.terrain = terrain

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
                if self.rect.bottom <= hits[
                    0].rect.top + 1 + self.vel.y:  # Sets player y-position to be on top of platform
                    self.rect.bottom = hits[0].rect.top + 1  # Sets player y-position to be on top of platform
                    self.vel.y = 0  # Zeroes out velocity (Stops the object)
                    # TODO new - bind player paltform hit to scorekeeper
                    self.scorekeeper.on_platform_hit(hits[0])

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
        hits = pygame.sprite.spritecollideany(self, self.terrain)
        if hits:  # Makes sure player is contacting a solid object (the platforms)
            self.vel.y = -12


class Platform(Entity):  # Creates the platforms
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))  # Creates the surface of the platform
        self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the hitbox of the platform
        self.rect.center = Vector2((WIDTH / 2, HEIGHT - 10))

    def randomize_size(self):
        self.surf = pygame.Surface((random.randint(50, 100), 12))
        self.surf.fill((255, 0, 0))  # Fills the surface with a color
        self.rect = self.surf.get_rect()  # Creates the hitbox of the platform


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

        # TODO trigger on scroll down event on all
        for l in self.listeners:
            l.on_scroll_down(dist)


# TODO - new class Scorekeeper
class Scorekeeper:
    font = pygame.font.Font('Assets/8-BIT WONDER.ttf', 32)
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

# TODO new, do after end screen, button for play again
class PlayAgainButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Assets/PlayAgain.png")
        self.image = pygame.transform.scale(self.image, (128, 84))
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH/2, HEIGHT * 5/6

    def on_mouse_click(self, position):
        if self.rect.collidepoint(position):
            main()



# TODO new start screen
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



# TODO new end screen
def end():
    # Temporary game loop for title screen
    end_image = pygame.image.load("Assets/GameOver.png")
    end_image = pygame.transform.scale(end_image, (WIDTH, HEIGHT))
    play_button = PlayAgainButton()

    while True:  # Game loop
        for event in pygame.event.get():
            if event.type == QUIT:  # If the event is a quit (X out of the window)
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                play_button.on_mouse_click(pygame.mouse.get_pos())
        displaysurface.fill((0, 0, 0))
        displaysurface.blit(end_image, (0, 0))

        displaysurface.blit(play_button.image, play_button.rect)
        pygame.display.update()
        frame_clock.tick(FPS)




def main():
    start()

    scorekeeper = Scorekeeper()

    ground = Platform()  # Creates the first platform

    terrain_sprites = pygame.sprite.Group()  # Creates the group of platforms
    terrain_sprites.add(ground)
    player = Player(scorekeeper, terrain_sprites)  # Creates the player
    generator = PlatformGenerator()

    sprites = pygame.sprite.Group()  # Creates the group of all sprites
    sprites.add(ground)  # Adds the first platform to the group
    sprites.add(player)  # Adds the player to the group
    key_listeners = pygame.sprite.Group()  # Group of sprites that listen to key events
    key_listeners.add(player)
    for p in generator.generate():
        terrain_sprites.add(p)
        sprites.add(p)
    controller = CameraController(player, terrain_sprites, [generator, scorekeeper])

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


        for entity in sprites:  # For every entity in the group
            displaysurface.blit(entity.surf, entity.rect)  # Displays the entity to the screen

        #TODO new display the scorekeeper, AFTER we display the sprites so it's on top
        scorekeeper.display()
        if player.rect.top > HEIGHT:
            end()

        pygame.display.update()  # Updates the screen
        frame_clock.tick(FPS)  # Sets the FPS


main()  # Runs the game
