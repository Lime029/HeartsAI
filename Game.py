from Card import Card
from Deck import Deck
from Player import Player

class Game:
    def __init__(self, player_names, max_score):
        self.players = [Player(i,name) for i,name in enumerate(player_names)]
        self.max_score = max_score
        self.deck = Deck()
        self.deal_cards()
        self.trick = []
        self.hearts_broken = False
        self.current_player = self.find_starting_player()

    def deal_cards(self):
        """Deal 13 cards to each player."""
        hands = self.deck.deal()
        for player in self.players:
            player.hand = sorted(hands[player.index], key=lambda card: (Card.suits.index(card.suit), Card.ranks.index(card.rank)))

    def find_starting_player(self):
        """Find the player with the 2 of Clubs to start."""
        for player in self.players:
            for card in player.hand:
                if card.suit == "Clubs" and card.rank == "2":
                    return player
        raise ValueError("Nobody has the 2 of clubs.")

    def play_card(self, card):
        """Current player attempts to play a card."""
        if card not in self.current_player.hand:
            raise ValueError("Invalid move: You don't have that card.")

        if len(self.trick) == 0: # Starting trick with this card
            if card.suit == 'Hearts' and not self.hearts_broken and not self.current_player.has_any('Diamonds', 'Clubs', 'Spades'):
                raise ValueError("Invalid move: Hearts have not been broken.")
            trick_suit = card.suit
        else:
            trick_suit = self.trick[0][1].suit

        if card.suit != trick_suit and self.current_player.has_any(trick_suit):
            raise ValueError("Invalid move: You must follow the suit if possible.")

        self.current_player.hand.remove(card)
        self.trick.append((self.current_player.index, card))

        if card.suit == 'Hearts':
            self.hearts_broken = True

        if len(self.trick) == 4:  # Trick complete
            self.resolve_trick()
        else:
            self.current_player = self.players[(self.current_player.index + 1) % len(self.players)]
        return f"{self.current_player.name} played {card.rank} of {card.suit}."

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
        self.current_player = winner

        print(f"{winner.name} won the trick and received {points} points.")

    def is_game_over(self):
        """Check if any player has reached the max points."""
        for player in self.players:
            if player.score >= self.max_score:
                return True
        return False

    # Returns a dictionary representation of cards either of a single card or a list
    @staticmethod
    def dict_repr(obj):
        if isinstance(obj, Card):
            return {"rank": obj.rank, "suit": obj.suit}
        if isinstance(obj, list):
            return [{"rank": card.rank, "suit": card.suit} for card in obj]
        raise TypeError("Input must be a Card object or a list of Card objects.")