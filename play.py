from Player import Player
from Game import Game


# Create players
player1 = Player("Rachel")
player2 = Player("Meal")
player3 = Player("Shraf")
player4 = Player("Simi")

# Initialize the game
game = Game([player1, player2, player3, player4])

# Start the game
game.start_game()
