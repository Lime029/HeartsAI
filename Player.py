from Card import Card

class Player:
    def __init__(self, index, name):
        self.name = name
        self.index = index
        self.hand = []
        self.score = 0
    
    def has_any(self, *suits):
        """Returns True if the player has at least one card of the given suit(s), otherwise False."""
        return any(card.suit in suits for card in self.hand)