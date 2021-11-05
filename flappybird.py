#!/usr/bin/python

# Author: Shawn Roberts
# Date: November 2021

# Python: 3.8.13

# IMPORTS
import pygame
import os,time
import random

from pygame.image import tostring
pygame.font.init()
pygame.mixer.init()

# CONSTANTS
WIN_WIDTH = 576
WIN_HEIGHT = 1024
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird1.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird2.png'))),
            pygame.transform.scale2x(pygame.image.load(os.path.join('assets','bird3.png')))]

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','pipe.png')))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets','background-day.png')))

SCORE_FONT = pygame.font.Font(os.path.join('fonts','04B_19.TTF'),60)

FLAP_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_wing.wav'))
DEATH_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_hit.wav'))
SCORE_SOUND = pygame.mixer.Sound(os.path.join('sound','sfx_point.wav'))

# GAME VARIABLES

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
        # goes upward
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        # frame movement since last jump
        self.tick_count += 1
        # movmement of pixels per frame-develops arc movement
        displacement = self.velocity*(self.tick_count) + 0.5*(3)*(self.tick_count)**2
        if displacement >= 16:
            # terminal velocity
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
        if self.image_count <= self.ANIMATION_TIME:
            self.image= self.BIRD_IMAGES[0]
        elif self.image_count <= self.ANIMATION_TIME*2:
            self.image = self.BIRD_IMAGES[1]
        elif self.image_count <= self.ANIMATION_TIME*3:
            self.image = self.BIRD_IMAGES[2]
        elif self.image_count <= self.ANIMATION_TIME*4:
            self.image = self.BIRD_IMAGES[1]
        elif self.image_count == self.ANIMATION_TIME*4 + 1:
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
    GAP = 200
    VELOCITY = 5

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
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
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

        """if collision returns array of overlapping pixels else returns None 
        if they are overlapping return true to mark a collision else false for no collision"""

        bottom_point_of_collisison = bird_mask.overlap(bottom_pipe_mask,bottom_offset)
        top_point_of_collisison = bird_mask.overlap(top_pipe_mask,top_offset)
        if (bottom_point_of_collisison or top_point_of_collisison):
            return True
        return False

class Base:
    VELOCITY = 5
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self,y):
        #X position changes not y
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
        # draw first image
        window.blit(self.IMAGE, (self.x1, self.y))
        # draw second image
        window.blit(self.IMAGE, (self.x2, self.y))



# FUNCTIONS
def draw_window(window,bird,pipes,base,score):
    window.blit(BACKGROUND_IMAGE,(0,0))
    [pipe.draw(window) for pipe in pipes]
    bird.draw(window)
    base.draw(window)
    score_surface = SCORE_FONT.render(f'{int(score)}' ,True,(255,255,255))
    score_rect = score_surface.get_rect(center = (288,100))
    window.blit(score_surface,score_rect)
    pygame.display.update()

def main_game():
    bird = Bird(230,350)
    base = Base(930)
    pipes = [Pipe(700)]
    continue_game = True
    score = 0
    window = pygame.display.set_mode([WIN_WIDTH,WIN_HEIGHT])
    clock = pygame.time.Clock()

    while continue_game:
        clock.tick(30)
        add_pipe = False
        remove_pipes = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue_game = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.move()
                    FLAP_SOUND.play()
        # CLEAN UP 
        for pipe in pipes:
            # if(pipe.collide(bird)):
                # DEATH_SOUND.play()
                # print("COLLISSION")
            [pipes.remove(pipe) if pipe.pipe_passed and pipe.x +pipe.PIPE_TOP.get_width() < 0 else False for pipe in pipes]
            # if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            #     pipes.remove(pipe)
            print(len(pipes))
            if not pipe.pipe_passed and pipe.x < bird.x:
                """Update pipe passed to true, add score, and create new pipe"""
                pipe.pipe_passed = True
                score += 1
                SCORE_SOUND.play()
                pipes.append(Pipe(700))
            pipe.move()
        # if bird.y + bird.image.get_height() >= 930 or bird.y + bird.image.get_height() <= 0:
            # DEATH_SOUND.play()
            # print("HIT FLOOR/ ROOF")

        base.move()  
        draw_window(window,bird,pipes,base,score)
    pygame.quit()
                

# RUN
if __name__ == "__main__":
    main_game()