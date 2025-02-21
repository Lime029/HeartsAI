from Card import Card

class Player:
    def __init__(self, index, name):
        self.name = name
        self.index = index
        self.hand = []
        self.score = 0

    def receive_card(self, card):
        if isinstance(card, Card):
            self.hand.append(card)
            self.hand = sorted(self.hand, key=lambda card: (Card.suits.index(card.suit), Card.ranks.index(card.rank)))
            print(self.hand)
        else:
            print("Error: The provided card must be an instance of the Card class.")

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return card
        return None
    
    def has_any(self, *suits):
        """Returns True if the player has at least one card of the given suit(s), otherwise False."""
        return any(card.suit in suits for card in self.hand)