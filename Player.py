import Card

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0

    def receive_cards(self, cards):
        self.hand = sorted(cards, key=lambda card: (Card.suits.index(card.suit), Card.ranks.index(card.rank)))
        print(self.hand)

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return card
        return None
    

    