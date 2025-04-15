from Game import Game
from Card import Card
from State import State
from ISMCTS import ISMCTS

from model import DQN
from DQ_Agent import get_all_possible_next_actions
from scipy.stats import bernoulli
import torch as T
from Map import Map

import pandas as pd
import random
import numpy as np
from tqdm import tqdm
import argparse
class Random_Player():
    def __init__(self, game: Game, player_idx=0, iters=50, verbose=False):
        self.__game = game

    def run(self):
        return self.__game.random_legal_move()
    
    def new_game(self, game):
        self.__game = game
class ISMCTS_Player():
    def __init__(self, game: Game, player_idx=0, iters=50, verbose=False):
        self.__game = game
        self.__game_verbosity = game.verbose
        self.__ismcts = ISMCTS(player_idx)
        self.__iters = iters
        self.__verbose = verbose

    def run(self):
        # Temporarily turn off game verbosity as MCTS runs
        self.__game.verbosity = False
        temp = self.__ismcts.run(State(self.__game), self.__iters, verbose=self.__verbose)
        self.__game.verbosity = self.__game_verbosity
        return temp
    
    def new_game(self, game):
        self.__game = game

class DQN_Player():
    def __init__(self, game: Game, player_idx=0, iters=50, verbose=False):
        self.__model = DQN()
        self.__cards_seen = np.zeros(shape=(52))
        self.__current_trick_cards = []
        self.__game = game
        self.__hand = []
        self.__map = Map()
        self.epsilon = 0.4

    def __set_hand(self):
        self.__hand = np.zeros(shape=(52))
        for card in self.__game.current_player.hand:
            index = self.__map.get_index(rank=card.rank, suit=card.suit)
            self.__hand[index] = 1  

    def new_game(self, game):
        self.__game = game
        self.__hand = []
        self.__cards_seen = np.zeros(shape=(52))
        self.__current_trick_cards = []


    def run(self):
        # Note the agent's hand before playing the card
        self.__set_hand()
        # Run the network to get a next action --> next card to play
        # Translate the network output to rank and suit
        best_card = []
        best_q_val = -np.inf
        for next_action in get_all_possible_next_actions(hand=self.__hand, game=self.__game, is_agent=False):
            # For lack of a more creative name space...
            meaningful_name = np.concatenate((self.__hand, self.__cards_seen, next_action), axis=None)
            meaningful_name = T.from_numpy(meaningful_name)
            q_val = self.__model.forward(meaningful_name.float())
            if q_val > best_q_val:
                best_q_val = q_val
                # Translate the next_action OHE to a Card object
                for idx in range (len(next_action)):
                    if next_action[idx] == 1:
                        best_card = self.__map.dict[idx + 1]
        # Now that we have the network's best move, we need to either 1)make that move or 2)make a random move
        # Determined by 1 - epsilon greedy exploration
        r = bernoulli.rvs(1 - self.epsilon)
        if r == 1:
            card = Card(suit=best_card[1], rank=best_card[0])
        elif r == 0 or not self.__game.is_valid_card(card):
            # Random action
            card = self.__game.random_legal_move()
            
        # Convert the agent's next card to a OHE
        ohe = np.zeros(shape=(52))
        index = self.__map.get_index(rank=card.rank, suit=card.suit)
        ohe[index] = 1
        agent_action = ohe
        
        # Make the agent's next move
        # self.__game.play_card(self.__game.deck.get_card(rank=card.rank, suit=card.suit))

        # Remove the card from the hand and set it as seen
        for i in range(len(self.__hand)):
            if self.__hand[i] == 1 and agent_action[i] == 1:
                self.__hand[i] = 0
                self.__cards_seen[i] = 1

        # Add played card to current trick 
        self.__current_trick_cards.append(card)

        # Check if the trick is over
        if len(self.__game.trick) == 0:
            # Update the cards seen with all the cards played in the terminated trick
            for card in self.__current_trick_cards:
                index = self.__map.get_index(rank=card.rank, suit=card.suit)
                self.__cards_seen[index] = 1
            # Reset 
            self.current_trick_cards = []
        return card

def ISMCTS_vs_RandomAgent(num_games=10, iters=100, max_score=50):
    """
    Run 1000 simulations of the game and save them in a dataframe.
    """

    rows = []
    ismcts_wins = 0
    ismcts_rwins = 0
    random2_wins = 0
    random2_rwins = 0
    random3_wins = 0
    random3_rwins = 0
    random4_wins = 0
    random4_rwins = 0
    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["Rachel", "Meal", "Shraf", "Simi"], max_score=max_score, verbose=False)

        # Evaluate ISMCTS against random agents
        ismcts_player = ISMCTS_Player(player_idx=0, game=game, iters=iters);
        random_player = Random_Player(game)
        players = [ismcts_player, random_player, random_player, random_player]
        last_round = 0
        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                player_round_score = round_scores[0]
                unsorted_scores = round_scores
                round_scores = sorted(round_scores, reverse=True)
                # If the player won this round, increment the number of rounds wons
                if round_scores[-1] == player_round_score:
                    ismcts_rwins = ismcts_rwins + 1

                if round_scores[-1] == random2_rwins:
                    random2_rwins = random2_rwins + 1

                if round_scores[-1] == random3_rwins:
                    random3_rwins = random3_rwins + 1

                if round_scores[-1] == random4_rwins:
                    random4_rwins = random4_rwins + 1
                rows.append({"player": "ISMCTS", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": player_round_score, "placement": round_scores.index(player_round_score), "round_wins": ismcts_rwins, "game_wins": ismcts_wins, "last_trick": False})
                rows.append({"player": "Random2", "game": i, "round": game.round, "current_score": game.players[1].score, "round_score": unsorted_scores[1], "placement": round_scores.index(unsorted_scores[1]), "round_wins": random2_rwins, "game_wins": random2_wins, "last_trick": False})
                rows.append({"player": "Random3", "game": i, "round": game.round, "current_score": game.players[2].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[2]), "round_wins": random3_rwins, "game_wins": random3_wins, "last_trick": False})
                rows.append({"player": "Random4", "game": i, "round": game.round, "current_score": game.players[3].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[3]), "round_wins": random4_rwins, "game_wins": random4_wins, "last_trick": False})
                
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-4]['last_trick'] = True
                    rows[-3]['last_trick'] = True
                    rows[-2]['last_trick'] = True
                    rows[-1]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        ismcts_wins = ismcts_wins + 1
                        rows[-4]['game_wins'] = ismcts_wins

                    if min([player.score for player in game.players]) == game.players[1].score:
                        random2_wins = random2_wins + 1
                        rows[-2]['game_wins'] = random2_wins

                    if min([player.score for player in game.players]) == game.players[2].score:
                        random3_wins = random3_wins + 1
                        rows[-1]['game_wins'] = random3_wins

                    if min([player.score for player in game.players]) == game.players[3].score:
                        random4_wins = random4_wins + 1
                        rows[-1]['game_wins'] = random4_wins

                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("ISMCTS_vs_Random.csv", index=False)
    return df

def DQN_vs_RandomAgent(num_games=10, max_score=50):
    """
    Run 1000 simulations of the game and save them in a dataframe.
    """

    rows = []
    dqn_wins = 0
    dqn_rwins = 0
    random2_wins = 0
    random2_rwins = 0
    random3_wins = 0
    random3_rwins = 0
    random4_wins = 0
    random4_rwins = 0

    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["Rachel", "Meal", "Shraf", "Simi"], max_score=max_score, verbose=False)

        # Evaluate dqn against random agents
        dqn_player = DQN_Player(game=game);
        random_player = Random_Player(game)
        players = [dqn_player, random_player, random_player, random_player]
        last_round = 0
        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                print(round_scores)
                player_round_score = round_scores[0]
                unsorted_scores = round_scores
                round_scores = sorted(round_scores, reverse=True)
                # If the player won this round, increment the number of rounds wons
                if round_scores[-1] == player_round_score:
                    dqn_rwins = dqn_rwins + 1
                    
                if round_scores[-1] == random2_rwins:
                    random2_rwins = random2_rwins + 1

                if round_scores[-1] == random3_rwins:
                    random3_rwins = random3_rwins + 1

                if round_scores[-1] == random4_rwins:
                    random4_rwins = random4_rwins + 1
                rows.append({"player": "DQN", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": player_round_score, "placement": round_scores.index(player_round_score), "round_wins": dqn_rwins, "game_wins": dqn_wins, "last_trick": False})
                rows.append({"player": "Random2", "game": i, "round": game.round, "current_score": game.players[1].score, "round_score": unsorted_scores[1], "placement": round_scores.index(unsorted_scores[1]), "round_wins": random2_rwins, "game_wins": random2_wins, "last_trick": False})
                rows.append({"player": "Random3", "game": i, "round": game.round, "current_score": game.players[2].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[2]), "round_wins": random3_rwins, "game_wins": random3_wins, "last_trick": False})
                rows.append({"player": "Random4", "game": i, "round": game.round, "current_score": game.players[3].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[3]), "round_wins": random4_rwins, "game_wins": random4_wins, "last_trick": False})
                
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-4]['last_trick'] = True
                    rows[-3]['last_trick'] = True
                    rows[-2]['last_trick'] = True
                    rows[-1]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        dqn_wins = dqn_wins + 1
                        rows[-2]['game_wins'] = dqn_wins
                    if min([player.score for player in game.players]) == game.players[1].score:
                        random2_wins = random2_wins + 1
                        rows[-2]['game_wins'] = random2_wins

                    if min([player.score for player in game.players]) == game.players[2].score:
                        random3_wins = random3_wins + 1
                        rows[-1]['game_wins'] = random3_wins

                    if min([player.score for player in game.players]) == game.players[3].score:
                        random4_wins = random4_wins + 1
                        rows[-1]['game_wins'] = random4_wins
          
                dqn_player.__cards_seen = np.zeros(shape=(52))
                dqn_player.__current_trick_cards = []
                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("DQN_vs_Random.csv", index=False)
    return df

def DQN_vs_ISMCTS(num_games=10, iters=100, max_score=50):
    """
    Run 1000 simulations of the game and save them in a dataframe.
    """
    rows = []
    dqn_wins = 0
    dqn_rwins = 0
    ismcts_wins = 0
    ismcts_rwins = 0

    random1_wins = 0
    random1_rwins = 0
    random2_wins = 0
    random2_rwins = 0
    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["ISMCTS", "DQN", "R1", "R2"], max_score=max_score, verbose=False)

        # Evaluate dqn against random agents
        ismcts_player = ISMCTS_Player(player_idx=0, game=game, iters=iters);
        dqn_player = DQN_Player(game=game);
        random_player = Random_Player(game)
        players = [ismcts_player, dqn_player, random_player, random_player]
        last_round = 0

        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                ismcts_round_score = round_scores[0]
                dqn_round_score = round_scores[1]
                unsorted_scores = round_scores

                # Round scores ordered from largest to smallest
                round_scores = sorted(round_scores, reverse=True)
                # If the player won this round, increment the number of rounds wons
                # A player won if the had the smallest (last in list) score
                if round_scores[-1] == ismcts_round_score:
                    ismcts_rwins = ismcts_rwins + 1
                if round_scores[-1] == dqn_round_score:
                    dqn_rwins = dqn_rwins + 1

                if round_scores[-1] == random3_rwins:
                    random3_rwins = random3_rwins + 1

                if round_scores[-1] == random4_rwins:
                    random4_rwins = random4_rwins + 1
                rows.append({"player": "ISMCTS", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": ismcts_round_score, "placement": round_scores.index(ismcts_round_score), "round_wins": ismcts_rwins, "game_wins": ismcts_wins, "last_trick": False})
                rows.append({"player": "DQN", "game": i, "round": game.round, "current_score": game.players[1].score, "round_score": dqn_round_score, "placement": round_scores.index(dqn_round_score), "round_wins": dqn_rwins, "game_wins": dqn_wins, "last_trick": False})
                rows.append({"player": "Random3", "game": i, "round": game.round, "current_score": game.players[2].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[2]), "round_wins": random3_rwins, "game_wins": random3_wins, "last_trick": False})
                rows.append({"player": "Random4", "game": i, "round": game.round, "current_score": game.players[3].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[3]), "round_wins": random4_rwins, "game_wins": random4_wins, "last_trick": False})
                
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-1]['last_trick'] = True
                    rows[-2]['last_trick'] = True
                    rows[-3]['last_trick'] = True
                    rows[-4]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        ismcts_wins = ismcts_wins + 1
                        rows[-4]['game_wins'] = ismcts_wins

                    if min([player.score for player in game.players]) == game.players[1].score:
                        dqn_wins = dqn_wins + 1
                        rows[-3]['game_wins'] = dqn_wins

                    if min([player.score for player in game.players]) == game.players[2].score:
                        random3_wins = random3_wins + 1
                        rows[-1]['game_wins'] = random3_wins

                    if min([player.score for player in game.players]) == game.players[3].score:
                        random4_wins = random4_wins + 1
                        rows[-1]['game_wins'] = random4_wins

                dqn_player.__cards_seen = np.zeros(shape=(52))
                dqn_player.__current_trick_cards = []
                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("DQN_vs_Random.csv", index=False)
    return df

def RandomAgent_vs_RandomAgent(num_games=10, max_score=50):
    rows = []
    random1_wins = 0
    random1_rwins = 0
    random2_wins = 0
    random2_rwins = 0
    random3_wins = 0
    random3_rwins = 0
    random4_wins = 0
    random4_rwins = 0
    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["Rachel", "Meal", "Shraf", "Simi"], max_score=max_score, verbose=False)
        for p in players:
            p.new_game(game)

        # Evaluate random against random agents for a baseline
        random_player = Random_Player(game)
        players = [random_player, random_player, random_player, random_player]
        last_round = 0
        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                unsorted_scores = round_scores
                round_scores = sorted(round_scores, reverse=True)

                # If the player won this round, increment the number of rounds wons
                if round_scores[-1] == random1_rwins:
                    random1_rwins = random1_rwins + 1

                if round_scores[-1] == random2_rwins:
                    random2_rwins = random2_rwins + 1

                if round_scores[-1] == random3_rwins:
                    random3_rwins = random3_rwins + 1

                if round_scores[-1] == random4_rwins:
                    random4_rwins = random4_rwins + 1
                rows.append({"player": "Random1", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": unsorted_scores[0], "placement": round_scores.index(unsorted_scores[0]), "round_wins": random1_rwins, "game_wins": random1_wins, "last_trick": False})
                rows.append({"player": "Random2", "game": i, "round": game.round, "current_score": game.players[1].score, "round_score": unsorted_scores[1], "placement": round_scores.index(unsorted_scores[1]), "round_wins": random2_rwins, "game_wins": random2_wins, "last_trick": False})
                rows.append({"player": "Random3", "game": i, "round": game.round, "current_score": game.players[2].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[2]), "round_wins": random3_rwins, "game_wins": random3_wins, "last_trick": False})
                rows.append({"player": "Random4", "game": i, "round": game.round, "current_score": game.players[3].score, "round_score": unsorted_scores[2], "placement": round_scores.index(unsorted_scores[3]), "round_wins": random4_rwins, "game_wins": random4_wins, "last_trick": False})
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-4]['last_trick'] = True
                    rows[-3]['last_trick'] = True
                    rows[-2]['last_trick'] = True
                    rows[-1]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        random1_wins = random1_wins + 1
                        rows[-4]['game_wins'] = random1_wins

                    if min([player.score for player in game.players]) == game.players[1].score:
                        random2_wins = random2_wins + 1
                        rows[-3]['game_wins'] = random2_wins

                    if min([player.score for player in game.players]) == game.players[2].score:
                        random3_wins = random3_wins + 1
                        rows[-2]['game_wins'] = random3_wins

                    if min([player.score for player in game.players]) == game.players[3].score:
                        random4_wins = random4_wins + 1
                        rows[-1]['game_wins'] = random4_wins

                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("Random_vs_Random.csv", index=False)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', choices=['dqn', 'ismcts', 'random', 'both'], default='dqn')
    parser.add_argument('--max_score', help="Determines the max_score used for a game of Hearts", default=100, type=int)
    parser.add_argument('--iters', help="Determines the number of iterations used for ISMCTS", default=100, type=int)
    parser.add_argument('--num_games', help="Determines the number of games with the agent", default=100, type=int)
    args = parser.parse_args()
    
    if args.algo == 'dqn':
        DQN_vs_RandomAgent(num_games=args.num_games, max_score=args.max_score)
    if args.algo == 'ismcts':
        ISMCTS_vs_RandomAgent(num_games=args.num_games, iters=args.iters, max_score=args.max_score)
    if args.algo == 'random':
        RandomAgent_vs_RandomAgent(num_games=args.num_games, max_score=args.max_score)
    if args.algo == 'both':
        DQN_vs_ISMCTS(num_games=args.num_games, iters=args.iters, max_score=args.max_score)