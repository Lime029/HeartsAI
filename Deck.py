import random
import Card

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]
        random.shuffle(self.cards)

    def deal(self, num_players=4):
        """deal 13 cards to each player."""
        return [self.cards[i::num_players] for i in range(num_players)]
