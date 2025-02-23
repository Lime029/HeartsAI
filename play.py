from Player import Player
from Game import Game

# Create the game with four players
game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)

# Deal with looping through rounds outside of the Game class
print(game.play_card(game.deck.get_card('2', 'Clubs')))

# Check if the game is over
if game.is_game_over():
    print("Game over!")