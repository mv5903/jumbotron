import json
import os
import tempfile
from flask import Flask, make_response, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO
from threading import Event
import time
import eventlet
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from PIL import Image
from io import BytesIO
import cv2

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

UPDATES_PER_SECOND = 30;

SAVES_DIR = "saves"

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

thread_started = False
thread_stop_event = Event()

def convert_image_to_matrix(image, brightness=40):
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

def convert_matrix_to_image(matrix):
    image = Image.new("RGB", (COLUMNS, ROWS))
    for row in range(ROWS):
        for column in range(COLUMNS):
            pixel = matrix[row][column]
            r, g, b = pixel['r'], pixel['g'], pixel['b']
            image.putpixel((column, row), (r, g, b))
    return image


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
    logger.info("Uploading image")
    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.info("No file selected for uploading")
        return jsonify({'error': 'No file selected for uploading.'}), 400

    if file:
        image = Image.open(file.stream)
        matrix_representation = convert_image_to_matrix(image, brightness)
        MATRIX.update_from_matrix_array(matrix_representation)
        logger.info("Image uploaded successfully")
        return jsonify(matrix_representation)
    
@app.route('/jumbotron/brightness/<int:brightness>', methods=['POST'])
def brightness(brightness):
    logger.info("Updating brightness to %d", brightness)
    MATRIX.updateBrightness(brightness)
    return jsonify({"success": True})

@app.route('/jumbotron/brightness')
def get_brightness():
    logger.info("Getting brightness")
    brightness = MATRIX.getBrightness()
    return jsonify({"brightness": brightness})

@app.route('/jumbotron/save_current_matrix/<string:matrixname>', methods=['POST'])
def save_current_matrix(matrixname):
    logger.info("Saving current matrix to file: %s", matrixname)
    # Ensure the "saves" directory exists
    if not os.path.exists(SAVES_DIR):
        logger.info("Creating saves directory")
        os.makedirs(SAVES_DIR)

    filename = f"{matrixname}.json"
    filepath = os.path.join(SAVES_DIR, filename)

    with open(filepath, 'w') as file:
        json.dump(MATRIX.get2DArrayRepresentation(), file)

    logger.info("Current matrix saved successfully")
    return jsonify({"success": True, "filename": filename})

@app.route('/jumbotron/get_saved_matrices')
def get_saved_matrices():
    logger.info("Getting saved matrices")
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

    files = [f for f in os.listdir(SAVES_DIR) if os.path.isfile(os.path.join(SAVES_DIR, f))]
    logger.info("Saved matrices retrieved successfully")
    return jsonify(files)

@app.route('/jumbotron/play_saved_matrix/<string:filename>')
def play_saved_matrix(filename):
    logger.info("Playing saved matrix: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)

    with open(filepath, 'r') as file:
        saved_matrix = json.load(file)

    MATRIX.update_from_matrix_array(saved_matrix)
    
    logger.info("Saved matrix played successfully")
    return jsonify({"success": True})

@app.route('/jumbotron/delete_saved_matrix/<string:filename>', methods=['DELETE'])
def delete_saved_matrix(filename):
    logger.info("Deleting saved matrix: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info("Saved matrix deleted successfully")    
        return jsonify({"success": True})
    else:
        logger.warning("File does not exist")
        return jsonify({"success": False, "error": "File does not exist."})
    
@app.route('/jumbotron/activate_saved_matrix/<string:filename>', methods=['POST'])
def activate_saved_matrix(filename):
    # Load the saved matrix JSON file
    logger.info("Activating saved matrix: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)
    # Load saved matrix onto the Jumbotron
    try:
        with open(filepath, 'r') as file:
            saved_matrix = json.load(file)
    except FileNotFoundError:
        logger.error("Matrix file not found: %s", filename)
        return jsonify({"success": False, "error": "File does not exist."}), 404
    
    MATRIX.update_from_matrix_array(saved_matrix)
    logger.info("Saved matrix activated successfully")
    return jsonify({"success": True})
    
@app.route('/jumbotron/get_saved_matrix_image/<string:filename>')
def get_saved_matrix_image(filename):
    logger.info("Getting image preview for saved matrix: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)

    # Load the saved matrix JSON file
    try:
        with open(filepath, 'r') as file:
            saved_matrix = json.load(file)
    except FileNotFoundError:
        logger.error("Matrix file not found: %s", filename)
        return jsonify({"success": False, "error": "File does not exist."}), 404

    # Convert the saved matrix to an image
    image = convert_matrix_to_image(saved_matrix)

    # Convert image to bytes and send as response
    byte_io = BytesIO()
    image.save(byte_io, "PNG")
    byte_io.seek(0)
    return send_file(byte_io, mimetype="image/png")

@app.route('/jumbotron/playvideo/<int:brightness>', methods=['POST'])
def play_video(brightness):
    logger.info("Playing video")
    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.info("No file selected for uploading")
        return jsonify({'error': 'No file selected for uploading.'}), 400
    
    # Create a temporary file to store the uploaded video
    temp_fd, temp_filename = tempfile.mkstemp()
    try:
        # Save the uploaded video file
        file.save(temp_filename)
        
        # Load video using OpenCV
        video = cv2.VideoCapture(temp_filename)
        if not video.isOpened():
            logger.warning("Could not open video")
            return jsonify({'error': 'Could not open video.'}), 400
        
        start_time = time.time()
        frames_processed = 0
        
        while True:
            # Read a frame from the video
            ret, frame = video.read()
            if not ret:
                # Break the loop if we've reached the end of the video
                break
            
            # Calculate the expected time for this frame
            expected_time = start_time + (frames_processed / UPDATES_PER_SECOND)
            
            # Check if we're ahead or behind the expected time
            current_time = time.time()
            if current_time < expected_time:
                # If ahead, sleep for the remaining duration
                time.sleep(expected_time - current_time)
            elif current_time > expected_time + (1 / UPDATES_PER_SECOND):
                # If behind, skip this frame
                frames_processed += 1
                continue
            
            # Convert the frame to an image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Convert the image to the matrix representation
            matrix_representation = convert_image_to_matrix(image)
            
            # Update the LED matrix
            MATRIX.update_from_matrix_array(matrix_representation)
            
            frames_processed += 1
        
        logger.info("Video played successfully")
        return jsonify({'success': True})
    except Exception as e:
        logger.error("Error playing video: %s", str(e))
        return jsonify({'error': 'Error playing video.'}), 500
    finally:
        # Release video capture and remove the temporary file
        video.release()
        os.close(temp_fd)
        os.remove(temp_filename)

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