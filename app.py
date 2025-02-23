from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def generate_random_cards(num=10):
    deck = [{"rank": rank, "suit": suit} for suit in suits for rank in ranks]
    return random.sample(deck, num)

player_cards = generate_random_cards(10)  # 10 cards for the player
center_cards = []  # Starts empty, updates as cards are played

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def send_initial_cards():
    """Send player cards and center cards on connection."""
    emit('update_cards', {"player_cards": player_cards, "center_cards": center_cards})

@socketio.on('play_card')
def play_card(card):
    """Move a played card from player cards to the center."""
    global player_cards, center_cards
    if card in player_cards:
        player_cards.remove(card)
        center_cards.append(card)
        emit('update_cards', {"player_cards": player_cards, "center_cards": center_cards}, broadcast=True)

@socketio.on('get_new_cards')
def get_new_cards():
    """Generates 10 new random cards for the player."""
    global player_cards
    player_cards = generate_random_cards(10)
    emit('update_cards', {"player_cards": player_cards, "center_cards": center_cards}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
