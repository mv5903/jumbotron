from flask import Flask, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Event
import time

from jumbotron import Jumbotron

import eventlet
eventlet.monkey_patch()

PIN=18

ROWS = 48
COLUMNS = 64

MATRIX = None

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


thread_started = False
thread_stop_event = Event()

def jumbotron_updater():
    while not thread_stop_event.is_set():
        if (MATRIX is not None):
            socketio.emit('array_update', {'data': MATRIX.get2DArrayRepresentation(), 'timestamp' : time.time_ns() }, namespace='/jumbotron')
            time.sleep(1/60.0)  # approximately 60 times per second

@socketio.on('connect', namespace='/jumbotron')
def handle_connect(*args):
    global thread_started
    print('Client connected')

    # Start the array updater thread only if it hasn't been started
    if not thread_started:
        socketio.start_background_task(jumbotron_updater)
        thread_started = True

@app.route('/jumbotron')
def discover():
    return {
        "isAlive": True,
        "rows": ROWS,
        "columns": COLUMNS,
    }

@app.route('/jumbotron/pixel/<int:row>/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updatePixel(row, column, r, g, b, brightness):
    MATRIX.updatePixel(row, column, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/row/<int:row>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateRow(row, r, g, b, brightness):
    MATRIX.updateRow(row, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/column/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateColumn(column, r, g, b, brightness):
    MATRIX.updateColumn(column, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/all/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateAll(r, g, b, brightness):
    MATRIX.updateAll(r, g, b, brightness)
    return {
        "success": True
    }

# Implement at a later time
@app.route('/jumbotron/playvideo/<string:video>')
def playVideo(video):
    return make_response("Service Temporarily Unavailable", 503)

if __name__ == '__main__':
    # Create empty matrix of pixels
    MATRIX = Jumbotron(ROWS, COLUMNS, PIN)
    socketio.run(app, host='127.0.0.1', port=5000)