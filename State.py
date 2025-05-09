from copy import deepcopy
import random
from Game import Game
from Card import Card


class State:
    """A class representing the game state, for MCTS. Normally, this would be an abstract class, but we only have one game."""

    def __init__(self, game: Game):
        self.game = deepcopy(game)  # maybe don't need to copy
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
        self.game.passed_cards = True #if we resolved the trick before, this may have been set to false by mistake (hacky fix though)
        self.game.play_card(move)
        self.to_move = self.game.current_player.index

    def get_moves(self):
        """@return legal moves for the current player"""
        p = self.game.players[self.to_move]
        if len(self.game.trick) == 0:
            if Card("Clubs", "2") in p.hand:
                return [p.hand[p.hand.index(Card("Clubs", "2"))]]
            # p is leading; can play anything except possibly hearts
            elif self.game.hearts_broken or not p.has_any(
                "Clubs", "Diamonds", "Spades"
            ):
                return p.hand  # can play anything
            else:
                return [c for c in p.hand if c.suit != "Hearts"]
        else:
            lead = self.game.trick[0][1].suit
            if p.has_any(lead):
                return [c for c in p.hand if c.suit == lead]
            else:
                return p.hand

    def get_score(self, player):
        """@return the score from the perspective of the player, normalized between 0 and 1, where 1 is the best, or 0 if the game is not over"""
        # print(f"game score for player is {self.game.players[player].score}")
        #return 1 - self.game.players[player].score / 100.0
        #print(f"scores: {[p.score for p in self.game.players]}")
        smin = min([p.score for p in self.game.players])
        smax = max([p.score for p in self.game.players])
        if smin == smax:
            return 0.5
        s = self.game.players[player].score
        return 1 - (s - smin)/(smax - smin)
