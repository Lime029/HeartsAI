from Game import Game
from Card import Card
from State import State
from ISMCTS import ISMCTS
from model import DQN
import pandas as pd
import random
import numpy as np
from tqdm import tqdm 
class Random_Player():
    def __init__(self, game: Game):
        self.__game = game

    def run(self):
        return self.__game.random_legal_move()
    
class ISMCTS_Player():
    def __init__(self, player_idx, game: Game, iters, verbose=False):
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


def ISMCTS_vs_RandomAgent(num_games=10):
    """
    Run 1000 simulations of the game and save them in a dataframe.
    """

    rows = []
    ismcts_wins = 0
    ismcts_rwins = 0
    random_wins = 0
    random_rwins = 0
    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["Rachel", "Meal", "Shraf", "Simi"], max_score=26, verbose=False)

        # Evaluate ISMCTS against random agents
        ismcts_player = ISMCTS_Player(player_idx=0, game=game, iters=100);
        random_player = Random_Player(game)
        players = [ismcts_player, random_player, random_player, random_player]
        last_round = 0
        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                player_round_score = round_scores[0]
                random_player_round_score = round_scores[1]
                round_scores = sorted(round_scores, reverse=True)
                # If the player won this round, increment the number of rounds wons
                if round_scores[-1] == player_round_score:
                    ismcts_rwins = ismcts_rwins + 1
                if round_scores[-1] == random_player_round_score:
                    random_rwins = random_rwins + 1
                rows.append({"player": "ISMCTS", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": player_round_score, "placement": round_scores.index(player_round_score), "round_wins": ismcts_rwins, "game_wins": ismcts_wins, "last_trick": False})
                rows.append({"player": "Random", "game": i, "round": game.round, "current_score": game.players[1].score, "round_score": random_player_round_score, "placement": round_scores.index(random_player_round_score), "round_wins": random_rwins, "game_wins": random_wins, "last_trick": False})
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-1]['last_trick'] = True
                    rows[-2]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        ismcts_wins = ismcts_wins + 1
                        rows[-2]['game_wins'] = ismcts_wins
                    elif min([player.score for player in game.players]) == game.players[1].score:
                        random_wins = random_wins + 1
                        rows[-1]['game_wins'] = random_wins

                
                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("ISMCTS_vs_Random1.csv", index=False)
    return df

def RandomAgent_vs_RandomAgent(num_games=10):
    rows = []
    random_wins = 0
    random_rwins = 0
    # Run 1000 games
    for i in tqdm(range(num_games)):
        game = Game(["Rachel", "Meal", "Shraf", "Simi"], max_score=26, verbose=False)

        # Evaluate random against random agents for a baseline
        random_player = Random_Player(game)
        players = [random_player, random_player, random_player, random_player]
        last_round = 0
        while not game.is_game_over():
            move = players[game.current_player.index].run()
            round_scores = game.play_card(move)
            
            if(round_scores is not None):    # A new trick just started
                random_player_round_score = round_scores[0]
                round_scores = sorted(round_scores, reverse=True)

                # If the player won this round, increment the number of rounds wons
                if round_scores[-1] == random_rwins:
                    random_rwins = random_rwins + 1
                rows.append({"player": "Random", "game": i, "round": game.round, "current_score": game.players[0].score, "round_score": random_player_round_score, "placement": round_scores.index(random_player_round_score), "round_wins": random_rwins, "game_wins": random_wins, "last_trick": False})
                if last_round == game.round:
                    # Correct last_trick for final game score if round was unfinished
                    rows[-1]['last_trick'] = True
                    if min([player.score for player in game.players]) == game.players[0].score:
                        random_wins = random_wins + 1
                        rows[-1]['game_wins'] = random_wins
                
                last_round = game.round

    df = pd.DataFrame(rows)
    df.to_csv("Random_vs_Random.csv", index=True)
    return df

if __name__ == "__main__":
    ISMCTS_vs_RandomAgent(10)

        # Average number of tricks agent does before game end
        # Average round_score

        # Average game score

        # Average placement

        # Average number of wins

        # Average number of round wins

        # Graph of point values vs current round in the game


        # MCTS with different number of iterations for MC

        # Maybe add graph of point value at current trick in the game