from Player import Player
from Game import Game


# Create players
player1 = Player("Rachel")
player2 = Player("Meal")
player3 = Player("Shraf")
player4 = Player("Simi")

# Create the game with four players
game = Game(["Rachel", "Meal", "Shraf", "Simi"])

# Deal with looping through rounds outside of the Game class
p1 = game.find_starting_player
print(game.play_card(p1, game.deck.get_card('2', 'Clubs')))

# Check if the game is over
if game.is_game_over():
    print("Game over!")