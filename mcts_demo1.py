from Game import Game
from ISMCTS import ISMCTS
from State import State
game = Game(["Player 1", "Player 2", "Player 3", "Player 4"], 100)

print("starting hands:")
for p in game.players:
    print(f"{p.name} {p.hand}")
print("")

mcts_idx = 0
print(f"mcts is {game.players[mcts_idx].name}\n")
mcts = ISMCTS(mcts_idx)

while not game.is_game_over() and game.current_player.hand != []:
    p = game.current_player
    if p.index == mcts_idx:
        s = State(game)
        print("running mcts")
        move = mcts.run(s, 999, verbose=False)
        print(f"mcts picked {move}")
    else:
        move = game.random_legal_move()
    game.play_card(move)

print("hand is over. scores:")
for p in game.players:
    print(f"{p.name}: {p.score}")
print("")
