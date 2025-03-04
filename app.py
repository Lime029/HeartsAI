from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from Player import Player
from Game import Game
from Card import Card

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def send_initial_cards():
    """Send player cards and center cards on connection."""
    trick_cards = [Game.dict_repr(trick[1]) for trick in game.trick]
    emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": trick_cards})

@socketio.on('play_card')
def play_card(card):
    """Move a played card from player cards to the center."""
    global game
    card = game.deck.get_card(card['rank'], card['suit'])
    print(card)
    print(game.current_player.hand)
    if card in game.current_player.hand:
        game.play_card(card)
        trick_cards = [Game.dict_repr(trick[1]) for trick in game.trick]
        emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": trick_cards}, broadcast=True)

@socketio.on('get_new_cards')
def get_new_cards():
    """Generates a new game."""
    global game
    game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)
    trick_cards = [Game.dict_repr(trick[1]) for trick in game.trick]
    emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": trick_cards}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
