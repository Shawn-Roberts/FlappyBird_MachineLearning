#!/usr/bin/python

# Author: Shawn Roberts
# Date: November 2021

# Python: 3.8.13

# IMPORTS
import pygame
import os,time
import random
pygame.font.init()
pygame.mixer.init()

# CONSTANTS
WINDOW_WIDTH = 576
WINDOW_HEIGHT = 1024
ITEM_VELOCITY = 10
PIPE_GAP = 300
BIRD_VELOCITY = -10
BASE_LEVEL = 930
BIRD_DEFAULT_X_POSTION = 230
BIRD_DEFAULT_Y_POSITION = 350
PIPE_DEFAULT_X_POSITION = 770
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird1.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird2.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird3.png')))]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','pipe.png')))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','background-day.png')))
GAME_OVER_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','gameover.png')))

SCORE_FONT = pygame.font.Font(os.path.join('fonts','04B_19.TTF'),60)
FLAP_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_wing.wav'))
HIT_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_hit.wav'))
DEATH_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_die.wav'))
SCORE_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_point.wav'))

# CLASSES
class Bird:
    BIRD_IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 120
        self.velocity = 0
        self.height = self.y
        self.image_count = 0
        self.image = self.BIRD_IMAGES[0]
    
    def flap(self):
        self.velocity = BIRD_VELOCITY
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # frame movement since last jump
        self.tick_count += 1

        # movmement of pixels per frame-develops arc movement
        displacement = self.velocity*(self.tick_count) + 0.5*(3)*(self.tick_count)**2
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2

        self.y = self.y +displacement
        # checks if bird position is moving upward or downward --for tilt
        if(displacement < 0 or self.y < self.height + 50):
            if(self.tilt < self.MAX_ROTATION): 
                self.tilt = self.MAX_ROTATION
        else:
            if(self.tilt > -90):
                self.tilt -= self.ROTATION_VELOCITY
    
    def draw(self,window):
        self.image_count += 1

        """Determines when it changes to a different bird image
        based off the draw. Basically just makes it flap by rotating 
        through the images
        """

        if self.image_count in range(0,5):
            self.image= self.BIRD_IMAGES[0]
        elif self.image_count in range(6, 10)or self.image_count in range (16,20):
            self.image = self.BIRD_IMAGES[1]
        elif self.image_count in range(11,15):
            self.image = self.BIRD_IMAGES[2]
        else:
            self.image = self.BIRD_IMAGES[0]
            self.image_count = 0

        if self.tilt <= -80:
            self.image = self.BIRD_IMAGES[1]
            self.image_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.image,self.tilt)
        rotated_rectangle = rotated_image.get_rect(center=self.image.get_rect(topleft = (self.x,self.y)).center)
        window.blit(rotated_image,rotated_rectangle.topleft)

    
    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class Pipe:
    GAP = PIPE_GAP
    VELOCITY = ITEM_VELOCITY

    def __init__(self,x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.pipe_passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def isPassed(self,pipe,bird):
        if bird.x > pipe.x + pipe.PIPE_TOP.get_width():
            return True
        else:
            return False
     
    def collide(self,bird):

        """ Using a mask vs a rectangle for collision detection 
            Looks at the pipes masks and the bird mask and figures out if they overlap
            https://www.pygame.org/docs/ref/mask.html
        """

        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask =pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        """collision returns array of overlapping pixels else returns None 
        if they are overlapping return true to mark a collision else false for no collision"""

        bottom_point_of_collisison = bird_mask.overlap(bottom_pipe_mask,bottom_offset)
        top_point_of_collisison = bird_mask.overlap(top_pipe_mask,top_offset)
        if (bottom_point_of_collisison or top_point_of_collisison):
            return True
        return False

class Base:
    VELOCITY =ITEM_VELOCITY
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # If image is fully off screen cycle it back to width
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self,window):
        window.blit(self.IMAGE, (self.x1, self.y))
        window.blit(self.IMAGE, (self.x2, self.y))

# FUNCTIONS
def getNewBird():
    return Bird(BIRD_DEFAULT_Y_POSITION,BIRD_DEFAULT_Y_POSITION)

def getNewPipe():
    return Pipe(PIPE_DEFAULT_X_POSITION)