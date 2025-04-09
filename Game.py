from Card import Card
from Deck import Deck
from Player import Player
import random

class Game:
    def __init__(self, player_names, max_score, verbose=False, jack_diamonds=True):
        self.players = [Player(i,name) for i,name in enumerate(player_names)]
        self.max_score = max_score
        self.verbose = verbose
        self.jack_diamonds = jack_diamonds
        self.round = 0
        self.new_round()

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
    
    def new_round(self):
        """Deals out a new hand and starts play again."""
        for p in self.players:
            p.round_score = 0
            p.shooting_moon = True
        
        self.deck = Deck()
        self.deal_cards()
        self.trick = [] # Caution: A list of pairs (playerIndex, card)
        self.hearts_broken = False
        self.current_player = self.find_starting_player()

    def resolve_round(self):
        # Set proper scores
        shot_moon = any(p.shooting_moon for p in self.players)
        for p in self.players:
            p.score += p.round_score
        if shot_moon:
            for p in self.players:
                # +26 for everyone who didn't shoot, 0 at most for shooter
                if p.round_score <= 0:
                    p.score += 26
                else: # This is the shooter
                    p.score -= 26
        
        if self.verbose:
            print(f"Round {self.round} ended.")
            for p in self.players:
                print(f"{p.name} now has {p.score} points.")
        
        if not self.is_game_over():
            self.round += 1
            self.new_round()
        elif self.verbose:
            print(f"Game ended because someone got {self.max_score} points.")

    def play_card(self, card):
        """Current player attempts to play a card."""
        if not self.is_valid_card(card):
            raise ValueError("Invalid card played.")

        self.current_player.hand.remove(card)
        self.trick.append((self.current_player.index, card))

        if card.suit == 'Hearts':
            self.hearts_broken = True

        if self.verbose:
            print(f"{self.current_player.name} played {card.rank} of {card.suit}.")

        if len(self.trick) == 4:  # Trick complete
            self.resolve_trick()
        else:
            self.current_player = self.players[(self.current_player.index + 1) % len(self.players)]

    def is_valid_card(self, card) -> bool:
        if card not in self.current_player.hand:
            return False

        if len(self.trick) == 0: # Starting trick with this card
            if card.suit == 'Hearts' and not self.hearts_broken and self.current_player.has_any('Diamonds', 'Clubs', 'Spades'):
                return False
            trick_suit = card.suit
        else:
            trick_suit = self.trick[0][1].suit

        if card.suit != trick_suit and self.current_player.has_any(trick_suit):
            return False

        return True

    def resolve_trick(self):
        """Determine who wins the trick and assign points."""
        lead_suit = self.trick[0][1].suit
        trick_cards = [(p, c) for p, c in self.trick if c.suit == lead_suit]
        winner = self.players[max(trick_cards, key=lambda x: Card.ranks.index(x[1].rank))[0]]

        # Calculate points
        points = sum(1 for _, c in self.trick if c.suit == 'Hearts')
        points += 13 if Card("Spades", "Q") in [c for _, c in self.trick] else 0
        if points > 0:
            # No other player besides winner can now shoot the moon
            for p in self.players:
                if p.index != winner.index:
                    p.shooting_moon = False
        if self.jack_diamonds: # Not required to shoot moon
            points -= 10 if Card("Diamonds", "J") in [c for _, c in self.trick] else 0

        winner.round_score += points
        self.trick = []
        self.current_player = winner

        if self.verbose:
            print(f"{winner.name} won the trick and received {points} points.")
        
        if len(self.current_player.hand) == 0:
            self.resolve_round()

    def is_game_over(self):
        """Check if any player has reached the max points."""
        for player in self.players:
            if player.score >= self.max_score:
                return True
        return False

    def random_legal_move(self):
        p = self.current_player
        if len(self.trick) == 0:
            # player is leading, can play anything except possibly hearts
            if self.hearts_broken or all(c.suit == "Hearts" for c in p.hand):
                move = random.choice(p.hand)
            else:
                move = random.choice([c for c in p.hand if c.suit != "Hearts"])
        else:
            lead = self.trick[0][1].suit
            move = random.choice(p.playable_cards(lead))
        return move

    # Returns a dictionary representation of cards either of a single card or a list
    @staticmethod
    def dict_repr(obj):
        if isinstance(obj, Card):
            return {"rank": obj.rank, "suit": obj.suit}
        if isinstance(obj, list):
            return [{"rank": card.rank, "suit": card.suit} for card in obj]
        raise TypeError("Input must be a Card object or a list of Card objects.")
