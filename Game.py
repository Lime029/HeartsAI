from Card import Card
from Deck import Deck
from Player import Player

class HeartsGame:
    def __init__(self, player_names, max_score):
        self.players = [Player(i,name) for i,name in enumerate(player_names)]
        self.max_score = max_score
        self.deck = Deck()
        self.deal_cards()
        self.trick = []
        self.hearts_broken = False
        self.current_player_index = self.find_starting_player()

    def deal_cards(self):
        """Deal 13 cards to each player."""
        hands = self.deck.deal()
        for player in self.players:
            player.receive_cards(hands[player.index])

    def find_starting_player(self):
        """Find the player with the 2 of Clubs to start."""
        for player in self.players:
            for card in player.hand:
                if card.suit == "Clubs" and card.rank == "2":
                    return player
        return None  # Fallback in case something goes wrong

    def play_card(self, player_index, card):
        """Player attempts to play a card."""
        player = self.players[player_index]

        if card not in player.hand:
            raise ValueError("Invalid move: You don't have that card.")

        if len(self.trick) == 0: # Starting trick with this card
            if card.suit == 'Hearts' and not self.hearts_broken and not player.has_any('Diamonds', 'Clubs', 'Spades'):
                raise ValueError("Invalid move: Hearts have not been broken.")
            trick_suit = card.suit
        else:
            trick_suit = self.trick[0][1].suit

        if card.suit != trick_suit and player.has_any(trick_suit):
            raise ValueError("Invalid move: You must follow the suit if possible.")

        player.play_card(card)
        self.trick.append((player_index, card))

        if card.suit == 'Hearts':
            self.hearts_broken = True

        if len(self.trick) == 4:  # Trick complete
            self.resolve_trick()

        return f"{player.name} played {card.rank} of {card.suit}."

    def resolve_trick(self):
        """Determine who wins the trick and assign points."""
        lead_suit = self.trick[0][1].suit
        trick_cards = [(p, c) for p, c in self.trick if c.suit == lead_suit]
        winner = max(trick_cards, key=lambda x: Card.ranks.index(x[1].rank))[0]

        # Calculate points
        points = sum(1 for _, c in self.trick if c.suit == 'Hearts')
        points += 13 if Card("Spades", "Q") in [c for _, c in self.trick] else 0

        winner.score += points
        self.trick = []

        print(f"{winner.name} won the trick and received {points} points.")

    def is_game_over(self):
        """Check if any player has reached the max points."""
        for player in self.players:
            if player.score >= self.max_score:
                return True
        return False