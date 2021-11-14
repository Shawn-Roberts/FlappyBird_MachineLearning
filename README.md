# FlappyBird Machine Learning

Machine Learning Models (NEAT and Q Learning) that have been optimized to play the game Flappy Bird

# Requirements
- Developed to run in Python 3
- Environment must be setup to include pygame, numpy, matplotlib, graphviz, neat-python,pickle,

#Information
  -config-NEAT.txt is the file that drives the environment and settings of the NEAT algorithm. Heavily modified to suit environment
  - new models will be saved into the /AI/SavedModels folder with the naming convention genome_NEAT_Fitness{X}_Population{X}.pk1.

# Instructions
 - Calling from command line:
    -train -config: tells the script to train a new model. Will require an argurment for the number of genomes (iterations) the NEAT algorithm should take.
    - name: runs an existing model saved to the AI/SavedModels folder. Current model in there was able to complete 50 pipes before death after 10 genomes.
