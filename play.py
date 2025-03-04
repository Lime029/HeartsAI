from Player import Player
from Game import Game
import random

# Create the game with four players
game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)
print(game.play_card(game.deck.get_card('2', 'Clubs')))

while(len(game.current_player.hand) > 0):
    print(game.current_player.name)
    print(game.current_player.hand)
    print(game.trick)
    success = False
    while not success:
        try:
            print(game.play_card(random.choice(game.current_player.hand)))
            success = True
        except Exception as e:
            pass
    if len(game.trick) == 0: # End of trick
        print(game.players[0].name,game.players[0].score)
        print(game.players[1].name,game.players[1].score)
        print(game.players[2].name,game.players[2].score)
        print(game.players[3].name,game.players[3].score)

# Check if the game is over
if game.is_game_over():
    print("Game over!")