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
        self.main_player = self.players[0]
        self.banner = "Welcome to Hearts AI"

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
        self.passed_cards = not self.should_pass() # = true if cards have already been passed (or they don't need to be)
        self.cards_to_pass = [[] for _ in self.players] #l[i] = list of cards that player i will pass
        self.current_player = self.find_starting_player()

    def resolve_round(self):
        # Set proper scores
        shot_moon = any(p.shooting_moon for p in self.players)
        # Save round scores to return for analysis
        round_scores = [player.round_score for player in self.players]
        
        for p in self.players:
            p.score += p.round_score
        if shot_moon:
            if self.verbose:
                print(f"Player {self.current_player.index} shot the moon")
            for p in self.players:
                # +26 for everyone who didn't shoot, 0 at most for shooter
                round_scores.append(p.round_score)
                if p.round_score <= 0:
                    p.score += 26
                    round_scores[-1] += 26
                else: # This is the shooter
                    p.score -= 26
                    round_scores[-1] -= 26
        
        if self.verbose:
            print(f"Round {self.round} ended.")
            for p in self.players:
                print(f"{p.name} now has {p.score} points.")
        
        if not self.is_game_over():
            if self.verbose:
                print("Round scores", round_scores)
            self.round += 1
            self.new_round()
        elif self.verbose:
            print(f"Game ended because someone got {self.max_score} points.")
        return round_scores

    def play_card(self, card):
        """Current player attempts to play a card."""
        if not self.is_valid_card(card):
            raise ValueError("Invalid card played.")
        if not self.passed_cards:
            print("Warning: playing card before cards have been passed.")

        self.current_player.hand.remove(card)
        self.trick.append((self.current_player.index, card))

        if card.suit == 'Hearts':
            self.hearts_broken = True

        if self.verbose:
            print(f"{self.current_player.name} played {card.rank} of {card.suit}.")

        if len(self.trick) == 4:  # Trick complete
            return self.resolve_trick()
        else:
            self.current_player = self.players[(self.current_player.index + 1) % len(self.players)]

    def is_valid_card(self, card) -> bool:
        if card not in self.current_player.hand:
            return False

        if len(self.trick) == 0: # Starting trick with this card
            if len(self.current_player.hand) == 13: # Starting the round (must be 2 of clubs)
                if not (card.suit == 'Clubs' and card.rank == '2'):
                    return False
            elif card.suit == 'Hearts' and not self.hearts_broken and self.current_player.has_any('Diamonds', 'Clubs', 'Spades'):
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
            self.banner = f"{winner.name} won the trick!"
            print(f"Trick winner: {winner.name}\t Points: {points}")
            print("Current scores", [player.round_score for player in self.players])
        if len(self.current_player.hand) == 0:
            return self.resolve_round()

    def is_game_over(self):
        """Check if any player has reached the max points."""
        for player in self.players:
            if player.score >= self.max_score:
                return True
        return False

    def random_legal_move(self):
        p = self.current_player
        if len(self.trick) == 0:
            if Card("Clubs", "2") in p.hand:
                move = p.hand[p.hand.index(Card('Clubs', '2'))]
            # player is leading, can play anything except possibly hearts
            elif self.hearts_broken or all(c.suit == "Hearts" for c in p.hand):
                move = random.choice(p.hand)
            else:
                move = random.choice([c for c in p.hand if c.suit != "Hearts"])
        else:
            lead = self.trick[0][1].suit
            move = random.choice(p.playable_cards(lead))
        return move

    def should_pass(self):
        #returns true if we need to pass cards this round
        return self.round % 4 != 3

    def pass_player_cards(self, idx, cards):
        if self.cards_to_pass[idx] != []:
            raise ValueError(f"Player {idx} has already passed cards")
        if len(cards) != 3:
            raise ValueError(f"Received only {len(cards)} cards to pass")
        if self.round % 4 == 3:
            raise ValueError("Attempted to pass cards on a round where no cards are passed")
        self.cards_to_pass[idx] = cards
        if all(self.cards_to_pass[p.index] != [] for p in self.players):
            self.do_pass_cards()

    def pass_recipient(self, idx):
        if self.round % 4 == 0:
            recipient = (idx - 1) % 4
        elif self.round % 4 == 1:
            recipient = (idx + 2) % 4
        elif self.round % 4 == 2:
            recipient = (idx + 1) % 4
        else:
            recipient = idx
        return recipient

    def do_pass_cards(self):
        #once each player has submitted their cards to pass, we actually do the passing
        for p in self.players:
            idx = p.index
            recipient = self.pass_recipient(idx)
            if recipient == idx:
                raise ValueError("Attempted to pass cards on round where cards are not passed")
            self.pass_from_to(idx, recipient, self.cards_to_pass[idx])
        for p in self.players:
            p.hand = sorted(p.hand, key=lambda card: (Card.suits.index(card.suit), Card.ranks.index(card.rank)))
        self.passed_cards = True
        self.current_player = self.find_starting_player()

    def pass_from_to(self, src, dst, cards):
        sender = self.players[src]
        receiver = self.players[dst]
        for c in cards:
            if c not in sender.hand:
                raise ValueError("Attempted to pass a card not in hand (in pass_from_to)")
            sender.hand.remove(c)
        receiver.hand.extend(cards)
        if self.verbose:
            print(f"{sender.name} gave {cards} to {receiver.name}")

    def get_random_pass_cards(self, idx):
        #gets a list of 3 randomly chosen cards from player idx's hand
        return random.sample(self.players[idx].hand, 3)

    def get_heur_pass_cards(self, idx):
        #gets 3 cards from player idx's hand according to weighting heuristic
        #this function has a lot of "magic numbers" that could instead be tunable parameters
        hand = self.players[idx].hand
        weights = [0 for _ in hand]
        suit_count = {s: sum(c.suit == s for c in hand) for s in ['Hearts', 'Diamonds', 'Clubs', 'Spades']}

        for i, c in enumerate(hand):
            if c.suit == 'Spades':
                if c.rank == 'Q':
                    weight = 100
                elif c.rank == 'A':
                    weight = 80
                elif c.rank == 'K':
                    weight = 70
                elif c.rank == 'J':
                    weight = 40
                elif c.rank == '10':
                    weight = 20
                else:
                    weight = 10
            elif c.suit == 'Hearts':
                weight = 2 * c.value #probably replace 2 with some tunable param
            else:
                #saying that there's no base advantage to throwing away an off-suit. could be different
                weight = 0

            #give a bonus if we are shorting an off-suit (or nearly so)
            if c.suit in ['Clubs', 'Diamonds']:
                if suit_count[c.suit] == 1:
                    weight += 20
                elif suit_count[c.suit] == 2:
                    weight += 10

            weights[i] = weight

        #then take the 3 highest-weight cards
        sorted_weights = sorted(zip(hand, weights), key = lambda x: x[1])
        return [c for c, _ in sorted_weights[:3]]


    # Returns a dictionary representation of cards either of a single card or a list
    @staticmethod
    def dict_repr(obj):
        if isinstance(obj, Card):
            return {"rank": obj.rank, "suit": obj.suit}
        if isinstance(obj, list):
            return [{"rank": card.rank, "suit": card.suit} for card in obj]
        raise TypeError("Input must be a Card object or a list of Card objects.")
