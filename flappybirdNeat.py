#!/usr/bin/python

# Author: Shawn Roberts
# Date: November 2021

# Python: 3.8.13

# IMPORTS
import pygame
import argparse
import neat
import os
import pickle
from Lib import FlappyBirdLibrary

# CONSTANTS
PARSER = argparse.ArgumentParser(description="Lets play some flappy bird")
PARSER.add_argument('-train', action='store_true',help='Train a new model with NEAT use -config to pass additional argurments')
PARSER.add_argument('-config', default=[50], nargs=1, metavar=('genome count'),help="geonome count required (number of times to run model)")
PARSER.add_argument('-name', default="genome_NEAT_100F_100P.pk1",type=str,nargs=1,help="name of model to run default is 100 fitness 100 population TAN H function")
WINDOW = pygame.display.set_mode((FlappyBirdLibrary.WINDOW_WIDTH, FlappyBirdLibrary.WINDOW_HEIGHT))
DRAW_LINES = True


# RUNNERS
def create_new_neat_model(config_path,genome_count):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    winner = population.run(main_game,int(genome_count))
    with open(f'AI/SavedModels/genome_NEAT_Fitness{5000}_Population{50}.pk1','wb') as file:
        pickle.dump(winner,file)
        file.close()

def load_existing_neat_model(config_path,model_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    with open(model_path,'rb') as file:
        genome = pickle.load(file)
        genomes = [(1,genome)]
        main_game(genomes,config)
    file.close()

# GAME FUNCTIONS
def draw_window(window, birds, pipes, base, score, pipe_index):
    window.blit(FlappyBirdLibrary.BACKGROUND_IMAGE, (0,0))
    [pipe.draw(window) for pipe in pipes]
    base.draw(window)
    for bird in birds:
        if DRAW_LINES:
            try:
                # draws lines to top and bottom and top
                pygame.draw.line(window, (255,0,0), (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_TOP.get_width()/2, pipes[pipe_index].height), 5)
                pygame.draw.line(window, (255,0,0), (bird.x+bird.image.get_width()/2, bird.y + bird.image.get_height()/2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_BOTTOM.get_width()/2, pipes[pipe_index].bottom), 5)
            except Exception as e:
                pass
        bird.draw(window)

    birds_label = FlappyBirdLibrary.SCORE_FONT.render("LEFT: "  + str(len(birds)),1,(255,255,255))
    window.blit(birds_label, (FlappyBirdLibrary.WINDOW_WIDTH - birds_label.get_width() - 330, 10))

    score_label = FlappyBirdLibrary.SCORE_FONT.render("Score: " + str(score),1,(255,255,255))
    window.blit(score_label, (FlappyBirdLibrary.WINDOW_WIDTH - score_label.get_width() - 15, 10))
    pygame.display.update()

def remove_bird_from_data(active_genome_list,active_networks_list,active_birds_list,bird):
    active_genome_list[active_birds_list.index(bird)].fitness -= 1
    active_networks_list.pop(active_birds_list.index(bird))
    active_genome_list.pop(active_birds_list.index(bird))
    active_birds_list.pop(active_birds_list.index(bird))

# MAIN GAME LOOP
def main_game(genomes,config):
    active_networks_list = []
    active_genome_list = []
    active_birds_list = []
    base = FlappyBirdLibrary.Base(930)
    pipes = [FlappyBirdLibrary.Pipe(600)]
    window = pygame.display.set_mode([FlappyBirdLibrary.WINDOW_WIDTH,FlappyBirdLibrary.WINDOW_HEIGHT])
    clock = pygame.time.Clock()
    score = 0
    game_active = True

    
    for genome_id, genome in genomes:
        genome.fitness = 0  
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        active_networks_list.append(net)
        active_birds_list.append(FlappyBirdLibrary.Bird(230,350))
        active_genome_list.append(genome)

    while game_active:
        clock.tick(50)
        upcoming_pipe_index = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.QUIT
                    quit() 

        if len(active_birds_list) > 0 and len(pipes) > 0:
            upcoming_pipe_index = 1 if pipes[0].isPassed(pipes[0],active_birds_list[0]) else 0
        else:
            game_active = False
            break

        for index,bird in enumerate(active_birds_list):
            bird.move()
            active_genome_list[index].fitness += 1
            # let the network associated to the current bird decide what to do next based on these inputs
            print(f"BIRD Y AND HEIGHT: {abs(bird.y - pipes[upcoming_pipe_index].height)} ")
            print(f" BIRD Y AND BOTTOM PIPE  {abs(bird.y - pipes[upcoming_pipe_index].bottom)}")
            output = active_networks_list[active_birds_list.index(bird)].activate((bird.y, abs(bird.y - pipes[upcoming_pipe_index].height), abs(bird.y - pipes[upcoming_pipe_index].bottom)))

            if output[0] > 0.5:
                bird.flap()

        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in active_birds_list:
                if pipe.collide(bird):
                    remove_bird_from_data(active_genome_list,active_networks_list,active_birds_list,bird)
            
            if not pipe.pipe_passed and pipe.x < bird.x:
                pipe.pipe_passed = True
                score += 1
                for genome in active_genome_list:
                    genome.fitness += 10
                pipes.append(FlappyBirdLibrary.Pipe(700))

        [pipes.remove(pipe) if pipe.x + pipe.PIPE_TOP.get_width() < 0 else False for pipe in pipes]
    
        for index,bird in enumerate(active_birds_list):
            if bird.y + bird.image.get_height() - 10 >= FlappyBirdLibrary.BASE_LEVEL or bird.y < 0:
                active_genome_list[index].fitness -= 20
                remove_bird_from_data(active_genome_list,active_networks_list,active_birds_list,bird)

        draw_window(window,active_birds_list, pipes, base, score,upcoming_pipe_index)


    
# RUN
if __name__ == "__main__":
    args = PARSER.parse_args()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'AI','config-NEAT.txt')

    # Train new model
    if(args.train):
        genome_count = args.config[0]
        create_new_neat_model(config_path,genome_count)

    #Run existing model 
    else:
        model_path = os.path.join(local_dir,'AI',args.name[0])
        if(os.path.exists(model_path)):
            load_existing_neat_model(config_path,model_path) 
        else:
            print("Error model does not exist")


        
