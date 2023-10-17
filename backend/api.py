from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Thread, Event
import time

from jumbotron import Jumbotron

ROWS = 48
COLUMNS = 64

MATRIX = [];

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

thread = Thread()
thread_stop_event = Event()

def jumbotron_updater():
    while not thread_stop_event.isSet():
        socketio.emit('array_update', {'data': MATRIX.get2DArrayRepresentation(), 'timestamp' : time.time_ns() }, namespace='/jumbotron')
        time.sleep(1/60.0)  # approximately 60 times per second

@socketio.on('connect', namespace='/jumbotron')
def handle_connect():
    global thread
    print('Client connected')

    # Start the array updater thread only if it's not alive
    if not thread.is_alive():
        thread = socketio.start_background_task(jumbotron_updater)

@app.route('/jumbotron')
def discover():
    return {
        "isAlive": True,
        "rows": ROWS,
        "columns": COLUMNS,
    }

if __name__ == '__main__':
    # Create empty matrix of pixels
    MATRIX = Jumbotron(ROWS, COLUMNS)
    app.run(debug=True, host='0.0.0.0')
    socketio.run(app, host='127.0.0.1', port=5000)