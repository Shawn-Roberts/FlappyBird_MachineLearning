#!/usr/bin/python

# Author: Shawn Roberts
# Date: November 2021

# Python: 3.8.13

# IMPORTS
import pygame
from Lib import FlappyBirdLibrary

# FUNCTIONS
def draw_window(window,bird,pipes,base,score,session_high_score,game_active):
    """If game is active draw bird pipes and score, if not active just draw high school and background"""
    if(game_active):
        window.blit(FlappyBirdLibrary.BACKGROUND_IMAGE,(0,0))
        [pipe.draw(window) for pipe in pipes]
        bird.draw(window)
        base.draw(window)
        score_surface = FlappyBirdLibrary.SCORE_FONT.render(f'{int(score)}' ,True,(255,255,255))
        score_rect = score_surface.get_rect(center = (288,100))
        window.blit(score_surface,score_rect)
        pygame.display.update() 

    else:
        window.blit(FlappyBirdLibrary.BACKGROUND_IMAGE,(0,0))
        high_score_surface = FlappyBirdLibrary.SCORE_FONT.render(f'High score:{int(session_high_score)}' ,True,(255,255,255))
        high_score_rect = high_score_surface.get_rect(center = (288,100))
        window.blit(high_score_surface,high_score_rect)
        window.blit(FlappyBirdLibrary.GAME_OVER_IMAGE,(100,400))
        pygame.display.update()

def run_main_game():
    bird = FlappyBirdLibrary.getNewBird()
    base = FlappyBirdLibrary.Base(FlappyBirdLibrary.BASE_LEVEL)
    pipes = [FlappyBirdLibrary.getNewPipe()]
    window = pygame.display.set_mode([FlappyBirdLibrary.WINDOW_WIDTH,FlappyBirdLibrary.WINDOW_HEIGHT])
    clock = pygame.time.Clock()
    game_active = True
    score = 0
    session_high_score = 0

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.QUIT
                quit()
            if event.type == pygame.KEYDOWN and game_active == True:
                if event.key == pygame.K_SPACE:
                    bird.flap()  
                    FlappyBirdLibrary.FLAP_SOUND.play()
            if event.type == pygame.KEYDOWN and game_active == False:
                    bird = FlappyBirdLibrary.getNewBird()
                    pipes = [FlappyBirdLibrary.getNewPipe()]
                    game_active = True
                    score = 0
        
        if game_active:
            # Check if bird current y postion is above top of screen or below base and exit (loose if so)
            if bird.y + bird.image.get_height() >= FlappyBirdLibrary.BASE_LEVEL or bird.y  <= 0:
                FlappyBirdLibrary.HIT_SOUND.play()
                game_active = False

            for pipe in pipes:
                # check if any collissions first thing
                if(pipe.collide(bird)):
                    FlappyBirdLibrary.HIT_SOUND.play()
                    game_active = False 
                # remove any pipes off the screen
                [pipes.remove(pipe) if pipe.x + pipe.PIPE_TOP.get_width() < 0 else False for pipe in pipes]
                # If pipes not already marked as passed but the bird is passed the pipe update pipe, score, and create new pipe
                if not pipe.pipe_passed and pipe.isPassed(pipe,bird):
                    pipe.pipe_passed = True
                    FlappyBirdLibrary.SCORE_SOUND.play()
                    score +=1 
                    session_high_score = score if score > session_high_score else session_high_score
                    pipes.append(FlappyBirdLibrary.getNewPipe())      
                pipe.move()
            bird.move()
            base.move()  
        draw_window(window,bird,pipes,base,score,session_high_score,game_active)
 
# RUN
if __name__ == "__main__":
    run_main_game()
