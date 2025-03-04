
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from model import DQN
import numpy as np
from Game import Game
import random


class State:
    '''
    A game state at some time point t is defined as a single vector (1 x (3*52))
        - hand the agent currently holds
        - cards that the agent as seen in play
        - the next card that the agent intends to play (the action)
    All will be represented as a one hot encoding
    '''
    def __init__(self, hand : np.ndarray, cards_seen : np.ndarray, next_action : np.ndarray):
        self.hand = hand
        self.cards_seen = cards_seen
        self.next_action = next_action
    
    def get_state(self):
        return np.concatenate(self.hand, self.cards_seen, self.next_action)

class Memory:
    '''
    A memory is a single time point in the replay memory. A training memory needs
        - current State
        - reward recived for taking the action (as stored in the state)
        - next state (as a result of taking the action)
        - a flag denoting whether or not the current state is a terminal state
    If the current state is terminal (terminal_flag=True), then next_state=Null
    '''
    def __init__(self, current_state : State, reward : float, next_state : State, terminal_flag : bool):
        self.current_state = current_state
        self.reward = reward
        self.next_state = next_state
        self.terminal_flag = terminal_flag


def generate_training_data(model : DQN) -> list:
    '''
    Play a bunch of games and store all of the model experiences as a list of memories
    '''
    for simulated_game in range (5000):
        game = Game(["Agent", "P1", "P2", "P3"])
        # Loop for the entire game
        while len(game.current_player.hand) > 0:
            inital_score = game.players[0].score

            if game.current_player.name == 'Agent':
                # Run the network to get a next action --> next card to play
                # Translate the network output to rank and suit
                game.play_card(game.deck.get_card(rank="", suit=""))
            else:
                # Get a random card and submit to game object
                rand_card_index = random.randint(0, len(game.current_player.hand))
                rand_card = game.current_player.hand[rand_card_index]
                while not game.is_valid_card(rand_card):
                    rand_card_index = random.randint(0, len(game.current_player.hand))
                    rand_card = game.current_player.hand[rand_card_index]
                game.play_card(rand_card)

            # Check if the trick is over and create a Memory
            if len(game.trick) == 0:
                reward = game.players[0].score - inital_score
        game.play_card()
        


    
        
