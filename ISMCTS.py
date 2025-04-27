from math import log, sqrt
import random
from State import State


class ISMCTS:
    """
    implementation of information set MCTS
    based on https://ieeexplore.ieee.org/document/6203567 and https://www.aifactory.co.uk/newsletter/2013_01_reduce_burden.htm
    """

    class Node:
        def __init__(self, move=None, parent=None, just_moved=None):
            self.move = move  # the move that was just made
            self.parent = parent
            self.children = []
            self.wins = 0.0
            self.visits = 0
            self.avails = 1
            self.just_moved = just_moved

        def get_untried(self, legal_moves):
            tried = [c.move for c in self.children]
            return [m for m in legal_moves if m not in tried]

        def select_child(self, legal_moves, gamma=0.7):
            """selects a child according to the UCB"""
            legal = [c for c in self.children if c.move in legal_moves]
            best = max(
                legal,
                key=lambda c: c.wins / c.visits
                + gamma * sqrt(log(c.avails) / c.visits),
            )

            for c in legal:
                c.avails += 1

            return best

        def add_child(self, move, just_moved):
            """@return the newly added child"""
            c = ISMCTS.Node(move=move, parent=self, just_moved=just_moved)
            self.children.append(c)
            return c

        def update(self, terminal_state: State):
            """increases visits by 1 and updates wins according to the terminal state"""
            self.visits += 1
            if self.just_moved is not None:
                score = terminal_state.get_score(self.just_moved)
                self.wins += score

        def __repr__(self):
            return f"{self.move}: {self.wins:.4}W, {self.visits}V, {self.avails}A"

        def tree_to_str(self, indent=0):
            s = self.indent_str(indent) + str(self)
            for c in self.children:
                s += c.tree_to_str(indent + 1)
            return s

        def indent_str(self, indent):
            s = "\n"
            for _ in range(1, indent + 1):
                s += "| "
            return s

        def children_to_str(self):
            s = ""
            for c in self.children:
                s += str(c) + "\n"
            return s

    def __init__(self, player_idx):
        self.player_idx = player_idx

    def run(self, root_state: State, iters, verbose=False):
        root = ISMCTS.Node()
        for _ in range(iters):
            # print(f"starting iteration {i}")
            n = root
            s = root_state.randomize_clone(self.player_idx)

            # print("Randomized hands:")
            # for p in s.game.players:
            #    print(f"{p.name} {p.hand}")
            # print("")

            while True:
                # traverse the tree until we find a node that is not fully expanded
                moves = s.get_moves()
                if moves == []:
                    break
                untried = n.get_untried(moves)
                if untried != []:
                    break
                n = n.select_child(moves)
                s.move(n.move)

            untried = n.get_untried(s.get_moves())
            if untried != []:
                m = random.choice(untried)
                p = s.to_move
                s.move(m)
                n = n.add_child(m, p)  # create a new child and traverse to it

            # simulate playing out the rest of the hand randomly from this point:
            curr_round = s.game.round
            while s.get_moves() != [] and s.game.round == curr_round:
                # print(f"moves: {s.get_moves()}")
                # print(f"current player: {s.game.current_player.name}")
                s.move(random.choice(s.get_moves()))
            #print(f"round = {s.game.round}, curr_round = {curr_round}")
            #print(f"scores = {[p.score for p in s.game.players]}")

            while n is not None:
                n.update(s)
                n = n.parent

        if verbose:
            print(root.tree_to_str(0))
        # else:
        #     print(root.ChildrenToString())

        return max(root.children, key=lambda c: c.visits).move
