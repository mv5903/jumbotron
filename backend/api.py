import json
import os
from flask import Flask, request, jsonify, send_file
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
from threading import Thread
from werkzeug.utils import secure_filename
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

temp_filename = None

PIN = 21

ROWS = 48
COLUMNS = 64

MATRIX = None

UPDATES_PER_SECOND = 60;

SAVES_DIR = "saves"

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

thread_started = False
thread_stop_event = Event()

playback_control = {"playing": True}

STATE_FILE = "last_state.json"

def save_state(state):
    with open(STATE_FILE, 'w') as file:
        json.dump(state, file)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            return json.load(file)
    return None

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
            time.sleep(1/UPDATES_PER_SECOND) 

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
    playback_control["playing"] = False
    time.sleep(1/UPDATES_PER_SECOND)
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
        playback_control["playing"] = False
        time.sleep(1/UPDATES_PER_SECOND)
        image = Image.open(file.stream)
        matrix_representation = convert_image_to_matrix(image, brightness)
        MATRIX.update_from_matrix_array(matrix_representation)
        logger.info("Image uploaded successfully")
        save_state({'type': 'image', 'content': matrix_representation})
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
    logger.info("Saving current content to file: %s", matrixname)
    # Ensure the "saves" directory exists
    if not os.path.exists(SAVES_DIR):
        logger.info("Creating saves directory")
        os.makedirs(SAVES_DIR)

    save_data = {}
    if playback_control["playing"]:
        # Handle video
        logger.info("Video is currently playing - saving the video file")
        try:
            current_video_filepath = temp_filename
            save_data['type'] = 'video'
            save_data['content'] = current_video_filepath  # Save the path, not the file itself
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        # Handle still frame
        logger.info("Saving current matrix as a still frame")
        current_matrix_state = MATRIX.get2DArrayRepresentation()
        save_data['type'] = 'image'
        save_data['content'] = current_matrix_state

    filename = f"{matrixname}.json"
    filepath = os.path.join(SAVES_DIR, filename)
    try:
        with open(filepath, 'w') as file:
            json.dump(save_data, file)
        logger.info("Current content saved successfully")
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        logger.error(f"Error saving content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/jumbotron/get_saved_matrices')
def get_saved_matrices():
    #logger.info("Getting saved matrices")
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

    files = [f for f in os.listdir(SAVES_DIR) if os.path.isfile(os.path.join(SAVES_DIR, f)) and f.endswith(".json")]

    # Remove .json
    data = []
    for i in range(len(files)):
        data.append({
            "filename": files[i],
            "image": f"/jumbotron/get_saved_matrix_image/{files[i]}",
            #"type": "video" if json.load(open(os.path.join(SAVES_DIR, files[i]), 'r'))['type'] == 'video' else 'image'
        })

    #logger.info("Saved matrices retrieved successfully")
    return jsonify(data)

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
        
        # If the file is a video, delete the video file as well
        with open(filepath, 'r') as file:
            saved_content = json.load(file)
            if saved_content['type'] == 'video':
                video_path = saved_content['content']
                if os.path.exists(video_path):
                    os.remove(video_path)
                    logger.info("Video file deleted successfully")
                else:
                    logger.warning("Video file does not exist")
        
        os.remove(filepath)
        logger.info("Saved matrix deleted successfully")    
        return jsonify({"success": True})
    else:
        logger.warning("File does not exist")
        return jsonify({"success": False, "error": "File does not exist."})
    
@app.route('/jumbotron/activate_saved_matrix/<string:filename>', methods=['POST'])
def activate_saved_matrix(filename):
    global temp_filename  # If handling video, update the global video filename

    logger.info("Activating saved matrix: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)

    try:
        with open(filepath, 'r') as file:
            saved_content = json.load(file)

        # Check if saved_content is a dictionary
        if not isinstance(saved_content, dict):
            logger.error("Invalid content format in file: %s", filename)
            return jsonify({"success": False, "error": "Invalid content format."}), 400

        if 'type' not in saved_content or 'content' not in saved_content:
            logger.error("Missing required keys in saved content: %s", filename)
            return jsonify({"success": False, "error": "Invalid content format."}), 400
        
        playback_control["playing"] = False
        time.sleep(1/UPDATES_PER_SECOND)

        if saved_content['type'] == 'video':
            video_path = saved_content['content']
            if os.path.exists(video_path):
                # Play the video
                playback_control["playing"] = True
                temp_filename = video_path  # Update the global variable
                save_state({'type': 'video', 'filename': filename, 'brightness': 40})
        
                thread = Thread(target=video_playback_thread)
                thread.start()
            else:
                logger.error("Video file not found: %s", video_path)
                return jsonify({"success": False, "error": "Video file not found."}), 404

        elif saved_content['type'] == 'image':
            # Display the image
            MATRIX.update_from_matrix_array(saved_content['content'])
            playback_control["playing"] = False
            save_state({'type': 'image', 'content': saved_content['content']})

        logger.info("Saved content activated successfully")
        return jsonify({"success": True})

    except FileNotFoundError:
        logger.error("Saved content file not found: %s", filename)
        return jsonify({"success": False, "error": "File does not exist."}), 404
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in file: %s", filename)
        return jsonify({"success": False, "error": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error(f"Error activating saved content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

    
@app.route('/jumbotron/get_saved_matrix_image/<string:filename>')
def get_saved_matrix_image(filename):
    logger.info("Getting preview for saved content: %s", filename)
    filepath = os.path.join(SAVES_DIR, filename)

    try:
        with open(filepath, 'r') as file:
            saved_content = json.load(file)

        if saved_content['type'] == 'video':
            # Handle video file - generate a thumbnail
            video_path = saved_content['content']
            try:
                cap = cv2.VideoCapture(video_path)
                success, frame = cap.read()
                if not success:
                    logger.error("Failed to capture frame from video: %s", video_path)
                    return jsonify({"success": False, "error": "Failed to capture frame from video."}), 500
                
                # Convert the frame to an image
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                byte_io = BytesIO()
                image.save(byte_io, 'PNG')
                byte_io.seek(0)
                cap.release()
                return send_file(byte_io, mimetype='image/png')
            except Exception as e:
                logger.error("Error processing video file: %s", str(e))
                return jsonify({"success": False, "error": str(e)}), 500

        elif saved_content['type'] == 'image':
            # Handle JSON matrix file
            image = convert_matrix_to_image(saved_content['content'])
            byte_io = BytesIO()
            image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return send_file(byte_io, mimetype='image/png')
    except FileNotFoundError:
        logger.error("Content file not found: %s", filename)
        return jsonify({"success": False, "error": "File does not exist."}), 404
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in file: %s", filename)
        return jsonify({"success": False, "error": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error("Error getting saved content image: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


def video_playback_thread():
    try:
        video = cv2.VideoCapture(temp_filename)

        if not video.isOpened():
            logger.warning("Could not open video")
            return

        start_time = time.time()
        frames_processed = 0

        while playback_control["playing"]:
            ret, frame = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                start_time = time.time()
                frames_processed = 0
                continue

            expected_time = start_time + (frames_processed / UPDATES_PER_SECOND)
            current_time = time.time()
            if current_time < expected_time:
                time.sleep(expected_time - current_time)
            elif current_time > expected_time + (1 / UPDATES_PER_SECOND):
                frames_processed += 1
                continue

            # Get the current brightness setting
            current_brightness = MATRIX.getBrightness()

            # Convert the frame to an image and adjust brightness
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            matrix_representation = convert_image_to_matrix(image, current_brightness)

            # Update the matrix with the new frame
            MATRIX.update_from_matrix_array(matrix_representation)
            frames_processed += 1

        video.release()
    except Exception as e:
        logger.error("Error in video playback thread: %s", str(e))


@app.route('/jumbotron/playvideo/<int:brightness>', methods=['POST'])
def play_video(brightness):
    global temp_filename  # Keep track of the current video file name

    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({'error': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.info("No file selected for uploading")
        return jsonify({'error': 'No file selected for uploading.'}), 400

    playback_control["playing"] = False
    time.sleep(1/UPDATES_PER_SECOND)
    # Save the file in a permanent location
    filename = secure_filename(file.filename)  # Use a secure filename
    permanent_file_path = os.path.join(SAVES_DIR, filename)
    file.save(permanent_file_path)
    temp_filename = permanent_file_path  # Update the global variable

    try:
        playback_control["playing"] = True
        save_state({'type': 'video', 'filename': permanent_file_path, 'brightness': brightness})
        thread = Thread(target=video_playback_thread)
        thread.start()
        return jsonify({'success': True})
    except Exception as e:
        logger.error("Error playing video: %s", str(e))
        return jsonify({'error': 'Error playing video.'}), 500

@app.after_request
def after_request(response):
    if request.endpoint not in ['get_saved_matrices']:
        logger.info("After request -- Saving matrix state to file")
        MATRIX.save_to_file()
        logger.info("After request -- Matrix state saved to file")
    return response

if __name__ == '__main__':
    # Create empty matrix of pixels
    logger.info("Creating matrix of pixels %d x %d on pin %d", ROWS, COLUMNS, PIN)
    MATRIX = Jumbotron(ROWS, COLUMNS, PIN)
    logger.info("Matrix created successfully")
    logger.info("Loading last state")
    last_state = load_state()
    if last_state:
        if last_state['type'] == 'video':
            video_path = SAVES_DIR + "/" + last_state.get('filename')
            
            # Retrieve the content
            with open(video_path, 'r') as file:
                video_path = json.load(file)['content']
            
            if os.path.exists(video_path):
                # Play the video
                playback_control["playing"] = True
                temp_filename = video_path  # Update the global variable
                thread = Thread(target=video_playback_thread)
                thread.start()
            else:
                logger.error("Video file not found at startup: %s", video_path)
        elif last_state['type'] == 'image':
            # Display the image
            MATRIX.update_from_matrix_array(last_state['content'])
    logger.info("Last state loaded successfully")
    logger.info("Starting Jumbotron API")
    socketio.run(app, host='0.0.0.0', port=5000)
    logger.info("Jumbotron API started successfully")