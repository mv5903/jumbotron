# pip imports
import json
import os
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from threading import Event
import time
import eventlet
from PIL import Image
from io import BytesIO
import cv2
from threading import Thread
from werkzeug.utils import secure_filename
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# local imports
from utils.jumbotron import Jumbotron
from utils.config import Config

try:
    # Setup
    #eventlet.spawn()
    temp_filename = None
    thread_started = False
    thread_stop_event = Event()
    video_is_playing = True
    app = Flask(__name__)
    CORS(app)
    sockets = Sockets(app)
    clients = set()

    # region Helper Methods
    def save_state(state):
        with open(Config.STATE_FILE, 'w') as file:
            json.dump(state, file)

    def load_state():
        if os.path.exists(Config.STATE_FILE):
            with open(Config.STATE_FILE, 'r') as file:
                return json.load(file)
        return None

    def convert_matrix_to_image(matrix):
        image = Image.new("RGB", (Config.COLUMNS, Config.ROWS))
        for row in range(Config.ROWS):
            for column in range(Config.COLUMNS):
                pixel = matrix[row][column]
                r, g, b = pixel['r'], pixel['g'], pixel['b']
                image.putpixel((column, row), (r, g, b))
        return image

    def jumbotron_updater():
        while not thread_stop_event.is_set():
            if (Config.MATRIX is not None):
                for ws in clients.copy():
                    try:
                        message = json.dumps({
                            'data': Config.MATRIX.get2DArrayRepresentation(),
                            'timestamp': time.time_ns()
                        })
                        ws.send(message)
                    except Exception as e:
                        clients.remove(ws)  # Remove disconnected client
                time.sleep(1/Config.UPDATES_PER_SECOND) 
                
    def video_playback_thread():
        try:
            video = cv2.VideoCapture(temp_filename)

            if not video.isOpened():
                Config.LOGGER.warning("Could not open video")
                return

            start_time = time.time()
            frames_processed = 0

            while video_is_playing:
                ret, frame = video.read()
                if not ret:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    start_time = time.time()
                    frames_processed = 0
                    continue

                expected_time = start_time + (frames_processed / Config.UPDATES_PER_SECOND)
                current_time = time.time()
                if current_time < expected_time:
                    time.sleep(expected_time - current_time)
                elif current_time > expected_time + (1 / Config.UPDATES_PER_SECOND):
                    frames_processed += 1
                    continue

                # Get the current brightness setting
                current_brightness = Config.MATRIX.getBrightness()

                # Convert the frame to an image and adjust brightness
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                matrix_representation = Jumbotron.convert_image_to_matrix(image, current_brightness)

                # Update the matrix with the new frame
                Config.MATRIX.update_from_matrix_array(matrix_representation)
                frames_processed += 1

            video.release()
        except Exception as e:
            Config.LOGGER.error("Error in video playback thread: %s", str(e))
            
    # endregion

    # region API Endpoints
    @sockets.route('/jumbotron')
    def handle_jumbotron_socket(ws):
        global thread_started
        client_ip = request.remote_addr
        print(f"Client connected from {client_ip}")

        clients.add(ws)
        
        # Start the updater thread once
        if not thread_started:
            threading.Thread(target=jumbotron_updater).start()
            thread_started = True

        while not ws.closed:
            message = ws.receive()
            if message:
                print(f"Received message from {client_ip}: {message}")

        clients.remove(ws)
        print(f"Client disconnected from {client_ip}")
        
    @app.route('/')
    def hello():
        return 'Hello World!'

    @app.route('/jumbotron', methods=['GET'])
    def discover():
        Config.LOGGER.info("Client discovered Jumbotron API")
        return {
            "isAlive": True,
            "rows": Config.ROWS,
            "columns": Config.COLUMNS,
        }

    @app.route('/jumbotron/pixel/<int:row>/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
    def updatePixel(row, column, r, g, b, brightness):
        Config.LOGGER.info("Updating pixel at row: %d, column: %d to r: %d, g: %d, b: %d, brightness: %d", row, column, r, g, b, brightness)
        Config.MATRIX.updatePixel(row, column, r, g, b, brightness)
        return {
            "success": True
        }

    @app.route('/jumbotron/row/<int:row>/<int:r>/<int:g>/<int:b>/<int:brightness>')
    def updateRow(row, r, g, b, brightness):
        Config.LOGGER.info("Updating row: %d to r: %d, g: %d, b: %d, brightness: %d", row, r, g, b, brightness)
        Config.MATRIX.updateRow(row, r, g, b, brightness)
        return {
            "success": True
        }

    @app.route('/jumbotron/column/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>')
    def updateColumn(column, r, g, b, brightness):
        Config.LOGGER.info("Updating column: %d to r: %d, g: %d, b: %d, brightness: %d", column, r, g, b, brightness)
        Config.MATRIX.updateColumn(column, r, g, b, brightness)
        return {
            "success": True
        }

    @app.route('/jumbotron/all/<int:r>/<int:g>/<int:b>/<int:brightness>')
    def updateAll(r, g, b, brightness):
        Config.LOGGER.info("Updating all pixels to r: %d, g: %d, b: %d, brightness: %d", r, g, b, brightness)
        Config.MATRIX.updateAll(r, g, b, brightness)
        return {
            "success": True
        }

    @app.route('/jumbotron/reset')
    def reset():
        Config.LOGGER.info("Resetting all pixels to r: 0, g: 0, b: 0, brightness: 0")
        video_is_playing = False
        time.sleep(1/Config.UPDATES_PER_SECOND)
        Config.MATRIX.reset()
        return {
            "success": True
        }


    @app.route('/jumbotron/upload/<int:brightness>', methods=['POST'])
    def upload_image(brightness):
        Config.LOGGER.info("Uploading image")
        if 'file' not in request.files:
            Config.LOGGER.warning("No file part in the request")
            return jsonify({'error': 'No file part in the request.'}), 400

        file = request.files['file']
        if file.filename == '':
            Config.LOGGER.info("No file selected for uploading")
            return jsonify({'error': 'No file selected for uploading.'}), 400

        if file:
            video_is_playing = False
            time.sleep(1/Config.UPDATES_PER_SECOND)
            image = Image.open(file.stream)
            matrix_representation = Jumbotron.convert_image_to_matrix(image, brightness)
            Config.MATRIX.update_from_matrix_array(matrix_representation)
            Config.LOGGER.info("Image uploaded successfully")
            save_state({'type': 'image', 'content': matrix_representation})
            return jsonify(matrix_representation)
        
    @app.route('/jumbotron/brightness/<int:brightness>', methods=['POST'])
    def brightness(brightness):
        Config.LOGGER.info("Updating brightness to %d", brightness)
        Config.MATRIX.updateBrightness(brightness)
        return jsonify({"success": True})

    @app.route('/jumbotron/brightness')
    def get_brightness():
        Config.LOGGER.info("Getting brightness")
        brightness = Config.MATRIX.getBrightness()
        return jsonify({"brightness": brightness})

    @app.route('/jumbotron/save_current_matrix/<string:matrixname>', methods=['POST'])
    def save_current_matrix(matrixname):
        Config.LOGGER.info("Saving current content to file: %s", matrixname)
        # Ensure the "saves" directory exists
        if not os.path.exists(Config.SAVES_DIR):
            Config.LOGGER.info("Creating saves directory")
            os.makedirs(Config.SAVES_DIR)

        save_data = {}
        if video_is_playing:
            # Handle video
            Config.LOGGER.info("Video is currently playing - saving the video file")
            try:
                current_video_filepath = temp_filename
                save_data['type'] = 'video'
                save_data['content'] = current_video_filepath  # Save the path, not the file itself
            except Exception as e:
                Config.LOGGER.error(f"Error saving video: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500
        else:
            # Handle still frame
            Config.LOGGER.info("Saving current matrix as a still frame")
            current_matrix_state = Config.MATRIX.get2DArrayRepresentation()
            save_data['type'] = 'image'
            save_data['content'] = current_matrix_state

        filename = f"{matrixname}.json"
        filepath = os.path.join(Config.SAVES_DIR, filename)
        try:
            with open(filepath, 'w') as file:
                json.dump(save_data, file)
            Config.LOGGER.info("Current content saved successfully")
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            Config.LOGGER.error(f"Error saving content: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500



    @app.route('/jumbotron/get_saved_matrices')
    def get_saved_matrices():
        Config.LOGGER.info("Getting saved matrices")
        if not os.path.exists(Config.SAVES_DIR):
            os.makedirs(Config.SAVES_DIR)

        files = [f for f in os.listdir(Config.SAVES_DIR) if os.path.isfile(os.path.join(Config.SAVES_DIR, f)) and f.endswith(".json")]

        # Remove .json
        data = []
        for i in range(len(files)):
            data.append({
                "filename": files[i],
                "image": f"/jumbotron/get_saved_matrix_image/{files[i]}"
            })

        Config.LOGGER.info("Saved matrices retrieved successfully")
        return jsonify(data)

    @app.route('/jumbotron/play_saved_matrix/<string:filename>')
    def play_saved_matrix(filename):
        Config.LOGGER.info("Playing saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        with open(filepath, 'r') as file:
            saved_matrix = json.load(file)

        Config.MATRIX.update_from_matrix_array(saved_matrix)
        
        Config.LOGGER.info("Saved matrix played successfully")
        return jsonify({"success": True})

    @app.route('/jumbotron/delete_saved_matrix/<string:filename>', methods=['DELETE'])
    def delete_saved_matrix(filename):
        Config.LOGGER.info("Deleting saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        if os.path.exists(filepath):
            
            # If the file is a video, delete the video file as well
            with open(filepath, 'r') as file:
                saved_content = json.load(file)
                if saved_content['type'] == 'video':
                    video_path = saved_content['content']
                    if os.path.exists(video_path):
                        os.remove(video_path)
                        Config.LOGGER.info("Video file deleted successfully")
                    else:
                        Config.LOGGER.warning("Video file does not exist")
            
            os.remove(filepath)
            Config.LOGGER.info("Saved matrix deleted successfully")    
            return jsonify({"success": True})
        else:
            Config.LOGGER.warning("File does not exist")
            return jsonify({"success": False, "error": "File does not exist."})
        
    @app.route('/jumbotron/activate_saved_matrix/<string:filename>', methods=['POST'])
    def activate_saved_matrix(filename):
        global temp_filename  # If handling video, update the global video filename

        Config.LOGGER.info("Activating saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        try:
            with open(filepath, 'r') as file:
                saved_content = json.load(file)

            # Check if saved_content is a dictionary
            if not isinstance(saved_content, dict):
                Config.LOGGER.error("Invalid content format in file: %s", filename)
                return jsonify({"success": False, "error": "Invalid content format."}), 400

            if 'type' not in saved_content or 'content' not in saved_content:
                Config.LOGGER.error("Missing required keys in saved content: %s", filename)
                return jsonify({"success": False, "error": "Invalid content format."}), 400
            
            video_is_playing = False
            time.sleep(1/Config.UPDATES_PER_SECOND)

            if saved_content['type'] == 'video':
                video_path = saved_content['content']
                if os.path.exists(video_path):
                    # Play the video
                    video_is_playing = True
                    temp_filename = video_path  # Update the global variable
                    save_state({'type': 'video', 'filename': filename, 'brightness': 40})
            
                    thread = Thread(target=video_playback_thread)
                    thread.start()
                else:
                    Config.LOGGER.error("Video file not found: %s", video_path)
                    return jsonify({"success": False, "error": "Video file not found."}), 404

            elif saved_content['type'] == 'image':
                # Display the image
                Config.MATRIX.update_from_matrix_array(saved_content['content'])
                video_is_playing = False
                save_state({'type': 'image', 'content': saved_content['content']})

            Config.LOGGER.info("Saved content activated successfully")
            return jsonify({"success": True})

        except FileNotFoundError:
            Config.LOGGER.error("Saved content file not found: %s", filename)
            return jsonify({"success": False, "error": "File does not exist."}), 404
        except json.JSONDecodeError:
            Config.LOGGER.error("Invalid JSON format in file: %s", filename)
            return jsonify({"success": False, "error": "Invalid JSON format."}), 400
        except Exception as e:
            Config.LOGGER.error(f"Error activating saved content: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

        
    @app.route('/jumbotron/get_saved_matrix_image/<string:filename>')
    def get_saved_matrix_image(filename):
        Config.LOGGER.info("Getting preview for saved content: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

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
                        Config.LOGGER.error("Failed to capture frame from video: %s", video_path)
                        return jsonify({"success": False, "error": "Failed to capture frame from video."}), 500
                    
                    # Convert the frame to an image
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    byte_io = BytesIO()
                    image.save(byte_io, 'PNG')
                    byte_io.seek(0)
                    cap.release()
                    return send_file(byte_io, mimetype='image/png')
                except Exception as e:
                    Config.LOGGER.error("Error processing video file: %s", str(e))
                    return jsonify({"success": False, "error": str(e)}), 500

            elif saved_content['type'] == 'image':
                # Handle JSON matrix file
                image = convert_matrix_to_image(saved_content['content'])
                byte_io = BytesIO()
                image.save(byte_io, 'PNG')
                byte_io.seek(0)
                return send_file(byte_io, mimetype='image/png')
        except FileNotFoundError:
            Config.LOGGER.error("Content file not found: %s", filename)
            return jsonify({"success": False, "error": "File does not exist."}), 404
        except json.JSONDecodeError:
            Config.LOGGER.error("Invalid JSON format in file: %s", filename)
            return jsonify({"success": False, "error": "Invalid JSON format."}), 400
        except Exception as e:
            Config.LOGGER.error("Error getting saved content image: %s", str(e))
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/jumbotron/playvideo/<int:brightness>', methods=['POST'])
    def play_video(brightness):
        global temp_filename  # Keep track of the current video file name

        if 'file' not in request.files:
            Config.LOGGER.warning("No file part in the request")
            return jsonify({'error': 'No file part in the request.'}), 400

        file = request.files['file']
        if file.filename == '':
            Config.LOGGER.info("No file selected for uploading")
            return jsonify({'error': 'No file selected for uploading.'}), 400

        video_is_playing = False
        time.sleep(1/Config.UPDATES_PER_SECOND)
        # Save the file in a permanent location
        filename = secure_filename(file.filename)  # Use a secure filename
        permanent_file_path = os.path.join(Config.SAVES_DIR, filename)
        file.save(permanent_file_path)
        temp_filename = permanent_file_path  # Update the global variable

        try:
            video_is_playing = True
            save_state({'type': 'video', 'filename': permanent_file_path, 'brightness': brightness})
            thread = Thread(target=video_playback_thread)
            thread.start()
            return jsonify({'success': True})
        except Exception as e:
            Config.LOGGER.error("Error playing video: %s", str(e))
            return jsonify({'error': 'Error playing video.'}), 500
        
    # endregion

    # region Specials
    @app.after_request
    def after_request(response):
        if request.endpoint not in ['get_saved_matrices']:
            Config.LOGGER.info("After request -- Saving matrix state to file")
            Config.MATRIX.save_to_file()
            Config.LOGGER.info("After request -- Matrix state saved to file")
        return response

    # endregion

    if __name__ == '__main__':
        # Create empty matrix of pixels
        Config.LOGGER.info("Creating matrix of pixels %d x %d on GPIO PIN %d", Config.ROWS, Config.COLUMNS, Config.PIN)
        Config.MATRIX = Jumbotron(Config.ROWS, Config.COLUMNS, Config.PIN)
        Config.LOGGER.info("Matrix created successfully")
        Config.LOGGER.info("Loading last state")
        last_state = load_state()
        if last_state:
            if last_state['type'] == 'video':
                video_path = Config.SAVES_DIR + "/" + last_state.get('filename')
                
                # Retrieve the content
                with open(video_path, 'r') as file:
                    video_path = json.load(file)['content']
                
                if os.path.exists(video_path):
                    # Play the video
                    video_is_playing = True
                    temp_filename = video_path  # Update the global variable
                    thread = Thread(target=video_playback_thread)
                    thread.start()
                else:
                    Config.LOGGER.error("Video file not found at startup: %s", video_path)
            elif last_state['type'] == 'image':
                # Display the image
                Config.MATRIX.update_from_matrix_array(last_state['content'])
        Config.LOGGER.info("Last state loaded successfully")
        Config.LOGGER.info("Starting Jumbotron API")
        server = pywsgi.WSGIServer(('0.0.0.0', Config.PORT), app, handler_class=WebSocketHandler)
        Config.LOGGER.info("Jumbotron API started successfully")
        server.serve_forever()

except KeyboardInterrupt as e:
    Config.LOGGER.info("Keyboard interrupt received")
    thread_stop_event.set()
    Config.LOGGER.info("Stopping Jumbotron API")
    server.stop()
    Config.LOGGER.info("Jumbotron API stopped successfully")
    Config.LOGGER.info("Exiting")
    exit(0)