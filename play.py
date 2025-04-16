from Game import Game
from State import State
from ISMCTS import ISMCTS

num_hands = 10
mcts_scores = []
random_scores = [[] for _ in range(3)]
mcts_idx = 0

for i in range(num_hands):
    print(f"---------------------------------------Running hand {i}/{num_hands}...--------------------------------------")

    # Create a new game for each hand
    game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)
    mcts = ISMCTS(mcts_idx)

    while not game.is_game_over() and game.current_player.hand != []:
        p = game.current_player
        if p.index == mcts_idx:
            s = State(game)
            move = mcts.run(s, 100, verbose=False)
        else:
            move = game.random_legal_move()
        game.play_card(move)

    # Store scores at the end of the hand
    for p in game.players:
        if p.index == mcts_idx:
            mcts_scores.append(p.round_score)
        else:
            random_scores[p.index if p.index < mcts_idx else p.index - 1].append(p.round_score)

# Compute average scores
print("\nSimulation Results:")
print(f"MCTS average score: {sum(mcts_scores)/len(mcts_scores):.2f}")
for i, scores in enumerate(random_scores):
    print(f"Random player {i + 1} average score: {sum(scores)/len(mcts_scores):.2f}")

"""
# Create the game with four players
game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)

print("Starting hands:")
for p in game.players:
    print(f"{p.name} {p.hand}")
print("")

mcts_idx = 0
print(f"MCTS is {game.players[mcts_idx].name}\n")
mcts = ISMCTS(mcts_idx)

while not game.is_game_over() and game.current_player.hand != []:
    p = game.current_player
    if p.index == mcts_idx:
        s = State(game)
        print("running MCTS")
        move = mcts.run(s, 999, verbose=False)
        print(f"MCTS picked {move}")
    else:
        move = game.random_legal_move()
    game.play_card(move)

print("Hand is over. Scores:")
for p in game.players:
    print(f"{p.name}: {p.round_score}")
print("")
"""
