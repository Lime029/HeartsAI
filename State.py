from copy import deepcopy
import random


class State:
    """A class representing the game state, for MCTS. Normally, this would be an abstract class, but we only have one game."""

    def __init__(self, game):
        self.game = deepcopy(game) #maybe don't need to copy
        self.game.verbose = False
        self.n_players = 4  # assuming 4 players for now
        self.to_move = game.current_player.index

    def clone(self):
        cl = State(deepcopy(self.game))
        cl.to_move = self.to_move
        return cl

    def randomize_clone(self, observer):
        """@return a determinization of the current state. all information not visible to observer is randomized"""
        cl = self.clone()
        # need to randomize the other players' hands
        obs_hand = cl.game.players[observer].hand
        # TODO: replace this with a call to a Game method, which should keep track of cards that have been played in previous tricks
        unseen = [
            c
            for c in cl.game.deck.cards
            if c not in obs_hand and c not in [card for (_, card) in cl.game.trick]
        ]
        random.shuffle(unseen)

        for p in cl.game.players:
            if p.index != observer:
                sz = len(p.hand)
                p.hand = unseen[:sz]
                unseen = unseen[sz:]
        return cl

    def move(self, move):
        self.game.play_card(move)
        self.to_move = self.game.current_player.index

    def get_moves(self):
        """@return legal moves for the current player"""
        p = self.game.players[self.to_move]
        if len(self.game.trick) == 0:
            # p is leading; can play anything except possibly hearts
            if self.game.hearts_broken or not p.has_any("Clubs", "Diamonds", "Spades"):
                return p.hand  # can play anything
            else:
                # TODO: replace with a method call in Player.py
                return [c for c in p.hand if c.suit != "Hearts"]
        else:
            lead = self.game.trick[0][1].suit
            if p.has_any(lead):
                # TODO: replace with a method call
                return [c for c in p.hand if c.suit == lead]
            else:
                return p.hand

    def get_score(self, player):
        """@return the score from the perspective of the player, normalized between 0 and 1, where 1 is the best, or 0 if the game is not over"""
        #print(f"game score for player is {self.game.score[player]}")
        return 1 - self.game.players[player].score / 26.0
