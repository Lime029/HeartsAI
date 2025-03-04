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
    emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": Game.dict_repr(game.trick)})

@socketio.on('play_card')
def play_card(card):
    """Move a played card from player cards to the center."""
    global game
    if card in game.current_player.hand:
        game.play_card(card)
        emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": Game.dict_repr(game.trick)}, broadcast=True)

@socketio.on('get_new_cards')
def get_new_cards():
    """Generates a new game."""
    global game
    game = Game(["Rachel", "Meal", "Shraf", "Simi"], 100)
    emit('update_cards', {"player_cards": Game.dict_repr(game.current_player.hand), "center_cards": Game.dict_repr(game.trick)}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
