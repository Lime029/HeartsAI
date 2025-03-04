from Player import Player
from Game import Game
from State import State
from ISMCTS import ISMCTS
import random

# Create the game with four players
# game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)

# Deal with looping through rounds outside of the Game class
# print(game.play_card(game.deck.get_card("2", "Clubs")))

# Check if the game is over
# if game.is_game_over():
#    print("Game over!")

random.seed(0)

game = Game(["A", "B", "C", "D"], 100)
# A will be the MCTS agent

while not game.is_game_over():
    p = game.current_player
    if p.name == "A":
        s = State(game)
        move = ISMCTS.run(s, 1000, verbose=True)
    else:
        # non-MCTS players just play randomly
        if len(game.trick) == 0:
            # player is leading, can play anything except possibly hearts
            if game.hearts_broken or all(c.suit == "Hearts" for c in p.hand):
                move = random.choice(p.hand)
            else:
                move = random.choice([c for c in p.hand if c.suit != "Hearts"])
        else:
            lead = game.trick[0][1].suit
            move = random.choice(p.playable_cards(lead))

    print(game.play_card(move))
