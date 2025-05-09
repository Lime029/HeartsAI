
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
from scipy.stats import bernoulli
import pickle
from Player import Player
import copy 


class DQState:
    '''
    A game state at some time point t is defined as a single vector (3*52)
        - hand the agent currently holds before playing the trick
        - cards that the agent as seen in play before playing its own card
        - the current game object
    '''
    def __init__(self, hand : np.ndarray, cards_seen : np.ndarray, game : Game):
        self.hand = hand
        self.cards_seen = cards_seen
        self.game = game

class Memory:
    '''
    A memory is a single time point in the replay memory. A training memory needs
        - current State
        - reward recived for taking the action (as stored in the state)
        - the action the model took at current State. A one hot encoding of the card played
        - the next State after the agent takes the action
    '''
    def __init__(self, current_state : DQState, reward : float, action : list, next_state : DQState):
        self.current_state = current_state
        self.reward = reward
        self.action = action
        self.next_state = next_state

def generate_training_data(model : DQN, epoch : int) -> list:
    '''
    Play a bunch of games and store all of the model experiences as a list of memories.
    Training epoch 0 will use random agents, and all other training epochs will use self-play
    '''
    replay_memory = []
    map = Map()
    epsilon = 0.4

    for simulated_game in range (5000):
        game = Game(player_names=["Agent", "P1", "P2", "P3"], max_score=25, verbose=False)
        cards_seen = np.zeros(shape=(52))
        current_trick_cards = []
        # Loop for the entire game
        while len(game.current_player.hand) > 0:
            if game.current_player.name == 'Agent' or epoch > 0:
                # Note the agent's hand before playing the card
                hand = np.zeros(shape=(52))
                for card in game.current_player.hand:
                    index = map.get_index(rank=card.rank, suit=card.suit)
                    hand[index] = 1


                # Run the network to get a next action --> next card to play
                # Translate the network output to rank and suit
                best_card = []
                best_q_val = -np.inf
                for next_action in get_all_possible_next_actions(hand=hand, game=game, is_agent=False):
                    # For lack of a more creative name space...
                    meaningful_name = np.concatenate((hand, cards_seen, next_action), axis=None)
                    meaningful_name = T.from_numpy(meaningful_name)
                    q_val = model.forward(meaningful_name.float())
                    if q_val > best_q_val:
                        best_q_val = q_val
                        # Translate the next_action OHE to a Card object
                        for idx in range (len(next_action)):
                            if next_action[idx] == 1:
                                best_card = map.dict[idx + 1]
                # Now that we have the network's best move, we need to either 1)make that move or 2)make a random move
                # Determined by 1 - epsilon greedy exploration
                r = bernoulli.rvs(1 - epsilon)
                if r == 1:
                    card = Card(suit=best_card[1], rank=best_card[0])
                elif r == 0 or not game.is_valid_card(card):
                    # Random action
                    rand_card_index = random.randint(0, len(game.current_player.hand) - 1)
                    rand_card = game.current_player.hand[rand_card_index]
                    while not game.is_valid_card(rand_card):
                        rand_card_index = random.randint(0, len(game.current_player.hand) - 1)
                        rand_card = game.current_player.hand[rand_card_index]
                    card = rand_card

                if game.current_player.name == 'Agent':
                    # Convert the agent's next card to a OHE
                    ohe = np.zeros(shape=(52))
                    index = map.get_index(rank=card.rank, suit=card.suit)
                    ohe[index] = 1
                    agent_action = ohe

                
                    current_state = DQState(hand=hand, cards_seen=cards_seen, game=copy.deepcopy(game))
                    inital_score = game.players[0].score
                    
                    # Make the agent's next move
                    game.play_card(game.deck.get_card(rank=card.rank, suit=card.suit))

                    reward = inital_score - game.players[0].score
                    # Remove the card from the hand and set it as seen
                    for i in range(len(hand)):
                        if hand[i] == 1 and agent_action[i] == 1:
                            hand[i] = 0
                            cards_seen[i] = 1
                    next_state = DQState(hand=hand, cards_seen=cards_seen, game=copy.deepcopy(game))

                    # Create a Memory
                    memory = Memory(current_state=current_state, reward=-reward, action=agent_action, next_state=next_state)
                    replay_memory.append(memory)
                    
                else:
                    game.play_card(game.deck.get_card(rank=card.rank, suit=card.suit))

                # Add played card to current trick 
                current_trick_cards.append(card)

            elif epoch == 0: # Playing against random agent
                # Get a random card and submit to game object
                rand_card_index = random.randint(0, len(game.current_player.hand) - 1)
                rand_card = game.current_player.hand[rand_card_index]
                while not game.is_valid_card(rand_card):
                    rand_card_index = random.randint(0, len(game.current_player.hand) - 1)
                    rand_card = game.current_player.hand[rand_card_index]
                game.play_card(rand_card)

                # Mark the played card as having been played in this trick
                current_trick_cards.append(rand_card)

            # Check if the trick is over
            if len(game.trick) == 0:
                # Update the cards seen with all the cards played in the terminated trick
                for card in current_trick_cards:
                    index = map.get_index(rank=card.rank, suit=card.suit)
                    cards_seen[index] = 1
                # Reset 
                current_trick_cards = []
    '''if epoch == 0:
        filename = "random_replay_memory"
    else:
        filename = "replay_memory_" + epoch
    with open(filename, 'wb') as file:
        pickle.dump(replay_memory, file)
    print(f"List successfully pickled to '{filename}'")'''


    return replay_memory

def get_all_possible_next_actions(hand : list, game : Game, is_agent : bool) -> list:
    '''
    Returns a list of lists (actions) that contain all possible next actions from the input state
    '''
    # Check if we need to set the current player to the agent. (for training purposes)
    if is_agent:
        game.current_player = game.players[0]
    map = Map()
    next_actions = []
    for i in range (len(hand)):
        if hand[i] == 1:
            # We have this card. Need to check if it is a valid card --> we can play it
            rank = map.dict[i + 1][0]
            suit = map.dict[i + 1][1]
            if game.is_valid_card(card=Card(suit=suit, rank=rank)):
                next_action = np.zeros(shape=(52))
                next_action[i] = 1
                next_actions.append(next_action)
    return next_actions


def learn():
    # Constants:
    gamma = 0.9
    model = DQN()

    for epoch in range (10):
        # Zero the gradients
        print(f"Epoch = {epoch}")
        model.optimiser.zero_grad()

        # sample a minibatch of 1000 memories
        replay_memory = generate_training_data(model=model, epoch=epoch)
        '''with open("random_replay_memory", 'rb') as f:
           replay_memory = pickle.load(f)'''
        replay_memory = random.sample(replay_memory, 1000)

        # calculate the label for each sample 
        # label y = sample_reward + gamma * next_action_max_q_val
        # Need to enumerate all the possible next moves from a given state
        labels = []
        predictions = []
        for memory in replay_memory:

            max_a_q_val = None
            for next_action in get_all_possible_next_actions(hand=memory.next_state.hand, game=memory.next_state.game, is_agent=True):
                s = np.concatenate((memory.next_state.hand, memory.next_state.cards_seen, next_action), axis=None)
                s = T.from_numpy(s)
                pred_q_val = model.forward(state=s.float())
                if max_a_q_val == None or pred_q_val > max_a_q_val:
                    max_a_q_val = pred_q_val
            if max_a_q_val: # not a terminal current state
                labels.append(memory.reward + gamma * max_a_q_val)
            
                s = np.concatenate((memory.current_state.hand, memory.current_state.cards_seen, memory.action), axis=None)
                s = T.from_numpy(s)
                pred_q_val = model.forward(state=s.float())
                predictions.append(pred_q_val)
            


        # Backprop the loss
        labels = T.tensor(labels, dtype=T.float32)
        predictions = T.tensor(predictions, dtype=T.float32)
        loss = model.loss(labels, predictions).to(model.device)
        loss = loss.clamp(-1, 1) 
        loss.requires_grad = True
        loss.backward()
        model.optimiser.step() 
        print(f"Loss is {loss.item()}")


    with open('model', 'wb') as file:
        pickle.dump(model, file)
    print(f"Model successfully pickled")

if __name__ == "__main__":
    learn()
