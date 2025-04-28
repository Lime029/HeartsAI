from Game import Game
from State import State
from ISMCTS import ISMCTS
import random

num_hands = 100
mcts_scores = []
random_scores = [[] for _ in range(3)]
heur_idx = 0
mcts_runs = 0

random.seed(200)
hand_seeds = [random.randint(1,2**32 - 1) for _ in range(num_hands)]

for i in range(num_hands):
    print(f"---------------------------------------Running hand {i}/{num_hands}...--------------------------------------")

    # Create a new game for each hand
    random.seed(hand_seeds[i])
    game = Game(["Player 1", "Player 2", "Player 3", "Player 4"], 100)
    mcts = ISMCTS(heur_idx)
    curr_round = game.round

    while not game.is_game_over() and game.current_player.hand != [] and game.round == curr_round:
        if not game.passed_cards:
            for pi in game.players:
                if pi.index == heur_idx:
                    to_pass = game.get_heur_pass_cards(pi.index)
                else:
                    to_pass = game.get_random_pass_cards(pi.index)
                game.pass_player_cards(pi.index, to_pass)
        p = game.current_player
        mcts.player_idx = p.index
        s = State(game)
        #print(f"running mcts. hand size = {len(game.current_player.hand)}. player = {game.current_player.name}")
        move = mcts.run(s, 100, verbose=False)
        mcts_runs += 1
        game.play_card(move)

    # Store scores at the end of the hand
    for p in game.players:
        if p.index == heur_idx:
            mcts_scores.append(p.score)
        else:
            random_scores[p.index if p.index < heur_idx else p.index - 1].append(p.score)
print(f"runs = {mcts_runs}")

# Compute average scores
print("\nSimulation Results:")
print(f"MCTS average score: {sum(mcts_scores)/len(mcts_scores):.2f}")
for i, scores in enumerate(random_scores):
    print(f"Random player {i + 1} average score: {sum(scores)/len(mcts_scores):.2f}")
