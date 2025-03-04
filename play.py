from Player import Player
from Game import Game
import random

# Create the game with four players
game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)

random.seed(0)

while not game.is_game_over():
    p = game.current_player
    if len(game.trick) == 0:
        # player is leading, can play anything except possibly hearts
        if game.hearts_broken or all(c.suit == "hearts" for c in p.hand):
            move = random.choice(p.hand)
        else:
            move = random.choice([c for c in p.hand if c.suit != "hearts"])
    else:
        lead = game.trick[0][1].suit
        if p.has_any(lead):
            move = random.choice([c for c in p.hand if c.suit == lead])
        else:
            move = random.choice(p.hand)

    print(game.play_card(move))
