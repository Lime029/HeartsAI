from Player import Player
from Deck import Deck

class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.round = 1

    def deal_cards(self):
        # Deal 13 cards to each player
        for _ in range(13):
            for player in self.players:
                card = self.deck.deal()
                player.receive_cards(card)

    def show_hands(self):
        for player in self.players:
            print(player)

    def play_round(self):
        # Each player plays a card
        print(f"\nRound {self.round}:")
        for player in self.players:
            print(f"\n{player.name}'s turn:")
            card = player.play_card()
            print(f"{player.name} played: {card}")

        self.round += 1

    def start_game(self):
        self.deal_cards()
        self.show_hands()
        
        # Play 3 rounds for demo purposes
        for _ in range(3):
            self.play_round()

