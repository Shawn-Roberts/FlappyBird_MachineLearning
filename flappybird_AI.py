#!/usr/bin/python

# Author: Shawn Roberts
# Date: November 2021

# Python: 3.8.13

# IMPORTS
import pygame
from pygame.constants import QUIT
import flappybird
import os,sys
import neat

# CONSTANTS
DRAW_LINES = True
WINDOW = pygame.display.set_mode((flappybird.WIN_WIDTH, flappybird.WIN_HEIGHT))
GENERATION = 0

def draw_window(win, birds, pipes, base, score, pipe_ind):

    # if generation == 0:
    #     gen = 1
    win.blit(flappybird.BACKGROUND_IMAGE, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except Exception as e:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = flappybird.SCORE_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (flappybird.WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label =  flappybird.SCORE_FONT.render("Gens: " + str(GENERATION),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # # alive
    # score_label =  flappybird.SCORE_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    # win.blit(score_label, (10, 50))

    pygame.display.update()


def main_game_AI(genomes,config):
    global GENERATION
    GENERATION += 1
    nets = []
    ge = []
    birds = []
    
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(flappybird.Bird(230,350))
        ge.append(genome)

    base = flappybird.Base(930)
    pipes = [flappybird.Pipe(600)]
    window = pygame.display.set_mode([flappybird.WIN_WIDTH,flappybird.WIN_HEIGHT])
    clock = pygame.time.Clock()

    score = 0
    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.QUIT
                    quit() 

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): 
                pipe_index = 1   
        else:
            run = False
            break

        for x,bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.flap()
        base.move()

            
        add_pipe = False
        remove = []

        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            if not pipe.pipe_passed and pipe.x < bird.x:
                pipe.pipe_passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(flappybird.Pipe(700))

        for r in remove:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.image.get_height() - 10 >= 930 or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        
        draw_window(window,birds, pipes, base, score,pipe_index)
    

def run_thing(config):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    winner = population.run(main_game_AI,50)


# RUN
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"AI","config-NEAT.txt")
    run_thing(config_path)
