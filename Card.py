class Card:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = self.set_value(rank)  # We assign a numerical value to each card for gameplay purposes

    def set_value(self, rank):
        # Assign values to each card rank (for a simple card game)
        if rank == 'J':
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        elif rank == 'A':
            return 14
        else:
            return int(rank)  # 2-10 have their own numerical value

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
    def dict_repr(self):
        return {"rank": self.rank, "suit": self.suit}