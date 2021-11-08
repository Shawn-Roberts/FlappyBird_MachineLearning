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

# CONSTANTS
PARSER = argparse.ArgumentParser(description="Lets play some flappy bird")
PARSER.add_argument('-train', action='store_true',help='Train a new model with NEAT use -config to pass additional argurments')
PARSER.add_argument('-config', default=[100,100,50], nargs=3, metavar=('fitness bound','pop','genome count'),help="3 argurments required upper fitness bound, population, geonome count")
PARSER.add_argument('-name', default="genome_NEAT_100F_100P.pk1",type=str,nargs=1,help="name of model to run default is 100 fitness 100 population TAN H function")

# FUNCTIONS
def create_new_neat_model(config_path):
    print("HI")


def load_existing_neat_model(config_path,model_name):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    with open(f'AI/{model_name}','wb') as file:
        genome = pickle.load(f)
        genomes = [(1,genome)]
        main_game_load_model(genomes,config)
    file.close()


def main_game_create_model(config):
    print("DO STUFF")


def main_game_load_model(genomes,config):
    print("DO STUFF")


# RUN
if __name__ == "__main__":
    args = PARSER.parse_args()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'AI','config-NEAT.txt')
    if(args.train):
        fitness_bound = args.config[0]
        population_size = args.config[1]
        genome_count = args.config[2]
        create_new_neat_model(config_path)
        
    else:
        existing_model_name = args.name 
        load_existing_neat_model(config_path,existing_model_name)  
        
