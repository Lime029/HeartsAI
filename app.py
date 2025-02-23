from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  

# Define possible suits and ranks
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

@app.route('/')
def index():
    return render_template('index.html')

# Simulated game loop sending cards
def game_loop():
    game_state = []  
    while True:
        time.sleep(2)  # Every 2 seconds, send a new card
        new_card = {"rank": random.choice(ranks), "suit": random.choice(suits)}
        game_state.append(new_card)
        socketio.emit('update', game_state)

threading.Thread(target=game_loop, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
