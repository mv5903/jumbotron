import json
import os
from flask import Flask, make_response, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Event
import time
import eventlet
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from PIL import Image

from jumbotron import Jumbotron

# Log format
log_format = "%(asctime)s - %(levelname)s - %(message)s"

# Create a logger
logger = logging.getLogger("Jumbotron")
logger.setLevel(logging.INFO)

# Create a timed rotating file handler that rotates logs every midnight
handler = TimedRotatingFileHandler("jumbotron.log", when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter(log_format))

# Add the file handler to the logger
logger.addHandler(handler)

# Create a stream handler to print log messages to stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(log_format))

# Add the stream handler to the logger
logger.addHandler(stream_handler)

eventlet.monkey_patch()

PIN = 21

ROWS = 48
COLUMNS = 64

MATRIX = None

UPDATES_PER_SECOND = 5;

SAVES_DIR = "saves"

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

thread_started = False
thread_stop_event = Event()

def convert_image_to_matrix(image, brightness=100):
    # Resize image to match Jumbotron resolution
    image = image.resize((COLUMNS, ROWS))
    
    # Convert image to RGB
    image = image.convert("RGB")

    matrix = []
    for row in range(ROWS):
        matrix_row = []
        for column in range(COLUMNS):
            r, g, b = image.getpixel((column, row))
            matrix_row.append({'r': r, 'g': g, 'b': b, 'brightness': brightness})  # Assuming full brightness
        matrix.append(matrix_row)

    return matrix


def jumbotron_updater():
    while not thread_stop_event.is_set():
        if (MATRIX is not None):
            socketio.emit('array_update', {'data': MATRIX.get2DArrayRepresentation(), 'timestamp' : time.time_ns() }, namespace='/jumbotron')
            time.sleep(1/UPDATES_PER_SECOND)  # approximately 60 times per second

@socketio.on('connect', namespace='/jumbotron')
def handle_connect(*args):
    global thread_started
    logger.info("Client connected to Jumbotron API")

    # Start the array updater thread only if it hasn't been started
    if not thread_started:
        logger.info("Starting jumbotron emitting updater thread")
        socketio.start_background_task(jumbotron_updater)
        thread_started = True

@app.route('/jumbotron')
def discover():
    logger.info("Client discovered Jumbotron API")
    return {
        "isAlive": True,
        "rows": ROWS,
        "columns": COLUMNS,
    }

@app.route('/jumbotron/pixel/<int:row>/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updatePixel(row, column, r, g, b, brightness):
    logger.info("Updating pixel at row: %d, column: %d to r: %d, g: %d, b: %d, brightness: %d", row, column, r, g, b, brightness)
    MATRIX.updatePixel(row, column, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/row/<int:row>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateRow(row, r, g, b, brightness):
    logger.info("Updating row: %d to r: %d, g: %d, b: %d, brightness: %d", row, r, g, b, brightness)
    MATRIX.updateRow(row, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/column/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateColumn(column, r, g, b, brightness):
    logger.info("Updating column: %d to r: %d, g: %d, b: %d, brightness: %d", column, r, g, b, brightness)
    MATRIX.updateColumn(column, r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/all/<int:r>/<int:g>/<int:b>/<int:brightness>')
def updateAll(r, g, b, brightness):
    logger.info("Updating all pixels to r: %d, g: %d, b: %d, brightness: %d", r, g, b, brightness)
    MATRIX.updateAll(r, g, b, brightness)
    return {
        "success": True
    }

@app.route('/jumbotron/reset')
def reset():
    logger.info("Resetting all pixels to r: 0, g: 0, b: 0, brightness: 0")
    MATRIX.reset()
    return {
        "success": True
    }


@app.route('/jumbotron/upload/<int:brightness>', methods=['POST'])
def upload_image(brightness):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading.'}), 400

    if file:
        image = Image.open(file.stream)
        matrix_representation = convert_image_to_matrix(image, brightness)
        MATRIX.update_from_matrix_array(matrix_representation)
        # Optional: Store or use this matrix representation as needed.
        return jsonify(matrix_representation)
    
@app.route('/jumbotron/save_current_matrix', methods=['POST'])
def save_current_matrix():
    # Ensure the "saves" directory exists
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

    # Generate a unique filename based on timestamp
    filename = f"{int(time.time())}.json"
    filepath = os.path.join(SAVES_DIR, filename)

    with open(filepath, 'w') as file:
        json.dump(MATRIX.get2DArrayRepresentation(), file)

    return jsonify({"success": True, "filename": filename})

@app.route('/jumbotron/get_saved_matrices')
def get_saved_matrices():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

    files = [f for f in os.listdir(SAVES_DIR) if os.path.isfile(os.path.join(SAVES_DIR, f))]
    return jsonify(files)

@app.route('/jumbotron/play_saved_matrix/<string:filename>')
def play_saved_matrix(filename):
    filepath = os.path.join(SAVES_DIR, filename)

    with open(filepath, 'r') as file:
        saved_matrix = json.load(file)

    MATRIX.update_from_matrix_array(saved_matrix)
    
    return jsonify({"success": True})


# Implement at a later time
@app.route('/jumbotron/playvideo/<string:video>')
def playVideo(video):
    logger.info("Playing video: %s [Service Temporarily Unavailable - Not Implemented Yet]", video)
    return make_response("Service Temporarily Unavailable - Not Implemented Yet", 503)

@app.after_request
def after_request(response):
    logger.info("After request -- Saving matrix state to file")
    MATRIX.save_to_file()
    logger.info("After request -- Matrix state saved to file")
    return response

if __name__ == '__main__':
    # Create empty matrix of pixels
    logger.info("Creating matrix of pixels %d x %d on pin %d", ROWS, COLUMNS, PIN)
    MATRIX = Jumbotron(ROWS, COLUMNS, PIN)
    logger.info("Matrix created successfully")
    logger.info("Starting Jumbotron API")
    socketio.run(app, host='0.0.0.0', port=5000)
    logger.info("Jumbotron API started successfully")