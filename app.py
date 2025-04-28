from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from threading import Timer
import random

from Player import Player
from Game import Game
from Card import Card
from ISMCTS import ISMCTS
from State import State 
from DQ_Agent import *
from get_metrics import DQN_Player

debug = False

print("Creating Flask app...")
app = Flask(__name__)

print("Initializing SocketIO...")
socketio = SocketIO(app, cors_allowed_origins="*")

print("Creating initial game state...")
player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
ai_candidates = player_names[1:]  # ["Player 2", "Player 3", "Player 4"]

# Randomly assign AI candidates to MCTS, DQ, random
mcts_player = random.choice(ai_candidates)
ai_candidates.remove(mcts_player)
dq_player = random.choice(ai_candidates)
ai_candidates.remove(dq_player)
random_player = ai_candidates[0]

mcts_players = [mcts_player]
dq_players = [dq_player]
random_players = [random_player]

game = Game(player_names, 100)

def emit_game_state(trick_cards = [Game.dict_repr(trick[1]) for trick in game.trick]):
    """Emit the current game state to all clients."""
    print("Emitting game state...")
    print(trick_cards)

    player_scores = [{"name": player.name, "score": player.score} for player in game.players]

    is_main_player = game.current_player == game.main_player

    if debug:
        display = Game.dict_repr(game.current_player.hand)
    else:
        display = Game.dict_repr(game.main_player.hand)

    if game.passed_cards:
        emit('update_cards', {
            "display_cards": display,
            "player_cards": Game.dict_repr(game.current_player.hand),
            "center_cards": trick_cards,
            "player_name": game.current_player.name,
            "player_score": game.current_player.score,
            "is_main_player": is_main_player,
            "banner": game.banner,
            "player_scores": player_scores,
            "mcts_players": mcts_players,
            "dq_players": dq_players,
            "need_to_pass": not game.passed_cards,
            "pass_target": game.players[game.pass_recipient(game.current_player.index)].name

        }, broadcast=True)
    else:
        print(f"hand: {game.main_player.hand}")
        emit('update_cards', {
            "display_cards": Game.dict_repr(game.main_player.hand),
            "player_cards": Game.dict_repr(game.main_player.hand),
            "center_cards": [],
            "player_name": game.main_player.name,
            "player_score": game.main_player.score,
            "is_main_player": True,
            "banner": game.banner,
            "player_scores": player_scores,
            "mcts_players": mcts_players,
            "dq_players": dq_players,
            "need_to_pass": not game.passed_cards,
            "pass_target": game.players[game.pass_recipient(game.main_player.index)].name
        }, broadcast=True)
        emit('pass_cards', {
            "target_player": game.players[game.pass_recipient(game.main_player.index)].name
        })

@app.route('/')
def index():
    print("Serving index.html...")
    return render_template('index.html')

@socketio.on('connect')
def send_initial_cards():
    """Send player cards and center cards on connection."""
    print("Client connected!")
    emit_game_state()

@socketio.on('play_card')
def play_card(card):
    """Move a played card from player cards to the center."""
    global game
    print(f"Received card to play: {card}")
    card = game.deck.get_card(card['rank'], card['suit'])
    print(f"Converted card object: {card}")
    print(f"Current player hand before play: {game.current_player.hand}")
    if card in game.current_player.hand:
        trick_cards = [Game.dict_repr(trick[1]) for trick in game.trick]
        game.play_card(card)
        trick_cards.append(Game.dict_repr(card))
        print("Card played successfully.")
        emit_game_state(trick_cards)
    else:
        print("Card not found in current player hand.")

@socketio.on('get_new_cards')
def get_new_cards():
    """Generates a new game."""
    global game
    print("Received request to start new game.")
    game = Game(["Player 1", "Player 2", "Player 3", "Player 4"], 100)
    emit_game_state()

@socketio.on('run_mcts')
def run_mcts():
    global game
    print("Running ISMCTS...")
    mcts = ISMCTS(game.current_player.index)
    s = State(game)
    move = mcts.run(s, 1000, verbose=False)
    print(f"ISMCTS chose move: {move}")
    play_card(Game.dict_repr(move))

@socketio.on('run_dq')
def run_dq():
    global game
    print("Running DQ...")
    dqn = DQN_Player(game)
    move = dqn.run()
    print(f"DQ chose move: {move}")
    play_card(Game.dict_repr(move))

@socketio.on('run_random')
def run_dq():
    global game
    print("Running Random...")
    move = game.random_legal_move()
    print(f"Random chose move: {move}")
    play_card(Game.dict_repr(move))

@socketio.on('run_pass')
def run_pass(data):
    global game
    # Extract data from the emitted payload
    passed_cards_by_player = data['cards']  # Cards being passed
    from_player = game.main_player.index  # Name of the player who is passing cards
    print(f"From player: {from_player}")

    # Find the from_player and to_player based on their names

    unicode_to_suit = {
    '♥': 'Hearts',
    '♣': 'Clubs',
    '♦': 'Diamonds',
    '♠': 'Spades'
    }
    
    cards_to_pass = []
    for card in passed_cards_by_player:
        rank, unicode_suit = card  # Unpack the inner list
        suit = unicode_to_suit[unicode_suit]  # Convert to full name
        card_obj = game.deck.get_card(rank, suit)
        print(f"Converted card object: {card_obj}")
        cards_to_pass.append(card_obj)
    game.pass_player_cards(from_player, cards_to_pass)

    for p in game.players:
        if p != game.main_player:
            game.pass_player_cards(p.index, game.get_random_pass_cards(p.index))

    emit_game_state()

if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
