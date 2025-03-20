
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from model import DQN
import numpy as np
from Game import Game
import random
from Map import Map
from Card import Card


class State:
    '''
    A game state at some time point t is defined as a single vector (3*52)
        - hand the agent currently holds before playing the trick
        - cards that the agent as seen in play before playing its own card
        - the next card that the agent intends to play in this trick
    All will be represented as a one hot encoding
    '''
    def __init__(self, hand : np.ndarray, cards_seen : np.ndarray, next_action : np.ndarray, game : Game):
        self.hand = hand
        self.cards_seen = cards_seen
        self.next_action = next_action
        self.game = game

class Memory:
    '''
    A memory is a single time point in the replay memory. A training memory needs
        - current State
        - reward recived for taking the action (as stored in the state)
    If the current state is terminal (terminal_flag=True), then next_state=Null
    '''
    def __init__(self, current_state : State, reward : float):
        self.current_state = current_state
        self.reward = reward


def generate_training_data(model : DQN) -> list:
    '''
    Play a bunch of games and store all of the model experiences as a list of memories
    '''
    replay_memory = []
    map = Map()

    for simulated_game in range (5000):
        game = Game(["Agent", "P1", "P2", "P3"])
        cards_seen = np.zeros(shape=(1,52))
        current_trick_cards = []
        # Loop for the entire game
        while len(game.current_player.hand) > 0:
            inital_score = game.players[0].score
            if game.current_player.name == 'Agent':
                # Note the agent's hand before playing the card
                hand = np.zeros(shape=(1,52))
                for card in game.players[0].hand:
                    index = map.get_index(rank=card.rank, suit=card.suit)
                    hand[index] = 1


                # Run the network to get a next action --> next card to play
                # Translate the network output to rank and suit
                # card = agent.chosen_card
                game.play_card(game.deck.get_card(rank=card.rank, suit=card.suit))


                # Mark the played card as the next_action
                index = map.get_index(rank=card.rank, suit=card.suit)
                next_state = np.zeros(shape=(1,52))
                next_state[index] = 1

                # Add played card to current trick 
                current_trick_cards.append(card)
            else:
                # Get a random card and submit to game object
                rand_card_index = random.randint(0, len(game.current_player.hand))
                rand_card = game.current_player.hand[rand_card_index]
                while not game.is_valid_card(rand_card):
                    rand_card_index = random.randint(0, len(game.current_player.hand))
                    rand_card = game.current_player.hand[rand_card_index]
                game.play_card(rand_card)

                # Mark the played card as having been played in this trick
                current_trick_cards.append(card)

            # Check if the trick is over and create a Memory
            if len(game.trick) == 0:
                # Calculate the necessary information for memory
                reward = game.players[0].score - inital_score
                current_state = State(hand=hand, cards_seen=cards_seen, next_action=next_state, game=game)
                memory = Memory(current_state, reward)
                replay_memory.append(memory)

                # Update the cards seen with all the cards played in the terminated trick
                for card in current_trick_cards:
                    index = map.get_index(rank=rand_card.rank, suit=rand_card.suit)
                    cards_seen[index] = 1
                # Reset 
                current_trick_cards = []
    return replay_memory

def get_all_possible_actions(state : State):
    state.game.current_player = "Agent"
    map = Map()
    next_actions = []
    for i in range (len(state.hand)):
        if state.hand[i] == 1:
            # We have this card. Need to check if it is a valid card
            rank = map.dict[i][0]
            suit = map.dict[i][1]
            if state.game.is_valid_card(card=Card(suit=suit, rank=rank)):
                action = np.zeros(shape=(52))
                action[i] = 1
                next_actions.append(action)
    return next_actions


def learn():
    # Constants:
    gamma = 0.001
    model = DQN()
    for _ in range (10):
        # Zero the gradients
        model.Q_network.optimiser.zero_grad()

        # sample a minibatch of 1000 memories
        replay_memory = generate_training_data(model=model)
        replay_memory = random.sample(replay_memory, 1000)

        # calculate the label for each sample 
        # label y = sample_reward + gamma * next_action_max_q_val
        # Need to enumerate all the possible next moves from a given state
        labels = []
        predictions = []
        for memory in replay_memory:
            reward = memory.reward
            state = memory.state
            for next_action in get_all_possible_actions(state):
                q_val = model.forward(next_action) # Assuming q_val is a vector of probabilities
                y = reward + gamma * max(q_val)
                labels.append(y)
                predictions.append(max(q_val))
            
        # Compute MSE for all the m samples 
        # MSE = 1/m * [sum i = 1 --> m : (Q_i - y_i) ^ 2]
        #squared_errors = [(y_true - y_pred) ** 2 for y_true, y_pred in zip(labels, predictions)]
        #mse = sum(squared_errors) / len(squared_errors)

        # Backprop the loss
        loss = model.Q_network.loss(labels, predictions).to(model.Q_network.device)
        loss = loss.clamp(-1, 1)
        loss.backward()
        model.Q_network.optimiser.step()



                
        


    
        
